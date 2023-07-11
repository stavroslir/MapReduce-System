import os
import grpc
from concurrent import futures
import time
import worker_pb2
import worker_pb2_grpc

class Worker(worker_pb2_grpc.WorkerServicer):   # Worker class 

    def __init__(self):
        self.status = worker_pb2.Status.WorkerStatus.IDLE       #init with status IDLE

    def AssignTask(self, request, context):

        self.status = worker_pb2.Status.WorkerStatus.BUSY       # Set worker status as BUSY
        try:
            exec(request.function_code)                             # Execute the function code
            function = locals()[request.function_name]              # Get the function from the local scope
            output = []

            if request.task_type== 1:                               #if Map request
                input_paths = request.input_path.split(',')
                print(f"Input paths: {input_paths}")  
                output.append(function(input_paths))
                print(output)
                with open(request.output_path, 'w') as file:
                    file.write(str(output))

            elif request.task_type== 2:                              #if Reduce request
                input_path = request.input_path     
                print(f"Reading from input path: {input_path}") 
                with open(input_path.strip(), 'r') as file:  
                    data = file.read()
                output.append(function(data))
                with open(request.output_path, 'w') as file:
                    file.write(str(output))

            else:                                                    #if Shuffle request
                input_path = request.input_path
                print(f"Reading from input path: {input_path}") 
                with open(input_path.strip(), 'r') as file:  
                    data = file.read()
                output.append(function(data))
                with open(request.output_path, 'w') as file:
                    file.write('\n'.join(output))
            self.status = worker_pb2.Status.WorkerStatus.IDLE                   # Set worker status as IDLE
            return worker_pb2.Status(status=worker_pb2.Status.WorkerStatus.ACCEPTED) 
        
        except Exception as e:
            print(f"Error while processing task: {str(e)}")
            return worker_pb2.Status(status=worker_pb2.Status.WorkerStatus.ERROR)
    
    def GetStatus(self, request, context):
        return worker_pb2.Status(status=self.status)                # Return the current worker status

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))        # Create a gRPC server
    worker_pb2_grpc.add_WorkerServicer_to_server(Worker(), server)          # Add the Worker service to the server
    server.add_insecure_port('0.0.0.0:5005')                                # Listen on port 5005
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
