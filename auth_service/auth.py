from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from db import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'we-are-super-safe'                              # Secret static key for the JWT, for demo purpose
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db.init_app(app)

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()          # Query database for the username
    if not user or not check_password_hash(user.password, data['password']):    # Return message if not found
        return jsonify({'message': 'Login failed!'})

    token = jwt.encode({                                                        # else create a JWT for him/her and return it
        'sub': user.username,
        'role': user.role,
        'email': user.email,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        app.config['SECRET_KEY'])
    
    return jsonify({'token': token})

@app.route('/user', methods=['POST'])
def create_user():
    
    data = request.get_json()
    existing_user = User.query.filter_by(username=data['username']).first()     # Check if a the username already exists.
    if existing_user:
        return jsonify({'message': 'Username already exists!'})

    hashed_password = generate_password_hash(data['password'], method='sha256')         #if not, create the user and commit it at the database.
    new_user = User(username=data['username'], password=hashed_password, email=data['email'], role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})

@app.route('/user/<username>', methods=['DELETE'])
def delete_user( username):

    user = User.query.filter_by(username=username).first()              
    if not user:                                                            # Check if a the user exists.
        return jsonify({'message': 'No user found!'})           
    
    db.session.delete(user)                                                 #if you find him at the database, delete him and commit.
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'})

@app.route('/validate_token', methods=['GET'])
def validate_token():
    token = request.headers.get('x-access-tokens')                                  # Get the token from the request headers
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])    # Try to decode the token
    except:
        return jsonify({'valid': False, 'role': None})                              # If invalid, return the appropriate message

    return jsonify({'valid': True, 'role': data['role']})                           # Else, return the appropriate info

if __name__ == '__main__':

    with app.app_context(): 
        db.create_all()                                                             # This will create the database file using SQLAlchemy
        hashed_password = generate_password_hash("adminpassword", method='sha256')
        new_user = User(username="admin", password=hashed_password, email="admin@example.com", role="admin")            # Init with admin user
        db.session.add(new_user)
        db.session.commit()

    app.run(host='0.0.0.0', port=4002)
