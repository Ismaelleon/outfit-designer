import os, requests, uuid, cloudinary.utils, cloudinary.uploader
import webcolors
from PIL import Image
from io import BytesIO
from rembg import remove, new_session
from werkzeug.utils import secure_filename
from flask import session, redirect
from jinja2 import Environment, FileSystemLoader
from colorthief import ColorThief

# create a rembg session once insetad of per every request
rembg_session = new_session("u2netp")  # smaller model (uses ~5mb)


def dark_mode(data, cookies):
    if "dark-mode" in cookies and cookies["dark-mode"] == "true":
        data["dark-mode"] = True

    return data


def handle_invalid_user_session():
    session.clear()
    return redirect("/")


def validate_outfit_form(request):
    # If required fields are not added show error
    errors = []
    required_fields = {
        "name": lambda: request.form.get("name", "").strip(),
        "season": lambda: request.form.get("season", "").strip(),
        "clothes": lambda: request.form.getlist("clothes"),
    }

    # If outfits uses an image, add it to the required fields
    if "use-image" in request.form:
        required_fields["image"] = lambda: request.files.get("image")

    # Check for field in request body, if not present, add field to errors list
    for field, getter in required_fields.items():
        field_value = getter()
        if not field_value:
            errors.append(field)

    return errors


def send_verification_mail(email, activation_code, app):
    # Open verification mail file
    env = Environment(loader=FileSystemLoader("./flaskr/views"))
    template = env.get_template("verification-mail.html")

    # Run jinja2 on template
    data = {"activation_code": activation_code, "APP_URL": os.environ["APP_URL"]}
    final_html = template.render(data=data)

    payload = {
        "from": {"email": os.environ["MAIL_DEFAULT_SENDER"], "name": "Outfit Designer"},
        "to": [{"email": email}],
        "subject": "Activate your account",
        "html": final_html,
    }

    headers = {
        "Authorization": "Bearer {}".format(os.environ["MAIL_API_TOKEN"]),
        "Content-Type": "application/json",
    }

    try:
        res = requests.request(
            "POST", os.environ["MAIL_API_URL"], headers=headers, json=payload
        )

        if res.status_code != 200:
            print("Failed to send email:", res.reason)
    except Exception as e:
        print("Exception during email sending:", str(e))


def upload_image(folder, image_file, app, remove_background, get_dominant_colors=False):
    # Save image file
    image_filename = secure_filename(str(uuid.uuid4()))
    image_file_path = os.path.join(
        os.getcwd(), app.config["UPLOAD_FOLDER"], image_filename
    )

    # If image has no filename to extract the extension
    if not hasattr(image_file, "filename"):
        # Save as png
        image_file.save(image_file_path, "PNG")
    else:
        # Otherwise save with original extension
        image_file.save(image_file_path)

    # Remove image background
    if remove_background:
        with open(image_file_path, "rb") as f:
            image_file = f.read()

        image_bg_removed = remove(image_file, session=rembg_session)

        with open(image_file_path, "wb") as f:
            f.write(image_bg_removed)

    # Scale image (max width or height 500px) for better upload time
    img = Image.open(image_file_path)
    img.thumbnail((500, 500))
    img.save(image_file_path, img.format, quality=100)

    if get_dominant_colors:
        color_thief = ColorThief(image_file_path)

        dominant_colors = color_thief.get_palette(color_count=2)

        # Convert color from rgb to text
        for index, color in enumerate(dominant_colors):
            try:
                # Try translating rgb to color name
                dominant_colors[index] = webcolors.rgb_to_name(color)
            except:
                min_colors = {}

                # Get nearest color on the HTML4 specification
                for name in webcolors.names("html4"):
                    key = webcolors.name_to_hex(name)

                    r, g, b = webcolors.hex_to_rgb(key)

                    red_distance = (r - color[0]) ** 2
                    green_distance = (g - color[1]) ** 2
                    blue_distance = (b - color[2]) ** 2

                    key_ = red_distance + green_distance + blue_distance
                    min_colors[key_] = name

                dominant_colors[index] = min_colors[min(min_colors.keys())]

        # Remove repeated colors
        dominant_colors = set(dominant_colors)

        # Convert back into list (mongodb's bson does not support sets)
        dominant_colors = list(dominant_colors)

        # Sort colors alphabetically
        dominant_colors.sort()

    # Upload image to cloudinary
    result = cloudinary.uploader.upload(
        image_file_path, public_id=image_filename, overwrite=False, folder=folder
    )
    image_src = result["secure_url"]

    # Delete image file
    os.remove(image_file_path)

    if get_dominant_colors:
        return image_src, dominant_colors

    return image_src


def generate_outfit_image(clothes):
    # Clothing position by type
    y_position = {
        "cap": 0,
        "coat": 85,
        "dress": 85,
        "hoodies": 85,
        "jacket": 85,
        "pants": 255,
        "shoes": 425,
        "shorts": 255,
        "shirt": 85,
        "skirt": 255,
        "sweater": 85,
        "tie": 85,
        "t-shirt": 85,
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

        if clothing_item["type"] == "shoes" or clothing_item["type"] == "cap":
            height = 85

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
