import os
import grpc
from concurrent import futures
import time
import worker_pb2
import worker_pb2_grpc

class Worker(worker_pb2_grpc.WorkerServicer):
    def __init__(self):
        self.status = worker_pb2.Status.IDLE

    def AssignTask(self, request, context):
        self.status = worker_pb2.Status.BUSY
        # Execute the function code
        exec(request.function_code)
        # Get the function from the local scope
        function = locals()[request.function_name]
        with open(request.input_path, 'r') as file:
            data = file.read()
        output = function(data)
        with open(request.output_path, 'w') as file:
            for pair in output:
                file.write(f"{pair[0]} {pair[1]}\n")
        self.status = worker_pb2.Status.IDLE
        return worker_pb2.Message(message="Task completed successfully")

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
