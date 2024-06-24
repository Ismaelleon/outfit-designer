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
            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            return render_template('create-outfit.html', closet=user['closet'])

        # Otherwise, redirect to the home page
        return redirect("/")

    @app.route("/closet")
    def closet ():
        # If user logged in render template
        if session.get("id"):
            # Get user document
            user_id = session.get("id")
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            return render_template('closet.html', closet=user['closet'])

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
            for clothing_item in user['closet']:
                if clothing_item['_id'] == clothing_id:
                    clothing_item = clothing_item

            return render_template('closet-item.html', clothing_item=clothing_item)

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
            result = cloudinary.uploader.upload(os.path.join(os.getcwd(), f'static/images/{filename}'), public_id=filename, overwrite=False)
            image_src = result['secure_url']

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

    @app.route("/closet/delete/<string:clothing_id>", methods=['DELETE'])
    def delete_clothes (clothing_id):
        if request.method == 'DELETE':
            if session.get("id"):
                # Get user document
                user_id = session.get("id")
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

                # Remove clothes from closet list 
                closet = user['closet']
                for item in closet:
                    if str(item['_id']) == clothing_id:
                        closet.remove(item)

                # Save updated closet
                result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"closet": closet}})

                # Return closet html
                html = ''
                for clothing_item in closet: 
                    html += f'''
                        <section class="flex flex-col p-3 rounded border" id={ clothing_item['_id'] }>
                            <img src="{ clothing_item['image'] }" alt="" class="w-full rounded mb-2">	
                            <header class="flex flex-row justify-between items-center">
                                <a href="/closet/{ clothing_item['_id'] }" class="text-base font-bold">{ clothing_item['name'].capitalize() }</a>
                                <button class="p-1 relative" onclick="toggleMenu(event)">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                                    </svg>
                                    <ul class="absolute right-0 top-8 min-w-36 bg-white rounded border hidden">
                                        <li class="flex justify-between items-center text-sm font-medium w-full p-2 hover:bg-zinc-200" 
                                            hx-delete={ '/closet/delete/{}'.format(clothing_item['_id']) } hx-swap="innerHTML" hx-target="#clothing-list">
                                            Delete clothing 
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="red" class="size-4">
                                                <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                            </svg>

                                        </li>
                                    </ul>
                                </button>
                            </header>
                            <span class="text-sm"><span class="font-medium">Brand</span>: { clothing_item['brand'].capitalize() }</span>
                            <span class="text-sm"><span class="font-medium">Type</span>: { clothing_item['type'].capitalize() }</span>
                            <span class="text-sm"><span class="font-medium">Colors</span>: { clothing_item['colors'].capitalize() }</span>
                        </section>	
                    '''

                return html
            

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

