from flaskr.extensions import mongo
from flaskr.helpers import dark_mode, handle_invalid_user_session, upload_image
from flask import render_template, request, make_response, session, redirect, Blueprint, current_app
from bson.objectid import ObjectId
import cloudinary, os

bp = Blueprint("closet", __name__, url_prefix="/closet")

@bp.route("/")
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

@bp.route("/<string:clothing_id>")
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

@bp.route("/new", methods=["GET", "POST"])
def add_clothes ():
    if request.method == "GET":
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
    elif request.method == "POST":
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
        image_src = upload_image(os.environ["CLOUDINARY_CLOSET_FOLDER"], image_file, current_app)

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


@bp.route("/filter", methods=["POST"])
def filter_clothes ():
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

@bp.route("/delete/<string:clothing_id>", methods=["DELETE"])
def delete_clothes (clothing_id):
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

