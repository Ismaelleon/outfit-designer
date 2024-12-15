import smtplib, os
from email.mime.text import MIMEText
from jinja2 import Template, Environment, FileSystemLoader

def dark_mode(data, cookies):
    if "dark-mode" in cookies and cookies["dark-mode"] == "true":
        data["dark-mode"] = True

    return data

def send_verification_mail(email, activation_code):
    # Open verification mail file
    env = Environment(loader=FileSystemLoader("./views"))
    template = env.get_template("verification-mail.html")

    # Run jinja2 on template
    data = {
        "activation_code": activation_code,
        "APP_URL": os.environ["APP_URL"]
    }
    final_html = template.render(data=data)

    message = MIMEText(final_html, "html")
    message["Subject"] = "Activate your account"
    message["From"] = "example@outfit-designer.com"
    message["To"] = email

    s = smtplib.SMTP(os.environ["MAILTRAP_HOST"], 2525)
    s.starttls()
    s.login(os.environ["MAILTRAP_USER"], os.environ["MAILTRAP_PASSWORD"])
    s.sendmail("example@outfit-designer.com", email, message.as_string())
    s.quit()
