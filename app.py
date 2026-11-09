import os
import re
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-before-deployment")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

CSRFProtect(app)

CONTACT_EMAIL = "ompujhari.digital@gmail.com"


def send_contact_email(name, email, service, message):
    """Send an enquiry to the studio inbox using SMTP environment variables."""
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_APP_PASSWORD")

    if not smtp_user or not smtp_password:
        raise RuntimeError("Email delivery is not configured yet.")

    msg = EmailMessage()
    msg["Subject"] = f"New OP Digital Studio enquiry — {service}"
    msg["From"] = smtp_user
    msg["To"] = CONTACT_EMAIL
    msg["Reply-To"] = email
    msg.set_content(
        f"New project enquiry from the OP Digital Studio website\\n\\n"
        f"Name: {name}\\nEmail: {email}\\nService: {service}\\n\\n"
        f"Message:\\n{message}\\n"
    )

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.is_secure or os.getenv("FLASK_ENV") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.route("/")
def home():
    return render_template("index.html", contact_email=CONTACT_EMAIL)


@app.route("/contact", methods=["POST"])
def contact():
    # Honeypot field: silently ignore simple bot submissions.
    if request.form.get("website", "").strip():
        return redirect(url_for("home") + "#contact")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    service = request.form.get("service", "General enquiry").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please complete your name, email and message.", "error")
        return redirect(url_for("home") + "#contact")

    if len(name) > 100 or len(email) > 254 or len(message) > 4000:
        flash("One of the fields is too long. Please shorten it and try again.", "error")
        return redirect(url_for("home") + "#contact")

    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("home") + "#contact")

    try:
        send_contact_email(name, email, service, message)
        flash("Thanks! Your enquiry has been emailed to our studio. We'll get back to you soon.", "success")
    except Exception:
        app.logger.exception("Contact email could not be delivered")
        flash(
            "The form is ready, but email delivery is not configured yet. "
            "Please use the email link below for now.",
            "error"
        )

    return redirect(url_for("home") + "#contact")


@app.errorhandler(404)
def not_found(_error):
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
