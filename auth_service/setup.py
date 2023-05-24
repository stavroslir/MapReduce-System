from werkzeug.security import generate_password_hash, check_password_hash
from db import db, User

def print_db():
    users = User.query.all()  # This line fetches all records from the User table
    for user in users:
        print(f'ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}')


if __name__ == '__main__':    
    db.create_all()  # This will create the database file using SQLAlchemy
    hashed_password = generate_password_hash("adminpassword", method='sha256')
    new_user = User(username="admin", password=hashed_password, email="admin@example.com", role="admin")
    db.session.add(new_user)
    db.session.commit()
    print_db()
    print("gtxm")

