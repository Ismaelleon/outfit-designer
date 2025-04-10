import os, requests, json
from flask import session, redirect
from jinja2 import Environment, FileSystemLoader

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

    payload = {
        "from": {
            "email": os.environ["MAIL_DEFAULT_SENDER"],
            "name": "Outfit Designer"
        },
        "to": [
            { "email": email }
        ],
        "subject": "Activate your account",
        "html": final_html
    }

    headers = {
        "Authorization": "Bearer {}".format(os.environ["MAIL_API_TOKEN"]),
        "Content-Type": "application/json"
    }

    try:
        res = requests.request("POST", os.environ["MAIL_API_URL"], headers=headers, json=payload)

        if res.status_code != 200:
            print("Failed to send email:", res.reason)
    except Exception as e:
        print("Exception during email sending:", str(e))
