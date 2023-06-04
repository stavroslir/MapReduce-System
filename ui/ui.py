from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

AUTH_SERVICE_URL = 'http://172.17.0.2:5000'  # Replace with the URL of your Authentication Service
MONITOR_SERVICE_URL = 'http://localhost:6000'  # Replace with the URL of your Monitoring Service

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response = requests.post(f'{AUTH_SERVICE_URL}/login', json=data)
    return jsonify(response.json()), response.status_code

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    headers = {'x-access-tokens': request.headers.get('x-access-tokens')}
    response = requests.post(f'{AUTH_SERVICE_URL}/user', headers=headers, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/delete_user/<username>', methods=['DELETE'])
def delete_user(username):
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    headers = {'x-access-tokens': token}
    response = requests.delete(f'{AUTH_SERVICE_URL}/user/{username}', headers=headers)

    return jsonify(response.json()), response.status_code


@app.route('/submit_job', methods=['POST'])
def submit_job():
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    data = request.get_json()
    headers = {'x-access-tokens': token}
    response = requests.post(f'{MONITOR_SERVICE_URL}/job', headers=headers, json=data)

    return jsonify(response.json()), response.status_code

@app.route('/view_jobs', methods=['GET'])
def view_jobs():
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    headers = {'x-access-tokens': token}
    response = requests.get(f'{MONITOR_SERVICE_URL}/jobs', headers=headers)

    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
