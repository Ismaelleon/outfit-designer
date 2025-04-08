# Get into the app directory
cd /root/outfit-designer/src/

# Start virtual environment
source env/bin/activate

# Install dependencies from requirements.txt
./env/bin/python3 -m pip install -r requirements.txt

# Start gunicorn wsgi
/usr/bin/gunicorn --bind 0.0.0.0:5000 wsgi:app
