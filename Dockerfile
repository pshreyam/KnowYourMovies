# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code into the container
COPY . .

# Expose the port number on which the Flask app will run (default is 5000)
EXPOSE 5000

# Command to run the Flask application using Gunicorn
CMD ./start.sh
