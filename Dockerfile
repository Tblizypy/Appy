# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install necessary packages, including Chromium
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable for Chromium path
ENV CHROME_PATH=/usr/bin/chromium

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Command to run your application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
