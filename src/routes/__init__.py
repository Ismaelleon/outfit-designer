import os, bcrypt, cloudinary, cloudinary.uploader, datetime, secrets, re
from flask import send_from_directory, render_template, redirect, request, make_response, session
from cloudinary import CloudinaryImage
from jinja2 import Environment, FileSystemLoader
from bson.objectid import ObjectId
from helpers import dark_mode, send_verification_mail, handle_invalid_user_session, upload_image
from flask_mail import Mail, Message

def setup_router (app, mongo):
    # Static files
    @app.route("/static/<path:file_path>")
    def static_files (file_path):
        return send_from_directory("static", file_path)

    @app.route("/")
    def index ():
        # If user logged in, redirect to outfits page 
        if session.get("id"):
            return redirect("/outfits")

        data = dark_mode({}, request.cookies)
        return render_template("index.html", data={})

    @app.route("/outfits")
    def outfits ():
        # If user logged in render template
        if session.get("id"):
            # Get user document 
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            outfits = user["outfits"]

            # Get the "activated" url param, to show a banner letting the user know that the account is activated
            just_activated = request.args.get("activated")

            if just_activated != "true":
                just_activated = False
            else:
                just_activated = True

            data = dark_mode({
                "outfits": outfits,
                "just_activated": just_activated,
                "activated": user["activation"]["activated"]
            }, request.cookies)
            return render_template("outfits.html", data=data)

        # Otherwise, redirect to the home page
        return redirect("/")

    @app.route("/outfits/<string:outfit_id>")
    def outfit (outfit_id):
        # If user is logged in
        if session.get("id"):
            # Get user data
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            # Find outfit
            outfit = {}
            for outfit in user["outfits"]:
                if str(outfit["_id"]) == outfit_id:
                    outfit = outfit 
                    break

            # Get outfit clothes
            for index, clothing_id in enumerate(outfit["clothes"]):
                for clothing_item in user["closet"]:
                    if str(clothing_item["_id"]) == clothing_id:
                        outfit["clothes"][index] = clothing_item 

            data = dark_mode({
                "outfit": outfit,
                "activated": user["activation"]["activated"],
            }, request.cookies)
            return render_template("outfit.html", data=data)

    @app.route("/outfits/edit/<string:outfit_id>", methods=["GET", "POST"])
    def edit_outfit(outfit_id):
        if request.method == "POST":
            # If user not logged in
            if not session.get("id"):
                res = make_response({"message": "Unauthorized"}, 401)
                res.headers["HX-Redirect"] = "/outfits"
                return res

            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

        # If user logged in render template
        if session.get("id"):
            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            # Find outfit
            outfit = {}
            for outfit in user["outfits"]:
                if str(outfit["_id"]) == outfit_id:
                    outfit = outfit 
                    break

            data = dark_mode({
                "name": outfit["name"],
                "season": outfit["season"],
                "image": outfit["image"],
                "clothes": outfit["clothes"],
                "closet": user["closet"],
                "activated": user["activation"]["activated"],
            }, request.cookies)
            return render_template("edit-outfit.html", data=data)

        # Otherwise, redirect to the home page
        return redirect("/")

    @app.route("/outfits/new", methods=["POST", "GET"])
    def create_outfit ():
        if request.method == "POST":
            # If user not logged in
            if not session.get("id"):
                res = make_response({"message": "Unauthorized"}, 401)
                res.headers["HX-Redirect"] = "/outfits"
                return res

            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            # If required properties not added
            if "name" not in request.form or "season" not in request.form or "image" not in request.files:
                data = dark_mode({
                    "closet": user["closet"],
                    "error": True,
                    "activated": user["activation"]["activated"],
                    "name": request.form["name"],
                    "season": request.form["season"],
                }, request.cookies)
                return render_template("create-outfit.html", data=data)

            # Get request body 
            name = request.form["name"]
            season = request.form["season"]
            clothes = request.form.getlist("clothes")
            image_file = request.files["image"]

            # If user does not select a file or some inputs are not valid
            if image_file.filename == "" or name == "":
                pass

            # Upload image to cloudinary
            image_src = upload_image(os.environ["CLOUDINARY_OUTFITS_FOLDER"], image_file, app)

            # Update closet array 
            outfits = user["outfits"]
            new_outfit_id = ObjectId()
            outfits.append({
                "_id": new_outfit_id,
                "name": name,
                "season": season,
                "image": image_src,
                "clothes": clothes,
                "created": datetime.datetime.now().strftime("%d/%m/%y"),
            })

            # Update document with updated closet array
            result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"outfits": outfits}})
            
            res = make_response({"message": "OK"}, 200)
            res.headers["HX-Redirect"] = f"/outfits/{new_outfit_id}?redirect"
            return res
        elif request.method == "GET":
            # If user logged in render template
            if session.get("id"):
                # Get user document
                user_id = session.get("id")
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

                if user == None:
                    return handle_invalid_user_session()

                data = dark_mode({
                    "closet": user["closet"],
                    "activated": user["activation"]["activated"],
                }, request.cookies)
                return render_template("create-outfit.html", data=data)

            # Otherwise, redirect to the home page
            return redirect("/")

    @app.route("/outfits/filter", methods=["POST"])
    def filter_outfits ():
        if request.method == "POST":
            if session.get("id"):
                # Get user document
                user_id = session.get("id")
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

                if user == None:
                    return handle_invalid_user_session()

                # Get request body
                clothes = request.form["clothes"] 
                season = request.form["season"]

                # Filter outfits by clothes and season
                filtered_outfits = []
                for outfit in user["outfits"]:
                    if (
                        (int(clothes) == 0 or int(clothes) == len(outfit["clothes"])) and
                        (season == "all" or season == outfit["season"])
                    ):
                        filtered_outfits.append(outfit)

                data = dark_mode({
                    "outfits": filtered_outfits,
                    "activated": user["activation"]["activated"],
                }, request.cookies)
                return render_template("components/outfit.html", data=data)


    @app.route("/outfits/delete/<string:outfit_id>", methods=["DELETE"])
    def delete_outfits (outfit_id):
        if request.method == "DELETE":
            if session.get("id"):
                # Get user document
                user_id = session.get("id")
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

                if user == None:
                    return handle_invalid_user_session()

                # Remove outfits from outfits list 
                outfits = user["outfits"]
                for outfit in outfits:
                    if str(outfit["_id"]) == outfit_id:
                        # Remove image from cloudinary
                        image_public_id = outfit["image"].split("/")[-1].split(".")[0]
                        cloudinary.uploader.destroy(os.path.join(os.environ["CLOUDINARY_OUTFITS_FOLDER"], image_public_id))

                        outfits.remove(outfit)

                # Save updated outfits 
                result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"outfits": outfits}})

                # Return outfits html
                data = dark_mode({
                    "outfits": outfits,
                    "activated": user["activation"]["activated"],
                }, request.cookies)
                return render_template("components/outfit.html", data=data)

    @app.route("/closet")
    def closet ():
        # If user logged in render template
        if session.get("id"):
            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            data = dark_mode({
                "closet": user["closet"],
                "activated": user["activation"]["activated"],
            }, request.cookies)
            return render_template("closet.html", data=data)

        # Otherwise, redirect to the home page
        return redirect("/")

    @app.route("/closet/<string:clothing_id>")
    def clothing (clothing_id):
        # If user is logged in
        if session.get("id"):
            # Get user data
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            # Find clothing item
            clothing_item = {}
            for clothing_item in user["closet"]:
                if str(clothing_item["_id"]) == clothing_id:
                    clothing_item = clothing_item
                    break

            data = dark_mode({
                "clothing_item": clothing_item,
                "activated": user["activation"]["activated"]
            }, request.cookies)
            return render_template("closet-item.html", data=data)

    @app.route("/closet/new", methods=["POST", "GET"])
    def add_clothes ():
        if request.method == "POST":
            # If user not logged in
            if not session.get("id"):
                res = make_response({"message": "Unauthorized"}, 401)
                res.headers["HX-Redirect"] = "/outfits"
                return res

            # Get user data
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            # If required properties not added
            if "name" not in request.form or "type" not in request.form or "color" not in request.form or "image" not in request.files:

                data = dark_mode({ 
                    "error": True,
                    "activated": user["activation"]["activated"],
                    "name": request.form["name"],
                    "type": request.form["type"],
                    "brand": request.form["brand"],
                    "colors": request.form.getlist("color"),
                }, request.cookies)
                return render_template("add-clothes.html", data=data)

            # Get request body 
            name = request.form["name"]
            clothing_type = request.form["type"]
            brand = request.form["brand"]
            colors = request.form.getlist("color")
            image_file = request.files["image"]

            # If user does not select a file
            if image_file.filename == "":
                data = dark_mode({ 
                    "error": True,
                    "activated": user["activation"]["activated"],
                    "name": name,
                    "type": clothing_type,
                    "brand": brand,
                    "colors": colors,
                }, request.cookies)
                return render_template("add-clothes.html", data=data)

            # Upload image to cloudinary
            image_src = upload_image(os.environ["CLOUDINARY_CLOSET_FOLDER"], image_file, app)

            # Update closet array 
            closet = user["closet"]
            new_clothing_id = ObjectId()
            closet.append({
                "_id": new_clothing_id,
                "name": name,
                "type": clothing_type,
                "brand": brand,
                "colors": colors,
                "image": image_src 
            })

            # Update document with updated closet array
            result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"closet": closet}})
            
            res = make_response({"message": "OK"}, 200)
            res.headers["HX-Redirect"] = f"/closet/{new_clothing_id}?redirect"
            return res

        # If user logged in render template
        if session.get("id"):
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            data = dark_mode({
                "error": False,
                "activated": user["activation"]["activated"],
            }, request.cookies)
            return render_template("add-clothes.html", data=data)

        # Otherwise, redirect to the home page
        return redirect("/")

    @app.route("/closet/filter", methods=["POST"])
    def filter_clothes ():
        if request.method == "POST":
            if session.get("id"):
                # Get user document
                user_id = session.get("id")
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

                if user == None:
                    return handle_invalid_user_session()

                # Get request body
                clothing_type = request.form["type"] 
                brand = request.form["brand"]
                colors = []
                if "color" in request.form:
                    colors = request.form.getlist("color")

                # Filter clothes by type, brand, and colors 
                filtered_clothes = []
                for clothing_item in user["closet"]:
                    if (
                        (clothing_type == "all" or clothing_type == clothing_item["type"]) and 
                        (brand == "" or brand.lower() == clothing_item["brand"].lower()) and
                        (len(colors) == 0 or sorted(colors) == sorted(clothing_item["colors"]))
                    ):
                        filtered_clothes.append(clothing_item)

                data = dark_mode({
                    "closet": filtered_clothes,
                    "activated": user["activation"]["activated"],
                }, request.cookies)
                return render_template("components/clothing-item.html", data=data)

    @app.route("/closet/delete/<string:clothing_id>", methods=["DELETE"])
    def delete_clothes (clothing_id):
        if request.method == "DELETE":
            if session.get("id"):
                # Get user document
                user_id = session.get("id")
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

                if user == None:
                    return handle_invalid_user_session()

                # Remove outfits using this clothing item
                outfits = user["outfits"]
                for outfit in outfits:
                    for clothing_item in outfit["clothes"]:
                        if clothing_item == clothing_id:
                            outfits.remove(outfit)

                # Remove clothes from closet list 
                closet = user["closet"]
                for item in closet:
                    if str(item["_id"]) == clothing_id:
                        # Remove image from cloudinary
                        image_public_id = item["image"].split("/")[-1].split(".")[0]
                        cloudinary.uploader.destroy(os.path.join(os.environ["CLOUDINARY_CLOSET_FOLDER"], image_public_id))
                        closet.remove(item)

                # Save updated closet
                result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"closet": closet, "outfits": outfits}})

                # Return closet html
                data = dark_mode({
                    "closet": closet,
                    "activated": user["activation"]["activated"],
                }, request.cookies)
                return render_template("components/clothing-item.html", data=data)

    @app.route("/profile")
    def profile ():
        # If user logged in render template
        if session.get("id"):
            # Get user document 
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session() 

            data = dark_mode({
                "user": user,
                "activated": user["activation"]["activated"],
            }, request.cookies)
            return render_template("profile.html", data=data)

        return redirect("/")

    @app.route("/settings", methods=["GET", "POST"])
    def settings ():
        # If user logged in render template
        if session.get("id"):
            # Get user document 
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if user == None:
                return handle_invalid_user_session()

            data = dark_mode({
                "user": user,
                "activated": user["activation"]["activated"],
                "modal-hidden": True,
            }, request.cookies)
            return render_template("settings.html", data=data)

        return redirect("/")

    @app.route("/sign-up", methods=["POST"])
    def sign_up ():
        if request.method == "POST":
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

    @app.route("/activate/<string:activation_code>", methods=["GET"])
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


    @app.route("/log-in", methods=["POST"])
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

    @app.route("/forgot-password", methods=["POST"])
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

    @app.route("/reset-password", methods=["GET", "POST"])
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

    @app.route("/account/delete", methods=["DELETE"])
    def delete_account():
        if session.get("id"):
            # Get user document 
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            # Get password form value
            password = request.form["password"]

            # Check if passwords match
            if bcrypt.checkpw(password.encode("ascii"), user["password"].encode("ascii")):
                # If password is valid, delete the account
                mongo.db.users.delete_one(user)

                # Remove the session
                session.pop("id", None)

                # Redirect user to /
                res = make_response({ "message": "OK" }, 200)
                res.headers["HX-Redirect"] = "/"
                return res

            # If passwords do not match, return delete-account component
            data = dark_mode({"error": True, "modal-hidden": False, "password": password}, request.cookies)
            return render_template("components/delete-account.html", data=data)

    @app.route("/log-out", methods=["POST"])
    def log_out ():
        if session.get("id"):
            # Remove user session
            session.pop("id", None)

            # Redirect user to index page
            res = make_response({ "message": "OK" }, 200)
            res.headers["HX-Redirect"] = "/"
            return res
