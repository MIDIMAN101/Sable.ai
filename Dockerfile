# Use the official Python 3.10 runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Define the command to run the application
# This is a standard entry point for Cloud Functions
CMD ["python3", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
