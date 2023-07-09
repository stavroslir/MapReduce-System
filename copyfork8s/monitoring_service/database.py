from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(120), nullable=False)
    task_type = db.Column(db.String(120), nullable=False)
    input_path = db.Column(db.PickleType, nullable=False)
    output_path = db.Column(db.String(120), nullable=False)
    function_name = db.Column(db.String(120), nullable=False)
    function_code = db.Column(db.Text, nullable=False)
    dependencies = db.Column(db.PickleType, nullable=True)
    worker_id = db.Column(db.Integer, nullable=True)


class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # address = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    service_name = db.Column(db.String(120), nullable=True)

def init_app(app):
    db.init_app(app)
