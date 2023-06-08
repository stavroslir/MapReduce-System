import os
import grpc
from concurrent import futures
import time
import itertools
import worker_pb2
import worker_pb2_grpc
from collections import defaultdict


# The actual map, shuffle, and reduce functions should go here
def map_function(data):
    word_list = data.split()
    return [(word, 1) for word in word_list]


def shuffle_function(mapped_data):
    result = defaultdict(list)
    for key, value in sorted(mapped_data, key=lambda x: x[0]):
        result[key].append(value)
    return list(result.items())


import ast

def reduce_function(shuffled_data):
    result = {}
    for key, *values_str_parts in shuffled_data:
        # Concatenate the parts of values_str to form a valid list representation.
        values_str = ''.join(values_str_parts)
        # Parse values_str as a list.
        values = ast.literal_eval(values_str)
        # Convert the elements of values to integers and sum them.
        total_count = sum(int(value) for value in values)
        result[key] = total_count
    return result






class Worker(worker_pb2_grpc.WorkerServicer):
    def __init__(self):
        self.status = worker_pb2.Status.IDLE

    def AssignTask(self, request, context):
        self.status = worker_pb2.Status.BUSY
        if request.task_type == worker_pb2.Task.MAP:
            with open(request.input_path, 'r') as file:
                data = file.read()
            map_output = map_function(data)
            with open(request.output_path, 'w') as file:
                for pair in map_output:
                    file.write(f"{pair[0]} {pair[1]}\n")
        elif request.task_type == worker_pb2.Task.SHUFFLE:
            with open(request.input_path, 'r') as file:
                mapped_data = [tuple(line.split()) for line in file.readlines()]
            shuffled_data = shuffle_function(mapped_data)
            with open(request.output_path, 'w') as file:
                for pair in shuffled_data:
                    file.write(f"{pair[0]} {pair[1]}\n")
        elif request.task_type == worker_pb2.Task.REDUCE:
            with open(request.input_path, 'r') as file:
                shuffled_data = [tuple(line.split()) for line in file.readlines()]
            reduce_output = reduce_function(shuffled_data)
            with open(request.output_path, 'w') as file:
                for word, count in reduce_output.items():
                    file.write(f"{word} {count}\n")
        self.status = worker_pb2.Status.IDLE
        return worker_pb2.Message(message="Task completed successfully")

    def GetStatus(self, request, context):
        return worker_pb2.Status(status=self.status)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    worker_pb2_grpc.add_WorkerServicer_to_server(Worker(), server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
