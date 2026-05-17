from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

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

@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route('/admin/members')
def member_management():
    return render_template('admin_members.html')

@app.route('/admin/events')
def manage_events():
    return render_template('admin_events.html')

@app.route('/admin/notifications')
def system_notifications():
    return render_template('admin_notifications.html')

@app.route('/admin/attendance')
def admin_attendance():
    return render_template('admin_attendance.html')

@app.route('/admin/learning-materials')
def admin_learning():
    return render_template('admin_learning.html')

@app.route('/admin/reports')
def admin_reports():
    return render_template('admin_reports.html')

@app.route('/admin/generate-report', methods=['POST'])
def generate_report():
    return "Report is being generated and downloaded..."

@app.route('/admin/ai-helpdesk')
def admin_ai_helpdesk():
    return render_template('admin_ai_helpdesk.html')

if __name__ == "__main__":
    app.run(debug=True)