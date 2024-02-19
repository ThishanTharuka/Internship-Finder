from flask import Flask, render_template, request



app = Flask(__name__)

@app.route("/user_profile")
def display_user_profile():

    name = "rakshitha kulasara"
    address = "kalubwila" 
    email = "rakshitha@gmail.com"
    contact = "0777 777 777"
    birthday = "1999.09.09"
    degree = "computer science"
    university = "university of kelaniya"
    github = "github.com"
    linkedin = "linkedin.com"
    skills = ["HTML", "CSS", "PYTHON","JAVA"]
    technologies = ["technology01", "technology02", "technology03",]
    expiriences = ["expirience01", "expirience02", "expirience03"]
    profile_pic = "profile.jpg"
    custom_field = "bla blablaa"

    profile = {
    "name" : name,
    "address" : address,
    "email" : email,
    "contact" : contact,
    "birthday" : birthday,
    "degree" : degree,
    "university" : university,
    "github" : github,
    "linkedin" : linkedin,
    "skills": skills,
    "technologies": technologies,
    "expiriences" : expiriences,
    "profile_pic": profile_pic,
    "custom_field" : custom_field,
    
    

    }

    return render_template("profile.html", **profile)


@app.route("/")
def display_profile():
    return render_template("user_profile.html",)