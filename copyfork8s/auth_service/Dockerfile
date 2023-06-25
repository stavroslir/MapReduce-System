# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Set environment variables
# ENV FLASK_APP=auth
# ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_RUN_PORT=5000

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . /app

# Make the container's port 5000 available to the outside world
EXPOSE 5000

# Run the command to start your app
CMD [ "python", "auth.py" ]
