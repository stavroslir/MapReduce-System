from flask import Flask, request, jsonify
from database import db, Job, Worker, init_app
import grpc
import worker_pb2
import worker_pb2_grpc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
stub_dict = {}

@app.route('/job', methods=['POST'])
def submit_job():
    data = request.get_json()
    new_job = Job(status='submitted', user_id=data['user_id'], description=data['job_description'])
    db.session.add(new_job)
    db.session.commit()

    for worker in Worker.query.all():
        print(worker, worker.address)
        stub = worker_pb2_grpc.WorkerStub(grpc.insecure_channel(worker.address))
        task = worker_pb2.Task()
        task.task_type = worker_pb2.Task.TaskType.Value(data['task_type'])
        task.input_path = data['input_path']
        task.output_path = data['output_path']
        response = stub.AssignTask(task)

    return jsonify({'message': 'New job created!', 'job_id': new_job.id})

@app.route('/jobs', methods=['GET'])
def view_jobs():
    jobs = Job.query.all()
    return jsonify([{'job_id': job.id, 'status': job.status, 'user_id': job.user_id, 'description': job.description} for job in jobs])

@app.route('/register', methods=['POST'])
def register_worker():
    data = request.get_json()
    new_worker = Worker(address=data['address'], status='IDLE')
    db.session.add(new_worker)
    db.session.commit()

    stub = worker_pb2_grpc.WorkerStub(grpc.insecure_channel(new_worker.address))
    stub_dict[new_worker.id] = stub

    return jsonify({'message': 'New worker registered!', 'worker_id': new_worker.id})

@app.route('/deregister', methods=['POST'])
def deregister_worker():
    data = request.get_json()
    worker = Worker.query.get(data['worker_id'])
    db.session.delete(worker)
    db.session.commit()

    del stub_dict[worker.id]

    return jsonify({'message': 'Worker deregistered!'})

@app.route('/workers', methods=['GET'])
def view_workers():
    workers = Worker.query.all()
    return jsonify([{'worker_id': worker.id, 'address': worker.address, 'status': worker.status} for worker in workers])

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=6000)
