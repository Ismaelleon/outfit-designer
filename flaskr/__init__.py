import os, cloudinary
from flask import Flask
from flask_session import Session
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from .extensions import mongo

# Load environment variables from .env file
load_dotenv()

def create_app():
    # Init flask app 
    app = Flask(__name__, template_folder="views")

    # Setup mongo
    app.config["MONGO_URI"] = os.environ["MONGO_URI"]
    mongo.init_app(app)

    # Setup cloudinary
    app.config["CLOUDINARY"] = cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True
    )

    # Setup uploads folder
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), os.environ["UPLOAD_FOLDER"])

    # Setup server sessions
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_TYPE"] = "mongodb"
    app.config["SESSION_MONGODB"] = mongo.cx
    app.config["SESSION_MONGODB_DB"] = os.environ["MONGO_DB"]
    app.config["SESSION_MONGODB_COLLECT"] = "sessions"
    Session(app)

    # Register blueprints
    from .blueprints.account import bp as account_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.closet import bp as closet_bp
    from .blueprints.main import bp as main_bp
    from .blueprints.outfits import bp as outfits_bp

    app.register_blueprint(account_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(closet_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(outfits_bp)

    return app
