from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
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