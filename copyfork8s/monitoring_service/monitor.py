from flask import Flask, request, jsonify
from database import db, Job, Worker, init_app
import grpc
import worker_pb2
import worker_pb2_grpc
import threading
import time
from kubernetes import client
from kubernetes.config import load_incluster_config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
stub_dict = {}

class Dispatcher:
    def __init__(self, app):
        self.thread = threading.Thread(target=self.run)
        self.app = app

    def start(self):
        self.thread.start()

    def run(self):
        while True:
            self.dispatch_jobs()
            self.check_worker_status()
            time.sleep(1)  

    def dispatch_jobs(self):
        with self.app.app_context():
            for job in Job.query.filter(Job.status.in_(['submitted', 'waiting'])).all():
                # Check if the job has any dependencies
                print(f"Job {job.id} dependencies: {job.dependencies}")
                if job.dependencies:
                    # Check if all dependencies have completed
                    dependencies_completed = all(
                        Job.query.get(dep_id).status == 'completed' for dep_id in job.dependencies
                    )
                    if not dependencies_completed:
                            continue  # Skip this job if its dependencies have not completed
                for worker in Worker.query.filter_by(status='IDLE').all():
                    stub = stub_dict[worker.id]
                    task = worker_pb2.Task()
                    task.job_id = job.id
                    task.task_type = job.task_type
                    # Check if the input_path is a list
                    if isinstance(job.input_path, list):
                        task.input_path = ','.join(job.input_path)  # Join all paths into a single string
                    else:
                        task.input_path = job.input_path
                    task.output_path = job.output_path
                    task.function_name = job.function_name  
                    task.function_code = job.function_code
                    response = stub.AssignTask(task)
                    print(f"Dispatched job {job.id} to worker {worker.id}, response: {response.status}")
                    if response.status == worker_pb2.Status.WorkerStatus.ACCEPTED:
                        job.status = 'running'
                        job.worker_id = worker.id 
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
                        job = Job.query.filter_by(status='running', worker_id=worker.id).first()
                        if job:
                            job.status = 'completed'
                            waiting_jobs = Job.query.filter(Job.dependencies.contains([job.id])).all()
                            for waiting_job in waiting_jobs:
                                waiting_job.status = 'submitted'
                        db.session.commit()
                    else:
                        print(f"Worker {worker.id} is still busy")
                except grpc.RpcError as e:
                    print(f"GetStatus RPC failed for worker {worker.id}. Error: {str(e)}")

def split_data_into_chunks(data, num_chunks):
    
    # Split the data into words
    words = data.split()
    chunk_size = len(words) // num_chunks
    chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
    chunks = [' '.join(chunk) for chunk in chunks]

    return chunks

@app.route('/job', methods=['POST'])
def submit_job():
    data = request.get_json()
    with open(data['function_file'], 'r') as file:
        function_code = file.read()   
    with open(data['input_path'], 'r') as file:
        f = file.read()
    chunks = split_data_into_chunks(f, num_chunks=10)

    # Create the Map jobs
    map_jobs = []
    for i, chunk in enumerate(chunks):
        # Write the chunk to a new input file
        chunk_input_path = f'/app/shared/map_input_{i}'
        with open(chunk_input_path, 'w') as file:
            file.write(chunk)

        map_job = Job(status='submitted', user_id=data['user_id'], 
                      description=data['job_description'], task_type='MAP', 
                      input_path=f'/app/shared/map_input_{i}', output_path=f'/app/shared/map_output_{i}', 
                      function_name="map_function", function_code=function_code)
        db.session.add(map_job)
        map_jobs.append(map_job)
    db.session.commit()

    shuffle_job = Job(status='waiting', user_id=data['user_id'], 
                  description=data['job_description'], task_type='SHUFFLE', 
                  input_path=[map_job.output_path for map_job in map_jobs], 
                  output_path='/app/shared/shuffle_output', 
                  function_name='shuffle_function', function_code=function_code,
                  dependencies=[map_job.id for map_job in map_jobs])
    db.session.add(shuffle_job)
    db.session.commit()

    # Create the Reduce job and set its dependency to the Shuffle jobs
    reduce_job = Job(status='waiting', user_id=data['user_id'], 
                    description=data['job_description'], task_type='REDUCE', 
                    input_path=shuffle_job.output_path, 
                    output_path='/app/shared/reduce_output', 
                    function_name='reduce_function', function_code=function_code,
                    dependencies=[shuffle_job.id])
    db.session.add(reduce_job)
    db.session.commit()


    return jsonify({'message': 'New job created!', 'job_id': map_jobs[0].id})

