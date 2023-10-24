# Use the official Python image as a base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tk-dev

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY ./docker/Requirements.txt .

# Install Python dependencies from Requirements.txt
RUN pip install -r Requirements.txt

# Expose port for Flask app
EXPOSE 5000 

# Define environment variable
ENV FLASK_APP=main.py

# Copy the application source code into the container
COPY ./src/ .

# Specify the command to run your application
#CMD ["python", "main.py"]

# Run flask app with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
