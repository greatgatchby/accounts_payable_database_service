# Use the official Python base image with version 3.8.9
FROM python:3.8.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code to the working directory
COPY . .

# Set the environment variable for Flask app
ENV FLASK_APP=accounts_payable_service

# Expose the port on which the Flask app will run (change if necessary)
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
