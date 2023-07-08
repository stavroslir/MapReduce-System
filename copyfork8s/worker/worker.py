import os
import grpc
from concurrent import futures
import time
import worker_pb2
import worker_pb2_grpc
import json

class Worker(worker_pb2_grpc.WorkerServicer):
    def __init__(self):
        self.status = worker_pb2.Status.WorkerStatus.IDLE

    def AssignTask(self, request, context):
        self.status = worker_pb2.Status.WorkerStatus.BUSY
        try:
            # Execute the function code
            exec(request.function_code)
            # Get the function from the local scope
            function = locals()[request.function_name]
            output = []
            if request.task_type== 1:
                input_paths = request.input_path.split(',')
                print(f"Input paths: {input_paths}")  # Debugging print statement
                output.append(function(input_paths))
                print(output)
                with open(request.output_path, 'w') as file:
                    file.write(str(output))
            elif request.task_type== 2:
                input_path = request.input_path
                print(f"Reading from input path: {input_path}")  # Debugging print statement
                with open(input_path.strip(), 'r') as file:  # Use strip() to remove leading/trailing whitespace
                    data = file.read()
                    print(data)
                output.append(function(data))
                with open(request.output_path, 'w') as file:
                    file.write(str(output))
            else:
                input_path = request.input_path
                print(f"Reading from input path: {input_path}")  # Debugging print statement
                with open(input_path.strip(), 'r') as file:  # Use strip() to remove leading/trailing whitespace
                    data = file.read()
                output.append(function(data))
                with open(request.output_path, 'w') as file:
                    file.write('\n'.join(output))
            self.status = worker_pb2.Status.WorkerStatus.IDLE
            return worker_pb2.Status(status=worker_pb2.Status.WorkerStatus.ACCEPTED) 
        except Exception as e:
            print(f"Error while processing task: {str(e)}")
            return worker_pb2.Status(status=worker_pb2.Status.WorkerStatus.ERROR)
    
    def GetStatus(self, request, context):
        return worker_pb2.Status(status=self.status)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    worker_pb2_grpc.add_WorkerServicer_to_server(Worker(), server)
    server.add_insecure_port('0.0.0.0:5005')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