@app.route('/register', methods=['POST'])
def register_worker():
    new_worker = Worker(status='IDLE')
    db.session.add(new_worker)
    db.session.commit()

    # Create a new worker pod
    load_incluster_config()
    v1 = client.CoreV1Api()
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(
        name=f"worker-{new_worker.id}",
        labels={"app": f"worker-{new_worker.id}"}),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name="worker",
                    image="localhost:5004/worker-k8s:latest",
                    ports=[client.V1ContainerPort(container_port=5005)],
                    env=[
                        client.V1EnvVar(
                            name="WORKER_ID",
                            value=str(new_worker.id)
                        ),
                        client.V1EnvVar(
                            name="MONITOR_ADDRESS",
                            value="monitor-service.default.svc.cluster.local:80"
                        )
                    ],
                    volume_mounts=[
                        client.V1VolumeMount(
                            name="hostpath-storage",
                            mount_path="/app/shared"
                        )
                    ]
                )
            ],
            volumes=[
                client.V1Volume(
                    name="hostpath-storage",
                    host_path=client.V1HostPathVolumeSource(
                        path="/Users/stavroslironis/Desktop/storage",
                        type="Directory"
                    )
                )
            ]
        )
    )
    v1.create_namespaced_pod(namespace="default", body=pod)
    service = client.V1Service(
        metadata=client.V1ObjectMeta(name=f"worker-{new_worker.id}"),
        spec=client.V1ServiceSpec(
            selector={"app": f"worker-{new_worker.id}"},
            ports=[client.V1ServicePort(port=5005, target_port=5005)]
        )
    )
    v1.create_namespaced_service(namespace="default", body=service)

    # Wait for the worker pod to start
    time.sleep(10)  # Adjust this delay as needed

    # Create the gRPC stub and open the connection
    stub = worker_pb2_grpc.WorkerStub(grpc.insecure_channel(f"worker-{new_worker.id}.default.svc.cluster.local:5005"))
    stub_dict[new_worker.id] = stub

    # Check if the worker is running and reachable
    try:
        response = stub.GetStatus(worker_pb2.Empty())
        print(f"Worker {new_worker.id} status: {response.status}")
    except grpc.RpcError as e:
        print(f"GetStatus RPC failed for worker {new_worker.id}. Error: {str(e)}")

    return jsonify({'message':'New worker registered!', 'worker_id': new_worker.id})


@app.route('/deregister', methods=['POST'])
def deregister_worker():
    data = request.get_json()
    worker_id = int(data['worker_id'])
    worker = Worker.query.get(worker_id)

    if worker is None:
        return jsonify({'message': f'No worker found with ID {worker_id}'}), 404

    # Delete the worker's pod and service from Kubernetes
    load_incluster_config()
    v1 = client.CoreV1Api()
    v1.delete_namespaced_pod(name=f"worker-{worker_id}", namespace="default")
    v1.delete_namespaced_service(name=f"worker-{worker_id}", namespace="default")

    # Remove the worker from the database
    db.session.delete(worker)
    db.session.commit()

    # Remove the worker's stub from stub_dict
    del stub_dict[worker_id]

    return jsonify({'message': 'Worker deregistered!'})

@app.route('/workers', methods=['GET'])
def view_workers():
    workers = Worker.query.all()
    return jsonify([{'worker_id': worker.id, 'status': worker.status} for worker in workers])

@app.route('/jobs', methods=['GET'])
def view_jobs():
    jobs = Job.query.all()
    return jsonify([{'job_id': job.id, 'status': job.status, 'user_id': job.user_id, 'description': job.description} for job in jobs])

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    dispatcher_thread = Dispatcher(app)
    dispatcher_thread.start()   
    app.run(host='0.0.0.0', port=4003)
