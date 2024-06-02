import os, bcrypt, cloudinary, cloudinary.uploader
from flask import send_from_directory, render_template, redirect, request, make_response, session
from cloudinary import CloudinaryImage
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

def setup_router (app, mongo):
    # Static files
    @app.route("/<path:file_path>")
    def static_files (file_path):
        return send_from_directory('static', file_path)

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

    @app.route("/outfits/new")
    def create_outfit ():
        # If user logged in render template
        if session.get("id"):
            return render_template('create-outfit.html')

        # Otherwise, redirect to the home page
        return redirect("/")

    @app.route("/closet")
    def closet ():
        # If user logged in render template
        if session.get("id"):
            return render_template('closet.html')

        # Otherwise, redirect to the home page
        return redirect("/")

    @app.route("/closet/new", methods=['POST', 'GET'])
    def add_clothes ():
        if request.method == 'POST':
            # If user not logged in
            if not session.get("id"):
                res = make_response({"msg": "Unauthorized"}, 401)
                res.headers['HX-Redirect'] = '/outfits'
                return res

            # Get request body 
            name = request.form['name']
            clothing_type = request.form['type']
            brand = request.form['brand']
            colors = request.form['color']
            image_file = request.files['image']

            # If user does not select a file
            if image_file.filename == '':
                return make_response({'msg': 'Bad Request'}, 400)

            # Save image file
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Upload image to cloudinary
            cloudinary.uploader.upload(os.path.join(os.getcwd(), f'static/images/{filename}'), public_id=filename, overwrite=False)
            image_src = CloudinaryImage(filename).build_url()

            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            # Update closet array 
            closet = user['closet']
            new_clothing_id = ObjectId()
            closet.append({
                '_id': new_clothing_id,
                'name': name,
                'type': clothing_type,
                'brand': brand,
                'colors': colors,
                'image': image_src 
            })

            # Update document with updated closet array
            result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"closet": closet}})
            
            res = make_response({'msg': 'OK'}, 200)
            res.headers['HX-Redirect'] = f'/closet/{new_clothing_id}'
            return res

        # If user logged in render template
        if session.get("id"):
            return render_template('add-clothes.html')

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
                'closet': [],
                'outfits': []
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

