from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/my_events")
def my_events():
    return render_template("my_events.html")

@app.route("/attendance")
def attendance():
    return render_template("attendance.html")

@app.route("/course_materials")
def course_materials():
    return render_template("course_materials.html")

@app.route("/personal_record")
def personal_record():
    return render_template("personal_record.html")

@app.route("/notifications")
def notifications():
    return render_template("notifications.html")

@app.route("/ai_helpdesk")
def ai_helpdesk():
    return render_template("ai_helpdesk.html")

if __name__ == "__main__":
    app.run(debug=True)