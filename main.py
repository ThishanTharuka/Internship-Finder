import io
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from pymongo import MongoClient
from datetime import datetime
from gridfs import GridFS, GridFSBucket
from bson import Binary, ObjectId

app = Flask(__name__)
client = MongoClient("mongodb+srv://Lasitha:intern-finder@internship-finder.ae6geb5.mongodb.net/")
app.db = client.internFinder;

app.secret_key = "DfhfpXFk3D4WlOM7k7RtPg"

fs = GridFS(app.db)


@app.route('/getid')
def getId():
    session_email = session.get('email')
    
    if session_email is not None:
        if session['type'] == 'user':
            session["user_id"] = str(app.db.users.find_one({"email": session_email})['_id'])
        elif session['type'] == 'company':
            session["user_id"] = str(app.db.companies.find_one({"email": session_email})['_id'])
        else:
            print("no session values")





@app.route("/")
def home():
    
    getId()
    if session["user_id"] and session.get('type') == 'user':
        return redirect(f"/user-profile/{session.get('user_id')}")
    elif session["user_id"] and session.get('type') == 'company':
        return redirect("/company")
    else:
        return render_template("home.html")

@app.route("/company")
def company():
    company = app.db.companies.find_one({"email": session.get('email')})
    print(company.get('name'))
    return render_template("company-profile.html", company=company)

@app.route("/company-jobs")
def companyJobs():
    company = app.db.companies.find_one({"email": session.get('email')})
    jobs = app.db.jobs.find({"owner_id": session.get('user_id')})
    return render_template("company-jobs.html",  company=company, jobs=jobs)

@app.route("/company-applications")
def companyApplications():
    company = app.db.companies.find_one({"email": session.get('email')})
    jobs = app.db.jobs.find({"owner_id": session.get('user_id')})

    applications = []

    for job in jobs:
        if len(job["applicants"]) > 0:
            job["num_of_app"] = len(job["applicants"])
            job["job_id"] = str(job["_id"])
            applications.append(job) 
    
    print(applications)

    return render_template("company-applications.html", company=company, applications=applications)

@app.route("/view-applicants/<string:job_id>")
def viewApplicants(job_id):

    ids = app.db.jobs.find_one({"_id": ObjectId(job_id)}).get('applicants')

    applicants = []

    for id in ids:
        applicants.append(app.db.users.find_one({"_id": ObjectId(id)}))

    print(applicants)

    return render_template("company-view-applicants.html", applicants=applicants)

@app.route("/view-user/<string:user_id>")
def viewUser(user_id):
    user = app.db.users.find_one({"_id": ObjectId(user_id)})
    return render_template("company-view-user.html", user=user)

@app.route("/user-registration")
def userRegistration():
    return render_template("user-register.html")

@app.route('/user-signup', methods=['POST'])
def userSignup():
    name = request.form.get('name')
    address = request.form.get('address')
    email = request.form.get('email')
    password = request.form.get('password')
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
        'password': password,
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

    session["email"] = email
    session["type"] = "user"

    return redirect("/")


# @app.route("/user-profile")
# def userProfile():
#     return render_template("user-profile.html", user={})

@app.route("/user-profile/<string:user_id>")
def userProfile(user_id):
    users = app.db.users.find_one({"_id": ObjectId(user_id)})
    if users:
        user_data = {
            "_id": session.get('user_id'),
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
        return render_template("user-profile.html", user=user_data)
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


@app.route("/user-recomendations")
def userRecomendations():

    users = app.db.users.find_one({"_id": ObjectId(session.get('user_id'))})
    if users:
        user_data = {
            "_id": session.get('user_id'),
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

    recomandations = []
    jobs = app.db.jobs.find({})

    for job in jobs:
        eligible = True
        for skill in job.get('skills'):
            if not skill in users.get('technologies'):
                eligible = False
                break
        
        if eligible:
            owner = app.db.companies.find_one({"_id": ObjectId(job.get('owner_id'))})
            job["owner_name"] = owner.get('name')
            job["profile_picture_id"] = owner["profile_picture_id"]
            job["job_id"] = str(job["_id"])
            recomandations.append(job)

    print(recomandations)
    return render_template("user-recomandations.html", user=user_data, recomandations=recomandations)

@app.route("/apply-job/<string:job_id>")
def applyJob(job_id):
    job = app.db.jobs.find_one({"_id": ObjectId(job_id)})
    applications_list = job.get('applicants')
    applications_list.append(session.get('user_id'))

    app.db.jobs.update_one({"_id":ObjectId(job_id)}, {"$set":{"applicants":applications_list}})

    return redirect("/user-recomendations")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():

    email = request.form.get('username')
    password = request.form.get('password')

    user_doc = app.db.users.find_one({"email": email})
    company_doc = app.db.companies.find_one({"email": email})


    if user_doc is not None and password == user_doc.get("password"):
        session["email"] = email
        session["type"] = "user"
        session["user_id"] = None
        return redirect("/")
    elif company_doc is not None and password == company_doc.get("password"):
        session["email"] = email
        session["type"] = "company"
        session["user_id"] = None
        return redirect("/")
    else:
        print("wrong email and password")
        return render_template("login.html")

    return render_template("login.html")



@app.route("/company-registration")
def companyRegistration():
    return render_template("company-register.html")

@app.route('/company-signup', methods=['POST'])
def companySignup():
    name = request.form.get('name')
    website = request.form.get('website')
    email = request.form.get('email')
    password = request.form.get('password')
    founded = request.form.get('founded')
    size = request.form.get('size')
    industry = request.form.get('industry')
    company_type = request.form.get('company_type')
    description = request.form.get('description')

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
        'website': website,
        'email': email,
        'password': password,
        'founded': founded,
        'size': size,
        'industry': industry,
        'company_type': company_type,
        'description': description,
    }

    # If profile_picture is available, add it to user_data
    if profile_picture:
        user_data['profile_picture_id'] = file_id

    # Save data to MongoDB
    app.db.companies.insert_one(user_data)

    session["email"] = email
    session["type"] = "company"

    return redirect("/")

@app.route("/add-new-job")
def addNewJob():
    return render_template('add-job.html')

@app.route("/job-register", methods=['POST'])
def jobRegister():
    title = request.form.get('title')
    location = request.form.get('location')
    salary = request.form.get('salary')
    discription = request.form.get('discription')
    responsibilities = request.form.get('responsibilities')
    requirements = request.form.get('requirements')
    owner_id = session.get('user_id')

    # Get technologies as a comma-separated string from the form
    skills_string = request.form.get('skills')

    # Split the string into a list of technologies
    skills = [tech.strip() for tech in skills_string.split(',')]


    # Now create user_data
    job_data = {
        'title': title,
        'location': location,
        'salary': salary,
        'discription': discription,
        'responsibilities': responsibilities,
        'requirements': requirements,
        'skills': skills,
        'owner_id': owner_id,
    }

    # Save data to MongoDB
    app.db.jobs.insert_one(job_data)

    return redirect("/company")


@app.route("/logout")
def logout():
    session.clear()
    session["user_id"] = None
    return redirect("/")