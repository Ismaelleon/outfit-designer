FROM python:3.10

# Create work directory for app
WORKDIR /home/outfit-designer

# Copy project files
COPY ./src/ ./src/

# Copy requirements.txt
COPY ./requirements.txt ./

# Create virtual environment
RUN python3 -m venv ./env;

# Activate virtual environment
RUN . ./env/bin/activate

# Install dependencies
RUN python3 -m pip install -r ./requirements.txt --pre

# Move into src directory
RUN cd ./src/

# Expose port 5000
EXPOSE 5000

# Start gunicorn server from src directory
CMD ["gunicorn", "--bind=0.0.0.0:5000", "-w=4", "-k=gthread", "--chdir=/home/outfit-designer/src", "wsgi:app"]
