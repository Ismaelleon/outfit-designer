import os
import bcrypt
from flask import send_from_directory, render_template, redirect, request, make_response, session

def setup_router (app, mongo):
    # Static files
    @app.route("/<path:file_path>")
    def static_files (file_path):
        return send_from_directory('static', file_path)

    # Views
    @app.route("/")
    def index ():
        return render_template('index.html')

    @app.route("/outfits")
    def outfits ():
        # If user logged in render template
        if session.get("id"):
            return render_template('outfits.html')

        # Otherwise, redirect to the home page
        return redirect("/")

    # Controllers
    @app.route("/sign-up", methods=['POST'])
    def sign_up ():
        if request.method == 'POST':
            # Get user data
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            # Check for user with same e-mail
            result = mongo.db.users.find_one({ 'email': email })

            if result != None:
                return make_response({'message': 'E-mail already exists'}, 409)

            # Encrypt password
            hashed_password = bcrypt.hashpw(password.encode('ascii'), bcrypt.gensalt()).decode('ascii')

            # Save new user
            new_user = {
                'name': name,
                'email': email,
                'password': hashed_password,
            }

            result = mongo.db.users.insert_one(new_user)

            if result.acknowledged == False:
                return make_response({'message': 'Internal Server Error'}, 500)

            # Create user session
            session["id"] = str(result.inserted_id)

            # Redirect user to outfits page
            res = make_response({'message': 'OK'}, 200)
            res.headers['HX-Redirect'] = '/outfits'
            return res 

    @app.route("/log-in", methods=['POST'])
    def log_in ():
        # Get user data
        email = request.form['email']
        password = request.form['password']

        # Search for user matching email address
        result = mongo.db.users.find_one({ 'email': email })

        if result == None:
            return make_response({'message': 'Not Found'}, 404)

        # Check if password doesn't match 
        if not bcrypt.checkpw(password.encode('ascii'), result['password'].encode('ascii')):
            return make_response({'message': 'Unauthorized'}, 401)

        # Create user session
        session["id"] = str(result['_id'])

        # Redirect user to outfits page
        res = make_response({'message': 'OK'}, 200)
        res.headers['HX-Redirect'] = '/outfits'
        return res 

