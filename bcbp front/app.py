from flask import Flask, render_template, request, redirect, flash, session
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "bcbp_secret_key_change_this"

# iProg SMS CONFIG
IPROG_API_TOKEN = "2ce1d87ab317b026eaf5a91f256d63e628e8306c"
IPROG_SMS_URL = "https://www.iprogsms.com/api/v1/sms_messages"


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


# FORGOT PASSWORD
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        phone = request.form.get("phone")

        if not email or not phone:
            flash("Email and phone number are required.")
            return redirect("/forgot_password")

        otp = str(random.randint(100000, 999999))

        session["otp"] = otp
        session["otp_expiry"] = (datetime.now() + timedelta(minutes=5)).isoformat()

        message = f"Your BCBP verification code is {otp}. Valid for 5 minutes."

        payload = {
            "api_token": IPROG_API_TOKEN,
            "phone_number": phone,
            "message": message
        }

        try:
            response = requests.post(
                IPROG_SMS_URL,
                json=payload,
                timeout=15
            )

            if response.status_code in [200, 201]:
                flash("Verification code sent successfully.")
                return redirect("/verify_code")
            else:
                flash("Failed to send SMS.")
                return redirect("/forgot_password")

        except Exception as e:
            flash(f"SMS Error: {str(e)}")
            return redirect("/forgot_password")

    return render_template("forgot_password.html")


# VERIFY CODE
@app.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    if request.method == "POST":
        entered_otp = request.form.get("otp")

        saved_otp = session.get("otp")
        expiry = session.get("otp_expiry")

        if not saved_otp or not expiry:
            flash("Session expired.")
            return redirect("/forgot_password")

        if datetime.now() > datetime.fromisoformat(expiry):
            flash("Verification code expired.")
            return redirect("/forgot_password")

        if entered_otp == saved_otp:
            session["verified"] = True
            return redirect("/reset_password")
        else:
            flash("Invalid verification code.")
            return redirect("/verify_code")

    return render_template("verify_code.html")


# RESET PASSWORD
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if not session.get("verified"):
        flash("Verification required.")
        return redirect("/forgot_password")

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect("/reset_password")

        session.pop("otp", None)
        session.pop("otp_expiry", None)
        session.pop("verified", None)

        return redirect("/reset_success")

    return render_template("reset_password.html")


# RESET SUCCESS
@app.route("/reset_success")
def reset_success():
    return render_template("reset_success.html")


if __name__ == "__main__":
    app.run(debug=True)