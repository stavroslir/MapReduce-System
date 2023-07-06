from flask import Flask, request, jsonify
from database import db, Job, Worker, init_app
import grpc
import worker_pb2
import worker_pb2_grpc
import base64
import threading
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
stub_dict = {}

class Dispatcher:
    def __init__(self, app):
        self.thread = threading.Thread(target=self.run)
        self.event = threading.Event()
        self.app = app

    def start(self):
        self.thread.start()

    def run(self):
        while True:
            self.event.wait()
            self.dispatch_jobs()
            self.check_worker_status()  # add this function call here
            self.event.clear()

    def trigger_dispatch(self):
        self.event.set()

    def dispatch_jobs(self):
        with self.app.app_context():
            for job in Job.query.filter_by(status='submitted').all():
                for worker in Worker.query.filter_by(status='IDLE').all():
                    stub = stub_dict[worker.id]
                    task = worker_pb2.Task()
                    task.job_id = job.id
                    task.task_type = job.task_type
                    task.input_path = job.input_path
                    task.output_path = job.output_path
                    task.function_name = job.function_name  
                    task.function_code = job.function_code
                    response = stub.AssignTask(task)
                    if response.status == worker_pb2.Status.WorkerStatus.ACCEPTED:
                        job.status = 'running'
                        worker.status = 'BUSY'
                        db.session.commit()
                    break

    def check_worker_status(self): 
        with self.app.app_context():
            for worker in Worker.query.filter_by(status='BUSY').all():
                stub = stub_dict[worker.id]
                try:
                    response = stub.GetStatus(worker_pb2.Empty())
                    if response.status == worker_pb2.Status.WorkerStatus.IDLE:
                        worker.status = 'IDLE'
                        db.session.commit()
                except grpc.RpcError as e:
                    print(f"GetStatus RPC failed for worker {worker.id}. Error: {str(e)}")

dispatcher_thread = Dispatcher(app)
dispatcher_thread.start()

@app.route('/job', methods=['POST'])
def submit_job():
    data = request.get_json()
    function_code = base64.b64decode(data['function_file']).decode('utf-8')
    new_job = Job(status='submitted', user_id=data['user_id'], 
                  description=data['job_description'], task_type=data['task_type'], 
                  input_path=data['input_path'], output_path=data['output_path'], 
                  function_name=data['function_name'], function_code=function_code)
    db.session.add(new_job)
    db.session.commit()
    dispatcher_thread.trigger_dispatch()
    return jsonify({'message': 'New job created!', 'job_id': new_job.id})

@app.route('/register', methods=['POST'])
def register_worker():
    data = request.get_json()
    new_worker = Worker(address=data['address'], status='IDLE')
    db.session.add(new_worker)
    db.session.commit()
    stub = worker_pb2_grpc.WorkerStub(grpc.insecure_channel(new_worker.address))
    stub_dict[new_worker.id] = stub
    dispatcher_thread.trigger_dispatch()
    return jsonify({'message':'New worker registered!', 'worker_id': new_worker.id})

@app.route('/deregister', methods=['POST'])
def deregister_worker():
    data = request.get_json()
    worker = Worker.query.get(data['worker_id'])
    db.session.delete(worker)
    db.session.commit()
    del stub_dict[worker.id]
    dispatcher_thread.trigger_dispatch()
    return jsonify({'message': 'Worker deregistered!'})

@app.route('/workers', methods=['GET'])
def view_workers():
    workers = Worker.query.all()
    return jsonify([{'worker_id': worker.id, 'address': worker.address, 'status': worker.status} for worker in workers])

@app.route('/jobs', methods=['GET'])
def view_jobs():
    jobs = Job.query.all()
    return jsonify([{'job_id': job.id, 'status': job.status, 'user_id': job.user_id, 'description': job.description} for job in jobs])

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=4003)
