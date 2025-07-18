import os, requests, uuid, cloudinary.uploader
from PIL import Image
from rembg import remove
from werkzeug.utils import secure_filename
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

def upload_image(folder, image_file, app):
    # Save image file
    image_filename = secure_filename(str(uuid.uuid4()))
    image_file_path = os.path.join(os.getcwd(), app.config["UPLOAD_FOLDER"], image_filename)
    image_file.save(image_file_path)

    # Remove image background
    image_file = open(image_file_path, "rb").read()
    image_bg_removed = remove(image_file)
    image_file = open(image_file_path, "wb")
    image_file.write(image_bg_removed)

    # Scale image (max width or height 500px) for better upload time
    img = Image.open(image_file_path)
    img.thumbnail((500, 500))
    img.save(image_file_path, img.format, quality=100)

    # Upload image to cloudinary
    result = cloudinary.uploader.upload(image_file_path, public_id=image_filename, overwrite=False, folder=folder)
    image_src = result["secure_url"]

    # Delete image file
    os.remove(image_file_path)

    return image_src
