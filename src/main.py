import os, cloudinary
from flask import Flask
from flask_pymongo import PyMongo
from flask_session import Session
from routes import setup_router 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Init flask app 
app = Flask(__name__, template_folder="views")

# Setup cloudinary
app.config["CLOUDINARY"] = cloudinary.config(secure=True)

# Setup mongo client
app.config["MONGO_URI"] = os.environ["MONGO_URI"]
mongo = PyMongo(app)

# Setup uploads folder
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), 'static/images')

# Setup server sessions
app.config["SESSION_PERMANENT"] = True 
app.config["SESSION_TYPE"] = "mongodb" 
app.config["SESSION_MONGODB"] = mongo.cx
app.config["SESSION_MONGODB_DB"] = os.environ["MONGO_DB"] 
app.config["SESSION_MONGODB_COLLECT"] = "sessions" 
Session(app)

# Setup routes
setup_router(app, mongo)
