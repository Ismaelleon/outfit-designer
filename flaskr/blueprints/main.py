from flask import render_template, request, send_from_directory, session, redirect, Blueprint
from flaskr.helpers import dark_mode

bp = Blueprint("main", __name__, url_prefix="/")

# Static files
@bp.route("/static/<path:file_path>")
def static_files (file_path):
    return send_from_directory("static", file_path)

@bp.route("/")
def index ():
    # If user logged in, redirect to outfits page 
    if session.get("id"):
        return redirect("/outfits")

    data = dark_mode({}, request.cookies)
    return render_template("index.html", data={})
