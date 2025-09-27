import os, requests, uuid, cloudinary.utils, cloudinary.uploader
from PIL import Image
from io import BytesIO
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
    env = Environment(loader=FileSystemLoader("./flaskr/views"))
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
    image_file.save(image_file_path, "PNG")

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

def generate_outfit_image(clothes):
    # Clothing position by type
    y_position = {
        "cap": 0,
        "coat": 170,
        "dress": 170,
        "hoodies": 170,
        "jacket": 170,
        "pants": 170,
        "shoes": 340,
        "shorts": 340,
        "shirt": 170,
        "skirt": 340,
        "sweater": 170,
        "tie": 170,
        "t-shirt": 0,
    }

    images = []

    # Create a blank image for the base
    images.append(Image.new("RGBA", (512, 512), (0, 0, 0, 0)))

    # Get all images data from url
    for clothing_item in clothes:
        image_url = clothing_item["image"]

        # Get image data from url
        res = requests.get(image_url)
        image = Image.open(BytesIO(res.content))

        # Resize image
        height = 170
        width = int((height * image.width) / image.height)
        image = image.resize((width, height))

        # Add to images list
        images.append(image)

    # Combine images
    for i in range(len(clothes)):
        # Calculate the x position of the image
        img = images[i + 1]
        x_position = int(256 - (img.width / 2))

        # Paste the next image over the first one
        images[0].paste(img, (x_position, y_position[clothes[i]["type"]]), img)

    return images[0]
