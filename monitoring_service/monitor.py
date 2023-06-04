from flask import Flask, request, jsonify
from database import db, Job, init_app

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

@app.route('/job', methods=['POST'])
def submit_job():
    data = request.get_json()
    new_job = Job(status='submitted', user_id=data['user_id'], description=data['description'])
    db.session.add(new_job)
    db.session.commit()

    return jsonify({'message': 'New job created!', 'job_id': new_job.id})

@app.route('/jobs', methods=['GET'])
def view_jobs():
    jobs = Job.query.all()
    return jsonify([{'job_id': job.id, 'status': job.status, 'user_id': job.user_id, 'description': job.description} for job in jobs])

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()  
    app.run(host='0.0.0.0', port=6000)
