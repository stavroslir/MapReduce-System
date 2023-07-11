# MapReduce System

This is a MapReduce System implemented for our class PLH 607.
We implemented it from scratch.


# Implementation
Each service is built in a docker container.
Then we deploy them as pods in a k8s cluster.

## Authentication Service

Our Authentication Service consists of:

* A database where we stored our users, along with their credentials. 
    This database is initialized with a single admin entry.

* A Flask API that interacts with the User Interface having numerous endpoints where it creates and deletes users.

When a user logs in a JWT is issued. This token is valid for 30 minutes and comes with certain accesses for each user(admin and user). The user will have to include this token in every following request he/she does.

The /validate_token endpoint will be called in every request to actually check the token and return the appropriate info (valid token and role).

## User Interface Service

Our UI is CLI implemented. The way it works is as an intermediary to our services. The user will submit his/her requests in the UI and the service will forward them to the appropriate service. It consists of a FLASK API. It would be efficient to create a gRPC with the Authentication service, since every call uses the /validate_token endpoint to check the Token. We will work on this.

## Monitoring Service

Our Monitoring Service is the backbone of our distributed system, ensuring that tasks are appropriately dispatched and executed across our worker nodes. It consists of:

* Database: A database where info about the Jobs and the Workers of our system is stored.

* Job Dispatcher: The Job Dispatcher is responsible for assigning tasks to available workers. It continually checks the job queue for new tasks and assigns them to idle workers. It also monitors the status of running tasks and updates their status upon completion. A job is created when the /submit_job endpoint is reached.

* Integration with Kubernetes: The Monitoring Service is designed to work seamlessly with Kubernetes. It uses the Kubernetes API to create and manage worker pods, ensuring that the system can scale up and down as needed. A worker will be created if an admin reaches the /register_worker endpoint of the ui. With each worker a gRPC is initiated at the moment of creation. Same goes for the /deregister_worker endpoint. If we want to scale down our system, we can delete a worker by providing its id.

The Monitoring Service exposes a FLASK API that allows users to submit jobs, view the status of jobs, and manage workers.
In essence, the Monitoring Service is the orchestrator of our distributed system, managing the workers and ensuring that all tasks are executed in a timely and reliable manner.

## Workers

Our workers are actually pretty simple in implementation. They are created by our monitoring service and work as a gRPC server. They stay put until the get a message.
They can either return their status or execute code that is provided.
    
- Security note!!!
    * We use the "exec" command for code execution which is highly not recommended. However, no matter what we would use, when you execute arbitrary code, there will always be a high security risk. We have chosen to use the "exec" command because our focus is not on the security scope.


# Important notes!
We used Docker-Desktop for our k8s cluster environment.
Docker Desktop creates a simple one node cluster.
That's why we didn't need HDFS or any similar Distributed file system.
In a production environment, this won't be true and slight modifications will be necessary (e.x. volume mounts in our yaml files, probably more).

In our implementation we have created a shared volume for our monitor and workers where we manually put our test file (the file were the system will be applied) and the functions.py file.
You should find it and change it to your own directory:
Specifically, you should change the path in the yaml of monitoring:

    volumes:
        - name: hostpath-storage
            hostPath:
            path: /Users/stavroslironis/Desktop/storage         # this should be changed to your own
            type: Directory

and in the actual code of the monitoring/register endpoint, where we create the workers, line 182:

    name="hostpath-storage",
                    host_path=client.V1HostPathVolumeSource(
                        path="/Users/stavroslironis/Desktop/storage",           # this should be changed
                        type="Directory"
                    )


# Quick Tutorial

Inside the Demo file, you will find a step by step guide to actually test our implementation.
Before being able to test it you should build it though.
That's why for each service, you should go in their folder and :

    make build
    make push

Make sure to push them correctly in you local docker repository. May need modifications regarding the port (default 5000 was binded for us). If you have a different port, change it in each Makefile and in each yaml, where the image is mentioned.

Once you have your containers, you will have to deploy your pods in you k8s cluster.
You will have to go again in each folder (except worker) and execute:

    kubectl apply -f <service>.yaml

This will deploy both the pod and the service needed. (In the case of monitoring service much much more!)

Now your cluster should be set!
The way we test it is by creating an Alice pod, representing a client and then exec in it.

    kubectl exec -it alice -- /bin/bash

From here on you can now follow the Demo file and test it yourself.


# Kubernetes Deployment

For our Kubernetes deployment we used Docker-Desktop. It's a very easy to use tool that provides the ability to deploy a one node cluster locally.
A guide on how to install Docker-Desktop on your machine can be found here: https://www.docker.com/products/docker-desktop/


# Contributions

- **[Vasilis Anagnostou, Stavros Lyronis]**:  Authentication service, UI service, Monitoring Service, Workers, Deployment on Kubernetes
- **[Panagiotis Mihas]**: Fault tolerance - Zookeeper