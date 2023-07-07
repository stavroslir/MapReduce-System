# Containers

# Test with containers only
Start with setting the containers up (use the makefiles)

First, as an admin, you want to create a new user. Here is how you might do this with a curl command.
# First login:
    curl -X POST -H "Content-Type: application/json" -d '{"username":"admin", "password":"adminpassword"}' http://localhost:4001/login

This should return a JWT in the response,eg:
{"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTYxMzgwNzc2MywiZXhwIjoxNjEzODA5NTYzfQ.YHYWjy7QcwCeNnuLMLT3sQEgQ5rFoFj8aeXD8zp-80U"}


# Then create a user:
    curl -X POST http://localhost:4001/register -H "Content-Type: application/json" -H "x-access-tokens: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJpYXQiOjE2ODc5NjEyNDksImV4cCI6MTY4Nzk2MzA0OX0.r-q802M6dYiZoOO3JGBIRNUcVWvyBIRvW00vjDwN5x0" -d '{"username": "new_user", "password": "new_password", "email": "new_user@example.com", "role": "user"}'
This command sends a POST request to the /register endpoint of the UI Service with the necessary data to create a new user. The UI Service then forwards this request to the Authentication Service, which actually creates the user.


# Register a worker: 
(if you want to find the IP of the worker container run:     docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ID)

    curl -X POST -H "Content-Type: application/json" -d '{
    "address": "172.17.0.5:5005"
}' http://localhost:4003/register                                                                    

Submit a job:
    curl -X POST \
        -H "Content-Type: application/json" \
        -H "x-access-tokens: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJpYXQiOjE2ODc5NjEyNDksImV4cCI6MTY4Nzk2MzA0OX0.r-q802M6dYiZoOO3JGBIRNUcVWvyBIRvW00vjDwN5x0" \
        -d '{
            "user_id": "1", 
            "task_type": "MAP", 
            "function_file": "'"$(base64 -i /Users/stavroslironis/Desktop/MapReduce-System/functions.py)"'", 
            "job_description": "Test job", 
            "input_path": "/app/test", 
            "output_path": "/app/output", 
            "function_name": "map_function"
        }' \
        http://localhost:4001/submit_job


This is working for now.


# TO-DO:

1. In test2 i have implemented the whole monitoring.
Tasks are automatically put to queue and picked up by idle workers. No idea about race conditions. Tested with 2 workers and worked fine. Workers are chosen randomly if IDLE. Needs improvement.

2. Should copy the code of test2 in copy4k8s for monitoring and workers. Monitoring yaml will need to have a shared volume as well.


3. When this is done we will look into fault tolerance- Zookeeper.

