FROM python:3.8-slim-buster

WORKDIR /app

COPY worker.py ./
COPY worker_pb2.py ./
COPY worker_pb2_grpc.py ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50051

CMD ["python", "worker.py"]
