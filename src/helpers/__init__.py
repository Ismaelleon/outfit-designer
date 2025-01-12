import smtplib, os
from flask import session, redirect
from jinja2 import Template, Environment, FileSystemLoader
from flask_mail import Mail, Message

def dark_mode(data, cookies):
    if "dark-mode" in cookies and cookies["dark-mode"] == "true":
        data["dark-mode"] = True

    return data

def handle_invalid_user_session():
    session.clear()
    return redirect("/")

def send_verification_mail(email, activation_code, app):
    # Open verification mail file
    env = Environment(loader=FileSystemLoader("./views"))
    template = env.get_template("verification-mail.html")

    # Run jinja2 on template
    data = {
        "activation_code": activation_code,
        "APP_URL": os.environ["APP_URL"]
    }
    final_html = template.render(data=data)

    try:
        # Init flask mail
        mail = Mail(app)

        msg = Message(
            sender=os.environ["MAIL_DEFAULT_SENDER"],
            subject="Activate your account",
            recipients=[email],
            html=final_html
        )

        mail.send(msg)
    except Exception as error:
        return f"Failed to send email: {error}"
