# TO-DO:
Zookeeper.


# MapReduce System

This is a MapReduce System implemented for our class PLH 607.
We implemented it from scratch.
Each service is built in a docker container.
Then we deploy them as pods in a k8s cluster.

# Important notes!
We used Docker-Desktop for our k8s cluster environment.
Docker Desktop creates a simple one node cluster.
That's why we didn't need NFS or any similar Distributed file system.
In a production environment, this won't be true and slight modifications will be necessary (e.x. volume mounts in our yaml files).

In our implementation we have created a shared volume for our monitor and workers where we manually put our test file (the file were the system will be applied) and the functions.py file .
You should find it and change it to your own directory:
In other words you should the path in the yaml of monitoring:

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
                )


# Quick Tutorial

Inside the Demo file, you will find a step by step guide to actually test our implementation.
Before being able to test it you should build it though.
That's why for each service, you should go in their folder and :

    make build
    make push

Make sure to push them correctly in you local docker repository. May need modifications regarding the port (default 5000 was binded for us).

Once you have your containers, you will have to deploy your pods in you k8s cluster.
You will have to go again in each folder (except worker) and execute:

    kubectl apply -f <service>.yaml
    
This will deploy both the pod and the service needed. (In the case of monitoring service much much more!)


Now your cluster should be set!
You can now follow the Demo file and test it yourself.
