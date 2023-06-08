from flask import Flask, request
import grpc
import worker_pb2
import worker_pb2_grpc

app = Flask(__name__)

# Assume that the worker is running on localhost at this port
stub = worker_pb2_grpc.WorkerStub(grpc.insecure_channel('localhost:50051'))

@app.route('/assign_task', methods=['POST'])
def assign_task():
    task = worker_pb2.Task()  # construct a Task based on the input data
    task.task_type = worker_pb2.Task.TaskType.Value(request.json['task_type'])
    task.input_path = request.json['input_path']
    task.output_path = request.json['output_path']
    
    # Assign the task to the worker
    response = stub.AssignTask(task)
    return response.message, 200

@app.route('/worker_status', methods=['GET'])
def worker_status():
    status = stub.GetStatus(worker_pb2.Empty())
    return worker_pb2.Status.WorkerStatus.Name(status.status), 200

if __name__ == '__main__':
    app.run(port=8080)
