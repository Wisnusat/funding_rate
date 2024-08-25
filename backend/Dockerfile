# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install ping, curl, supervisord, and other necessary utilities
RUN apt-get update && apt-get install -y iputils-ping curl supervisor && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the necessary ports
EXPOSE 8000

# Run supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]


# single stage build
# # Use an official Python runtime as a parent image
# FROM python:3.11-slim

# # Install ping, curl, and other necessary utilities (optional)
# RUN apt-get update && apt-get install -y iputils-ping curl && rm -rf /var/lib/apt/lists/*

# # Set the working directory
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Make port 8000 available to the world outside this container
# EXPOSE 8000

# # Run the application using Gunicorn
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]

