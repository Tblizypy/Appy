#!/bin/bash

# Update the package list
apt-get update

# Install wget and unzip
apt-get install -y wget unzip

# Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
wget https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin/
