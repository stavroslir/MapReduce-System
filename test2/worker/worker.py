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
            print("executing function code.")
            # Execute the function code
            exec(request.function_code)
            print("executed.")
            # Get the function from the local scope
            function = locals()[request.function_name]
            with open(request.input_path, 'r') as file:
                print("opening input file", request.input_path)
                data = file.read()
            output = function(data)
            print("yo")
            print(request.output_path)
            with open(request.output_path, 'w') as file:
                print("opening output file",request.output_path)
                file.write(output)
                print("did it")
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
