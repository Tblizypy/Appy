#!/bin/bash

# Install dependencies
apt-get update && apt-get install -y wget unzip

# Download Google Chrome (use a pre-built version)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Download ChromeDriver (hardcode a specific version to avoid mismatches)
CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Clean up
rm google-chrome-stable_current_amd64.deb chromedriver_linux64.zip
