# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR ./webapp

# Copy the requirements file into the container
COPY requirements.txt .

# Update Pip
RUN pip install --upgrade pip

# Install SQLite support
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the webapp runs on
EXPOSE 8000

# Run the application using Gunicorn with debug level logging
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "--log-level=debug", "webapp:app"]
