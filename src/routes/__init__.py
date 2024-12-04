import os, bcrypt, cloudinary, cloudinary.uploader, uuid, datetime
from flask import send_from_directory, render_template, redirect, request, make_response, session
from cloudinary import CloudinaryImage
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from rembg import remove
from helpers import dark_mode

def setup_router (app, mongo):
    # Static files
    @app.route("/<path:file_path>")
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
            outfits = user["outfits"]

            data = dark_mode({"outfits": outfits}, request.cookies)
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

            data = dark_mode({"outfit": outfit}, request.cookies)
            return render_template("outfit.html", data=data)

    @app.route("/outfits/new", methods=["POST", "GET"])
    def create_outfit ():
        if request.method == "POST":
            # If user not logged in
            if not session.get("id"):
                res = make_response({"msg": "Unauthorized"}, 401)
                res.headers["HX-Redirect"] = "/outfits"
                return res

            # If required properties not added
            if "name" not in request.form or "season" not in request.form or "clothes" not in request.form or "image" not in request.files:
                data = dark_mode({"error": True}, request.cookies)
                return render_template("create-outfit.html", data=data)

            # Get request body 
            name = request.form["name"]
            season = request.form["season"]
            clothes = request.form.getlist("clothes")
            image_file = request.files["image"]

            # If user does not select a file or some inputs are not valid
            if image_file.filename == "" or name == "" or len(clothes) == 0:
                pass

            # Save image file
            image_filename = secure_filename(str(uuid.uuid4()))
            image_file_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image_file.save(image_file_path)

            # Remove image background
            image_file = open(image_file_path, "rb").read()
            image_bg_removed = remove(image_file)
            image_file = open(image_file_path, "wb")
            image_file.write(image_bg_removed)

            # Upload image to cloudinary
            result = cloudinary.uploader.upload(os.path.join(os.getcwd(), f"static/images/{image_filename}"), public_id=image_filename, overwrite=False, folder=os.environ["CLOUDINARY_OUTFITS_FOLDER"])
            image_src = result["secure_url"]
            
            # Delete image file
            os.remove(image_file_path)

            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

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
            
            res = make_response({"msg": "OK"}, 200)
            res.headers["HX-Redirect"] = f"/outfits/{new_outfit_id}?redirect"
            return res
            

        # If user logged in render template
        if session.get("id"):
            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            data = dark_mode({"closet": user["closet"]}, request.cookies)
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

                data = dark_mode({"outfits": filtered_outfits}, request.cookies)
                return render_template("components/outfit.html", data=data)


    @app.route("/outfits/delete/<string:outfit_id>", methods=["DELETE"])
    def delete_outfits (outfit_id):
        if request.method == "DELETE":
            if session.get("id"):
                # Get user document
                user_id = session.get("id")
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})


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
                data = dark_mode({ "outfits": outfits }, request.cookies)
                return render_template("components/outfit.html", data=data)

    @app.route("/closet")
    def closet ():
        # If user logged in render template
        if session.get("id"):
            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            data = dark_mode({ "closet": user["closet"] }, request.cookies)
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

            # Find clothing item
            clothing_item = {}
            for clothing_item in user["closet"]:
                if str(clothing_item["_id"]) == clothing_id:
                    clothing_item = clothing_item
                    break

            data = dark_mode({ "clothing_item": clothing_item }, request.cookies)
            return render_template("closet-item.html", data=data)

    @app.route("/closet/new", methods=["POST", "GET"])
    def add_clothes ():
        if request.method == "POST":
            # If user not logged in
            if not session.get("id"):
                res = make_response({"msg": "Unauthorized"}, 401)
                res.headers["HX-Redirect"] = "/outfits"
                return res

            # If required properties not added
            if "name" not in request.form or "type" not in request.form or "color" not in request.form or "image" not in request.files:
                data = dark_mode({ "error": True }, request.cookies)
                return render_template("add-clothes.html", data=data)

            # Get request body 
            name = request.form["name"]
            clothing_type = request.form["type"]
            brand = request.form["brand"]
            colors = request.form.getlist("color")
            image_file = request.files["image"]

            # If user does not select a file
            if image_file.filename == "":
                return make_response({"msg": "Bad Request"}, 400)

            # Save image file
            image_filename = secure_filename(str(uuid.uuid4()))
            image_file_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image_file.save(image_file_path)

            # Remove image background
            image_file = open(image_file_path, "rb").read()
            image_bg_removed = remove(image_file)
            image_file = open(image_file_path, "wb")
            image_file.write(image_bg_removed)

            # Upload image to cloudinary
            result = cloudinary.uploader.upload(os.path.join(os.getcwd(), f"static/images/{image_filename}"), public_id=image_filename, overwrite=False, folder=os.environ["CLOUDINARY_CLOSET_FOLDER"])
            image_src = result["secure_url"]

            # Delete image file
            os.remove(image_file_path)

            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

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
            
            res = make_response({"msg": "OK"}, 200)
            res.headers["HX-Redirect"] = f"/closet/{new_clothing_id}?redirect"
            return res

        # If user logged in render template
        if session.get("id"):
            data = dark_mode({ "error": False }, request.cookies)
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

                data = dark_mode({ "closet": filtered_clothes }, request.cookies)
                return render_template("components/clothing-item.html", data=data)

    @app.route("/closet/delete/<string:clothing_id>", methods=["DELETE"])
    def delete_clothes (clothing_id):
        if request.method == "DELETE":
            if session.get("id"):
                # Get user document
                user_id = session.get("id")
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

                # Remove clothes from closet list 
                closet = user["closet"]
                for item in closet:
                    if str(item["_id"]) == clothing_id:
                        # Remove image from cloudinary
                        image_public_id = item["image"].split("/")[-1].split(".")[0]
                        cloudinary.uploader.destroy(os.path.join(os.environ["CLOUDINARY_CLOSET_FOLDER"], image_public_id))
                        closet.remove(item)

                # Save updated closet
                result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"closet": closet}})

                # Return closet html
                data = dark_mode({ "closet": closet }, request.cookies)
                return render_template("components/clothing-item.html", data=data)

    @app.route("/profile")
    def profile ():
        # If user logged in render template
        if session.get("id"):
            # Get user document 
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            data = dark_mode({ "user": user }, request.cookies)
            return render_template("profile.html", data=data)

        return redirect("/")

    @app.route("/settings", methods=["GET", "POST"])
    def settings ():
        # If user logged in render template
        if session.get("id"):
            # Get user document 
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            data = dark_mode({ "user": user }, request.cookies)
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
                "outfits": []
            }

            result = mongo.db.users.insert_one(new_user)

            if result.acknowledged == False:
                return make_response({"message": "Internal Server Error"}, 500)

            # Create user session
            session["id"] = str(result.inserted_id)

            # Redirect user to outfits page
            res = make_response({"message": "OK"}, 200)
            res.headers["HX-Redirect"] = "/outfits"
            return res 

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
        result = mongo.db.users.find_one({ "email": email })

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

    @app.route("/log-out", methods=["POST"])
    def log_out ():
        if session.get("id"):
            # Remove user session
            session.pop("id", None)

            # Redirect user to index page
            res = make_response({ "message": "OK" }, 200)
            res.headers["HX-Redirect"] = "/"
            return res
