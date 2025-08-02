import re, bcrypt
from flaskr.extensions import mongo
from flaskr.helpers import send_verification_mail, dark_mode
from flask import render_template, request, make_response, session, redirect, g, Blueprint

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/sign-up")
def sign_up ():
    # Get user data
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    # Check for input lengths
    if len(name) < 4 or len(email) < 8 or len(password) < 4:
        data = {
            "input-error": True,
            "name": name,
            "email": email,
            "password": password,
        }
        return render_template("components/signup-form.html", data=data)

    # Check for user with same e-mail
    result = mongo.db.users.find_one({ "email": email })

    if result != None:
        data = {
            "email-error": True,
            "name": name,
            "email": email,
            "password": password,
        }
        return render_template("components/signup-form.html", data=data)

    # Encrypt password
    hashed_password = bcrypt.hashpw(password.encode("ascii"), bcrypt.gensalt()).decode("ascii")

    # Save new user
    new_user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "closet": [],
        "outfits": [],
        "activation": {
            "activated": False,
            "code": secrets.token_urlsafe(16)
        }
    }

    result = mongo.db.users.insert_one(new_user)
    
    send_verification_mail(email, new_user["activation"]["code"], app)

    if result.acknowledged == False:
        return make_response({"message": "Internal Server Error"}, 500)

    # Create user session
    session["id"] = str(result.inserted_id)

    # Redirect user to outfits page
    res = make_response({"message": "OK"}, 200)
    res.headers["HX-Redirect"] = "/outfits"
    return res 

@bp.route("/log-in", methods=["POST"])
def log_in ():
    # Get user data
    email = request.form["email"]
    password = request.form["password"]

    # Check for input lengths
    if len(email) < 8 or len(password) < 4:
        data = {
            "input-error": True,
            "email": email,
            "password": password,
        }
        return render_template("components/login-form.html", data=data)

    # Search for user matching email address
    result = mongo.db.users.find_one({ "email": re.compile(email, re.IGNORECASE) })

    if result == None:
        return make_response({"message": "Not Found"}, 404)

    # Check if password doesn"t match
    if not bcrypt.checkpw(password.encode("ascii"), result["password"].encode("ascii")):
        data = {
            "password-error": True,
            "email": email,
            "password": password,
        }
        return render_template("components/login-form.html", data=data)

    # Create user session
    session["id"] = str(result["_id"])

    # Redirect user to outfits page
    res = make_response({"message": "OK"}, 200)
    res.headers["HX-Redirect"] = "/outfits"
    return res

@bp.route("/activate/<string:activation_code>")
def activate_account(activation_code):
    # Find user with same activation code
    user = mongo.db.users.find_one({ "activation": { "activated": False, "code": activation_code } })

    if user == None:
        return redirect("/")

    updated_activation = {
        "activation": {
            "activated": True
        }
    }
    result = mongo.db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": updated_activation})

    return redirect("/outfits?activated=true")


@bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    # Get user e-mail
    email = request.form["email"]

    # Show an error if the e-mail is shorter than 3 characters
    # or if there's not a user with the e-mail received
    user = mongo.db.users.find_one({ "email": email })
    if len(email) < 3 or user == None:
        data = dark_mode({"error": True, "email": email}, request.cookies)
        return render_template("components/forgot-password-form.html", data=data)

    # Generate a password reset code for the user with the e-mail
    reset_code = {
        "code": secrets.token_urlsafe(16), # Save a random url-safe token
        "user_id": user["_id"], # Save the user id
        "expiresAt": datetime.datetime.utcnow() + datetime.timedelta(hours=24) # Make the reset code expire after 24 hours
    }

    # Save the reset code
    mongo.db.reset_codes.insert_one(reset_code)

    # Open password reset mail file
    env = Environment(loader=FileSystemLoader("./views"))
    template = env.get_template("password-reset-mail.html")

    # Run jinja2 on template
    data = {
        "reset_code": reset_code["code"],
        "APP_URL": os.environ["APP_URL"]
    }
    final_html = template.render(data=data)

    # Send password-reset e-mail
    try:
        # Init flask mail
        mail = Mail(app)

        msg = Message(
            sender=os.environ["MAIL_DEFAULT_SENDER"],
            subject="Reset your password",
            recipients=[email],
            html=final_html
        )

        mail.send(msg)

        data = dark_mode({"success": True, "error": False, "email": email}, request.cookies)
        return render_template("components/forgot-password-form.html", data=data)
    except Exception as error:
        return f"Failed to send email: {error}"

@bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        # Get the reset code from url and pass it to the template
        reset_code = request.args.get("reset_code")
        data = dark_mode({"reset_code": reset_code}, request.cookies)

        return render_template("reset-password.html", data=data)
    elif request.method == "POST":
        # Get the reset code from the request body 
        reset_code = request.form["reset_code"] 

        # Check if reset code is not present in body 
        if reset_code == None:
            data = dark_mode({"error": True, "reset_code": reset_code}, request.cookies)
            return render_template("reset-password.html", data=data)

        # Find the user id
        reset_code_doc = mongo.db.reset_codes.find_one({"code": reset_code})

        # Check if reset code exists in db
        if reset_code_doc == None:
            data = dark_mode({"error": True, "reset_code": reset_code}, request.cookies)
            return render_template("reset-password.html", data=data)

        user_id = reset_code_doc["user_id"]

        # Get the new password
        password = request.form["password"]
        password_confirm = request.form["confirm-password"]

        # Check that new password matches the confirmation
        if password != password_confirm:
            data = dark_mode({"input-error": True, "reset_code": reset_code}, request.cookies)
            return render_template("reset-password.html", data=data)

        # Hash the new password
        hashed_password = bcrypt.hashpw(password.encode("ascii"), bcrypt.gensalt()).decode("ascii")

        # Update the user document
        result = mongo.db.users.update_one({"_id": user_id}, {"$set": {"password": hashed_password}})

        # Remove the reset code from db
        mongo.db.reset_codes.delete_one(reset_code_doc)

        res = make_response({"message": "OK"}, 200)
        res.headers["HX-Redirect"] = "/"
        return res

@bp.route("/log-out", methods=["POST"])
def log_out ():
    if session.get("id"):
        # Remove user session
        session.pop("id", None)

        # Redirect user to index page
        res = make_response({ "message": "OK" }, 200)
        res.headers["HX-Redirect"] = "/"
        return res
