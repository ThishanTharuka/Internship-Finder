from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
from gridfs import GridFS
from bson import Binary

app = Flask(__name__)

# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['mydb']
collection = db['users']

# Create a GridFS object
fs = GridFS(db)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    address = request.form.get('address')
    email = request.form.get('email')
    contact_number = request.form.get('contact_number')
    birthday = request.form.get('birthday')
    degree = request.form.get('degree')
    university = request.form.get('university')
    social_media_github = request.form.get('social_media_github')
    social_media_linkedin = request.form.get('social_media_linkedin')
    skills = request.form.get('skills')
    work_experiences = request.form.get('work_experiences')
    user_description = request.form.get('user_description')
    
    # Get technologies as a comma-separated string from the form
    technologies_string = request.form.get('technologies')

    # Split the string into a list of technologies
    technologies = [tech.strip() for tech in technologies_string.split(',')]
    
    # Convert birthday to datetime object
    birthday = datetime.strptime(birthday, '%Y-%m-%d')

    # Handle profile picture
    profile_picture = request.files['profile_picture']
    if profile_picture:
        # Read the file data
        file_data = profile_picture.read()
        # Save the file data into MongoDB using GridFS
        file_id = fs.put(file_data, filename=profile_picture.filename)

    # Now create user_data
    user_data = {
        'name': name,
        'address': address,
        'email': email,
        'contact_number': contact_number,
        'birthday': birthday,
        'degree': degree,
        'university': university,
        'social_media': {
            'github': social_media_github,
            'linkedin': social_media_linkedin,
        },
        'skills': skills,
        'technologies': technologies,
        'work_experiences': work_experiences,
        'user_description': user_description,
    }

    # If profile_picture is available, add it to user_data
    if profile_picture:
        user_data['profile_picture_id'] = file_id

    # Save data to MongoDB
    collection.insert_one(user_data)

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
