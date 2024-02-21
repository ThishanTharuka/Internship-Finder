from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # MongoDB connection string
db = client['internship_finder']
collection = db['jobs']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    job_title = request.form['job_title']
    location = request.form['location']
    salary = request.form['salary']
    working_days = request.form['working_days']
    closing_date = request.form['closing_date']
    description = request.form['discription']
    duties = request.form['duties']
    requirements = request.form['requirments']

    # Insert data into MongoDB
    job_data = {
        'job_title': job_title,
        'location': location,
        'salary': salary,
        'working_days': working_days,
        'closing_date': closing_date,
        'description': description,
        'duties': duties,
        'requirements': requirements
    }

    collection.insert_one(job_data)

    return "Job added successfully!"

if __name__ == '__main__':
    app.run(debug=True)