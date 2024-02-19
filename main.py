import io
from flask import Flask, render_template, request, redirect,send_file,url_for 
from pymongo import MongoClient
from datetime import datetime
from gridfs import GridFS
from bson import Binary
from bson import ObjectId
from gridfs import GridFSBucket


app = Flask(__name__)
client = MongoClient("mongodb+srv://Lasitha:intern-finder@internship-finder.ae6geb5.mongodb.net/")
app.db = client.internFinder

fs = GridFS(app.db)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/company")
def company():
    company = app.db.companies.find({"name":"Yahoo"})
    print(company[0]["name"])
    return render_template("company-profile.html", company=company[0])

@app.route("/company-jobs")
def companyJobs():
    return render_template("company-jobs.html")

@app.route("/company-applications")
def companyApplications():
    return render_template("company-applications.html")

@app.route("/user-registration")
def userRegistration():
    return render_template("user-register.html")

@app.route('/user-signup', methods=['POST'])
def userSignup():
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
    app.db.users.insert_one(user_data)

    return redirect("/")

@app.route("/user-profile/<string:user_id>")
def userProfile(user_id):
    users = app.db.users.find_one({"_id": ObjectId(user_id)})
    if users:
        user_data = {
            "name": users["name"],
            "address": users["address"],
            "email": users["email"],
            "contact_number": users["contact_number"],
            "birthday": users["birthday"].strftime("%Y-%m-%d"),
            "degree": users["degree"],
            "university": users["university"],
            "social_media_github": users["social_media"]["github"],
            "social_media_linkedin": users["social_media"]["linkedin"],
            "skills": users["skills"],
            "technologies": ", ".join(users["technologies"]),
            "work_experiences": users["work_experiences"],
            "user_description": users["user_description"],
            "profile_picture_id": users["profile_picture_id"],
        }
        return render_template("user_profile.html", user=user_data)
    else:
        # Handle case when user is not found
        return "User not found"
    
@app.route("/photo/<string:photo_id>")
def get_photo(photo_id):
    fs = GridFSBucket(app.db)
    photo_data = fs.open_download_stream(ObjectId(photo_id)).read()
    if photo_data:
        return send_file(io.BytesIO(photo_data), mimetype='image/jpeg')
    else:
        return "Photo not found"