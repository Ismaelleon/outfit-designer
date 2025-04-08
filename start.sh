#!/bin/bash 
 
# Get into the app directory 
cd /root/outfit-designer/ && 
 
# Start virtual environment 
source ./env/bin/activate && 
 
# Install dependencies from requirements.txt 
./env/bin/python3 -m pip install -r requirements.txt && 
 
# Get into src directory 
cd ./src/ 
 
# Start gunicorn wsgi 
../env/bin/python3 -m gunicorn --bind 0.0.0.0:5000 wsgi:app
