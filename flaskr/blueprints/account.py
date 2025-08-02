from flaskr.extensions import mongo
from flaskr.helpers import dark_mode, handle_invalid_user_session
from flask import render_template, request, make_response, session, redirect, Blueprint 
from bson.objectid import ObjectId
import bcrypt

bp = Blueprint("account", __name__, url_prefix="/account")

@bp.route("/")
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

@bp.route("/settings", methods=["GET"])
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

@bp.route("/delete", methods=["DELETE"])
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
