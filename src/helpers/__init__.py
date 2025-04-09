import smtplib, os, http.client, json
from flask import session, redirect
from jinja2 import Template, Environment, FileSystemLoader

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

    conn = http.client.HTTPSConnection(os.environ["MAIL_SERVER"])

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
    payload = json.dumps(payload)

    headers = {
        "Accept": "application/json",
        "Api-Token": os.environ["MAIL_API_TOKEN"],
        "Content-Type": "application/json"
    }

    conn.request("POST", "/api/send/{}".format(os.environ["MAIL_INBOX_ID"]), payload, headers)

    res = conn.getresponse()

    if res != 200:
        print(res.reason)
