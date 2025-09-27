from flaskr.extensions import mongo
from flaskr.helpers import dark_mode, handle_invalid_user_session, upload_image, generate_outfit_image
from flask import render_template, request, make_response, session, redirect, Blueprint, current_app as app
from bson.objectid import ObjectId
import cloudinary, os, datetime

bp = Blueprint("outfits", __name__, url_prefix="/outfits")

@bp.route("/")
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

@bp.route("/<string:outfit_id>")
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

@bp.route("/edit/<string:outfit_id>", methods=["GET", "POST"])
def edit_outfit(outfit_id):
    if request.method == "GET":
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
    elif request.method == "POST":
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


@bp.route("/new", methods=["GET", "POST"])
def create_outfit ():
    if request.method == "GET":
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
    elif request.method == "POST":
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
        if "name" not in request.form or "season" not in request.form:
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
        image_file = request.files["image"] if "image" in request.files else None

        # Initialize image source
        image_src = None

        # If user does not upload an image for the outfit generate an outfit image
        if image_file == None:
            # Get clothes details from user closet
            clothes_details = []
            
            for clothing_id in clothes:
                for clothing_item in user["closet"]:
                    if str(clothing_item["_id"]) == clothing_id:
                        public_id = clothing_item["image"].split("/")[-1].split(".")[0]
                        _id = clothing_item["_id"]
                        type_ = clothing_item["type"]
                        image = clothing_item["image"]

                        clothes_details.append({ "public_id": public_id, "_id": _id, "type": type_, "image": image })

            # Order clothes by type
            clothes_details.sort(key=lambda x: x["type"])

            # Create an image for the outfit using layers
            image_file = generate_outfit_image(clothes_details)

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

@bp.route("/filter", methods=["POST"])
def filter_outfits ():
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


@bp.route("/delete/<string:outfit_id>", methods=["DELETE"])
def delete_outfits (outfit_id):
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

