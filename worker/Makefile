# Define the name of the image you want to build
IMAGE_NAME = worker2

# Define the version for the docker image
VERSION = latest

# Define the ports
CONTAINER_PORT = 5005
HOST_PORT = 5005

# This is the default target, which will be executed when you run `make` or `make build`
all: build

# This target builds the Docker image, with the name and the version specified above
build:
	docker build -t $(IMAGE_NAME):$(VERSION) .

# This target runs the Docker image, in case you want to execute it as well
run:
	docker run -v /Users/stavroslironis/Desktop/MapReduce-System/worker:/app -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_NAME):$(VERSION)

# This target pushes the Docker image to DockerHub
push:
	docker push $(IMAGE_NAME):$(VERSION)

# This target removes the Docker image from your local Docker repository
clean:
	docker rmi $(IMAGE_NAME):$(VERSION)
