from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb+srv://Lasitha:intern-finder@internship-finder.ae6geb5.mongodb.net/")
app.db = client.internFinder;

@app.route("/")
def home():
    print([e for e in app.db.companies.find({})])
    return render_template("home.html")

@app.route("/company")
def company():
    return render_template("company-profile.html")

@app.route("/company-jobs")
def companyJobs():
    return render_template("company-jobs.html")

@app.route("/company-applications")
def companyApplications():
    return render_template("company-applications.html")