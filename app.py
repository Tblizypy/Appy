from flask import Flask, request, Response
import requests
import os
import chromedriver_autoinstaller
from selenium import webdriver

app = Flask(__name__)

# Attempt to find Chrome at common locations
def get_chrome_path():
    common_paths = ["/usr/bin/google-chrome", "/usr/bin/chrome", "/opt/google/chrome/google-chrome"]
    for path in common_paths:
        if os.path.exists(path):
            return path
    raise RuntimeError("Google Chrome is not installed at any expected location.")

# Retrieve the Chrome path
chrome_path = get_chrome_path()
print(f"Using Chrome at: {chrome_path}")

# Automatically install the matching ChromeDriver version
chromedriver_autoinstaller.install()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    target_url = f'{TARGET_URL}/{path}'
    headers = {key: value for key, value in request.headers if key != 'Host'}
    if request.method == 'POST':
        response = requests.post(target_url, headers=headers, data=request.form)
    else:
        response = requests.get(target_url, headers=headers, params=request.args)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]
    return Response(response.content, response.status_code, headers)

if __name__ == '__main__':
    TARGET_URL = 'https://www.sbobet.com'
    
    # Set up Selenium with Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.binary_location = chrome_path  # Set the dynamically found path
    
    driver = webdriver.Chrome(options=options)
    driver.get(TARGET_URL)
    print(driver.title)

    app.run(debug=True)
