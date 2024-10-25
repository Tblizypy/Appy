from flask import Flask, request, Response
import requests
import os
import subprocess
import chromedriver_autoinstaller
from selenium import webdriver

app = Flask(__name__)

# Install Google Chrome if not found
def install_chrome():
    chrome_path = "/usr/bin/google-chrome"
    if not os.path.exists(chrome_path):
        print("Google Chrome not found. Installing...")
        # Install Chrome via apt-get for Ubuntu/Debian-based systems
        subprocess.run("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", shell=True)
        subprocess.run("sudo apt-get update", shell=True)
        subprocess.run("sudo apt install ./google-chrome-stable_current_amd64.deb -y", shell=True)
        print("Google Chrome installed.")
    else:
        print("Google Chrome is already installed.")

# Automatically install the correct version of ChromeDriver
chromedriver_autoinstaller.install()

# Install Chrome
install_chrome()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    # Construct the target URL
    target_url = f'{TARGET_URL}/{path}'

    # Forward the request headers
    headers = {key: value for key, value in request.headers if key != 'Host'}

    # Forward GET and POST requests
    if request.method == 'POST':
        response = requests.post(target_url, headers=headers, data=request.form)
    else:
        response = requests.get(target_url, headers=headers, params=request.args)

    # Return the response from sbobet.com
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]

    return Response(response.content, response.status_code, headers)

if __name__ == '__main__':
    TARGET_URL = 'https://www.sbobet.com'
    
    # Set up Selenium with Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode if needed
    driver = webdriver.Chrome(options=options)

    # Example usage: navigate to a webpage
    driver.get(TARGET_URL)
    print(driver.title)  # Prints the title of the webpage

    app.run(debug=True)
