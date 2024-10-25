# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install necessary packages and Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/google-chrome /usr/bin/chrome \
    && echo "Chrome installed at:" $(which google-chrome) \
    && echo "Chrome version:" && google-chrome --version

# Set environment variable for Chrome path
ENV CHROME_PATH=/usr/bin/google-chrome

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