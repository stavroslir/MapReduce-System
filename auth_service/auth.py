from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
from db import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'we-are-super-safe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db.init_app(app)

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['sub']).first()
        except:
            return jsonify({'message': 'token is invalid'})
        
        return f(current_user, *args, **kwargs)
    return decorator

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Login failed!'})

    token = jwt.encode({
        'sub': user.username,
        'role': user.role,
        'email': user.email,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        app.config['SECRET_KEY'])
    
    return jsonify({'token': token})

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'Cannot perform that function!'})

    data = request.get_json()
    
    # Check if a user with the given username already exists
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Username already exists!'})

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password, email=data['email'], role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    print_db()
    return jsonify({'message': 'New user created!'})

@app.route('/user/<username>', methods=['DELETE'])
@token_required
def delete_user(current_user, username):
    if current_user.role != 'admin':
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User has been deleted!'})

def print_db():
    users = User.query.all()  # This line fetches all records from the User table
    for user in users:
        print(f'ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}')




if __name__ == '__main__':
    with app.app_context(): # Add this line
        db.create_all()  # This will create the database file using SQLAlchemy
        hashed_password = generate_password_hash("adminpassword", method='sha256')
        new_user = User(username="admin", password=hashed_password, email="admin@example.com", role="admin")
        db.session.add(new_user)
        db.session.commit()
        print_db()
    app.run(host='0.0.0.0', port=5000)
