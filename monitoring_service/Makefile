# Define the name of the image you want to build
IMAGE_NAME = monitor

# Define the version for the docker image
VERSION = latest

# Define the ports
CONTAINER_PORT = 6000
HOST_PORT = 6000

# This is the default target, which will be executed when you run `make` or `make build`
all: build

# This target builds the Docker image, with the name and the version specified above
build:
	docker build -t $(IMAGE_NAME):$(VERSION) .

# This target runs the Docker image, in case you want to execute it as well
run:
	docker run -it --rm -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_NAME):$(VERSION)

# This target pushes the Docker image to DockerHub
push:
	docker push $(IMAGE_NAME):$(VERSION)

# This target removes the Docker image from your local Docker repository
clean:
	docker rmi $(IMAGE_NAME):$(VERSION)
