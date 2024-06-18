# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Install MySQL client dependencies and pkg-config
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the image
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the image
COPY . .

# Set environment variable to enable Gunicorn's live reload in development
ENV GUNICORN_CMD_ARGS="--reload"

# Command to run the application
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "app:app"]

#Command to install bootstrap for flask 
RUN pip install Flask-Bootstrap

#Command to install flask-login
RUN pip install flask-login

# Command to install WTF forms 
RUN pip install Flask-WTF
