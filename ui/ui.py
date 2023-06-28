from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
AUTH_SERVICE_URL = 'http://172.17.0.3:4002'
MONITOR_SERVICE_URL = 'http://172.17.0.4:4003'

@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()
    token = request.headers.get('x-access-tokens')
    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)
    validation_data = validation_response.json()

    if validation_data.get('valid'):
        response = requests.post(f'{AUTH_SERVICE_URL}/user', headers=headers, json=data)

        return jsonify(response.json()), response.status_code
    return jsonify({'message': 'Token is invalid.'}), 401

@app.route('/delete_user/<username>', methods=['DELETE'])
def delete_user(username):

    token = request.headers.get('x-access-tokens')
    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)
    validation_data = validation_response.json()

    if validation_data.get('valid'):
        response = requests.delete(f'{AUTH_SERVICE_URL}/user/{username}', headers=headers)

    return jsonify(response.json()), response.status_code

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response = requests.post(f'{AUTH_SERVICE_URL}/login', json=data)
    return jsonify(response.json()), response.status_code

@app.route('/submit_job', methods=['POST'])
def submit_job():

    data = request.get_json()
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)
    validation_data = validation_response.json()

    if validation_data.get('valid'):
        response = requests.post(f'{MONITOR_SERVICE_URL}/job', headers=headers, json=data)
        return jsonify(response.json()), response.status_code
    
    return jsonify({'message': 'Token is invalid or you do not have permissions to perform this action.'}), 401


@app.route('/view_jobs', methods=['GET'])
def view_jobs():
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)
    validation_data = validation_response.json()

    if validation_data.get('valid'):
        response = requests.get(f'{MONITOR_SERVICE_URL}/jobs', headers=headers)
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Token is invalid or you do not have permissions to perform this action.'}), 401

@app.route('/register_worker', methods=['POST'])
def register_worker():
    token = request.headers.get('x-access-tokens')
    data = request.get_json()
    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)
    validation_data = validation_response.json()

    # Only admin users can register a worker
    if validation_data.get('valid') and validation_data.get('role') == 'admin':
        response = requests.post(f'{MONITOR_SERVICE_URL}/register', headers=headers, json=data)
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Token is invalid or you do not have permissions to perform this action.'}), 401

@app.route('/deregister_worker', methods=['POST'])
def deregister_worker():
    token = request.headers.get('x-access-tokens')
    data = request.get_json()
    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)
    validation_data = validation_response.json()

    # Only admin users can deregister a worker
    if validation_data.get('valid') and validation_data.get('role') == 'admin':
        response = requests.post(f'{MONITOR_SERVICE_URL}/deregister', headers=headers, json=data)
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Token is invalid or you do not have permissions to perform this action.'}), 401

@app.route('/view_workers', methods=['GET'])
def view_workers():
    token = request.headers.get('x-access-tokens')
    headers = {'x-access-tokens': token}

    # Validate token before forwarding request
    validation_response = requests.get(f'{AUTH_SERVICE_URL}/validate_token', headers=headers)
    validation_data = validation_response.json()

    if validation_data.get('valid'):
        response = requests.get(f'{MONITOR_SERVICE_URL}/workers', headers=headers)
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Token is invalid.'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)
