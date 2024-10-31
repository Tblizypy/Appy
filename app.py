from flask import Flask, request, Response
import requests
import os
import chromedriver_autoinstaller
from selenium import webdriver

app = Flask(__name__)

# Retrieve Chrome path from environment variable
chrome_path = os.getenv("CHROME_PATH", "/usr/bin/google-chrome")

if not os.path.exists(chrome_path):
    raise RuntimeError(f"Google Chrome is not installed at the expected location: {chrome_path}")

print(f"Using Google Chrome at: {chrome_path}")

# Automatically install the matching ChromeDriver version
chromedriver_autoinstaller.install()

# Define TARGET_URL globally
TARGET_URL = 'https://www.sbobet.com/betting.aspx'

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

    # Modify response content for HTML pages
    if 'text/html' in response.headers.get('Content-Type', ''):
        content = response.content.decode('utf-8')

        # Update links in the HTML content
        content = content.replace('href="', f'href="{request.url_root}')
        content = content.replace('src="', f'src="{request.url_root}')

        response_content = content.encode('utf-8')
        return Response(response_content, response.status_code, headers)

    return Response(response.content, response.status_code, headers)

if __name__ == '__main__':
    # Set up Selenium with Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.binary_location = chrome_path  # Use Google Chrome path
    
    driver = webdriver.Chrome(options=options)
    driver.get(TARGET_URL)
    print(driver.title)

    app.run(debug=True)
