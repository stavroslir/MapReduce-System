from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
AUTH_SERVICE_URL = 'http://auth-service'                                #k8s service name
MONITOR_SERVICE_URL = 'http://monitor-service'                          #k8s service name

@app.route('/login', methods=['POST'])
def login(): 
    data = request.get_json()
    response = requests.post(f'{AUTH_SERVICE_URL}/login', json=data)            # Forward the request to the authentication service 
    return jsonify(response.json()), response.status_code

@app.route('/register', methods=['POST'])                                       # register endpoint accords to the authenitcation /user (creates user) endpoint
def register():

    data = request.get_json()
    token = request.headers.get('x-access-tokens')
    headers = {'x-access-tokens': token}
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)           # Forward the request to the authentication service  to validate the token 
    validation_data = validation_response.json()

    if validation_data.get('valid') and validation_data.get('role') == 'admin':
        response = requests.post(f'{AUTH_SERVICE_URL}/user', headers=headers, json=data)                # if valid and the role is admin, forward it to /user endpoint
        return jsonify(response.json()), response.status_code
    return jsonify({'message': 'Token is invalid.'}), 401

@app.route('/delete_user/<username>', methods=['DELETE'])                         # delete_user endpoint accords to the authenitcation /user/<username> (deletes user with <username>) endpoint
def delete_user(username):

    token = request.headers.get('x-access-tokens')
    headers = {'x-access-tokens': token}
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)           # Forward the request to the authentication service  to validate the token 
    validation_data = validation_response.json()

    if validation_data.get('valid') and validation_data.get('role') == 'admin':
        response = requests.delete(f'{AUTH_SERVICE_URL}/user/{username}', headers=headers)              # if valid and the role is admin, forward it to /user/<username> endpoint
        return jsonify(response.json()), response.status_code
    
    return jsonify({'message': 'Token is invalid.'}), 401

@app.route('/submit_job', methods=['POST'])                                     # submit_job endpoint accords to the monitoring service job (creates a job) endpoint
def submit_job():

    data = request.get_json()
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    headers = {'x-access-tokens': token}
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)               # Forward the request to the authentication service  to validate the token
    validation_data = validation_response.json()

    if validation_data.get('valid'):
        response = requests.post(f'{MONITOR_SERVICE_URL}/job', headers=headers, json=data)                  # if valid, forward it to /job endpoint
        return jsonify(response.json()), response.status_code
    
    return jsonify({'message': 'Token is invalid or you do not have permissions to perform this action.'}), 401


@app.route('/view_jobs', methods=['GET'])                                           # view_jobs endpoint accords to the monitoring service jobs (print jobs ongoing and completed) endpoint
def view_jobs():

    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    headers = {'x-access-tokens': token}
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)           # Forward the request to the authentication service  to validate the token 
    validation_data = validation_response.json()

    if validation_data.get('valid'):
        response = requests.get(f'{MONITOR_SERVICE_URL}/jobs', headers=headers)                         # if valid, forward it to /jobs endpoint
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Token is invalid or you do not have permissions to perform this action.'}), 401

@app.route('/register_worker', methods=['POST'])                                # register_worker endpoint accords to the monitoring service register (creates worker) endpoint
def register_worker():
    token = request.headers.get('x-access-tokens')
    data = request.get_json()
    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)           # Forward the request to the authentication service  to validate the token
    validation_data = validation_response.json()

    # Only admin users can register a worker
    if validation_data.get('valid') and validation_data.get('role') == 'admin':
        response = requests.post(f'{MONITOR_SERVICE_URL}/register', headers=headers, json=data)            # if valid and role is admin, forward it to /register endpoint
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Token is invalid or you do not have permissions to perform this action.'}), 401

@app.route('/deregister_worker', methods=['POST'])                      # deregister_worker endpoint accords to the monitoring service deregister (deletes worker) endpoint
def deregister_worker():
    token = request.headers.get('x-access-tokens')
    data = request.get_json()
    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)           # Forward the request to the authentication service  to validate the token
    validation_data = validation_response.json()

    # Only admin users can deregister a worker
    if validation_data.get('valid') and validation_data.get('role') == 'admin':
        response = requests.post(f'{MONITOR_SERVICE_URL}/deregister', headers=headers, json=data)        # if valid and role is admin, forward it to /deregister endpoint
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Token is invalid or you do not have permissions to perform this action.'}), 401

@app.route('/view_workers', methods=['GET'])                    # view_workers endpoint accords to the monitoring service workers (prints register workers) endpoint
def view_workers():
    token = request.headers.get('x-access-tokens')
    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)         # Forward the request to the authentication service  to validate the token
    validation_data = validation_response.json()

    if validation_data.get('valid'):
        response = requests.get(f'{MONITOR_SERVICE_URL}/workers', headers=headers)                  # if valid, forward it to /workers endpoint
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Token is invalid.'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)
