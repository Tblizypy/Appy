from flask import Flask, request, Response
import requests
import os
import chromedriver_autoinstaller
from selenium import webdriver
import re

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
    headers = {
        key: value for key, value in request.headers if key.lower() not in ['host', 'referer']
    }
    headers['Referer'] = TARGET_URL  # Spoof the Referer header
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'

    try:
        if request.method == 'POST':
            response = requests.post(target_url, headers=headers, data=request.form)
        else:
            response = requests.get(target_url, headers=headers, params=request.args)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]

        # Modify response content for HTML pages
        if 'text/html' in response.headers.get('Content-Type', ''):
            content = response.content.decode('utf-8')
            
            # Replace all links to external domains with the error page link
            content = re.sub(r'href="https?://[^"]+"', 'href="/error"', content)
            content = re.sub(r'src="https?://[^"]+"', 'src="/error"', content)
            
            # Remove target="_blank" to prevent new tabs from opening
            content = re.sub(r'target="_blank"', '', content)

            response_content = content.encode('utf-8')
            headers.append(('Content-Type', 'text/html'))  # Explicitly set Content-Type
            return Response(response_content, response.status_code, headers)

        return Response(response.content, response.status_code, headers)

    except requests.RequestException:
        # Custom error message if the target URL fails
        error_message = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error</title>
            <style>
                body { background-color: #add8e6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: Arial, sans-serif; }
                .error-container { text-align: center; }
                .error-id { color: red; font-size: 24px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="error-container">
                <p>Dear customer, an unexpected error has occurred. Please try again later or you can contact our Support Team with Error ID:</p>
                <p class="error-id">B30-021-756</p>
            </div>
        </body>
        </html>
        """
        return Response(error_message, status=500, mimetype='text/html')

# Create a route to handle the custom error page
@app.route('/error')
def custom_error_page():
    # Custom error page content
    error_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bandwidth Limit Exceeded</title>
        <style>
            body { display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: Arial, sans-serif; background-color: #f8f8f8; }
            .error-container { text-align: center; max-width: 600px; padding: 20px; border: 1px solid #ccc; border-radius: 8px; background-color: #fff; }
            h1 { color: #333; }
            p { color: #666; }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>Bandwidth Limit Exceeded</h1>
            <p>Our hosting plan's bandwidth is currently insufficient to support this content. Please bear with us as we work to increase our capacity.</p>
            <p>Thank you for your understanding.</p>
        </div>
    </body>
    </html>
    """
    return Response(error_page, status=200, mimetype='text/html')

if __name__ == '__main__':
    # Set up Selenium with Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.binary_location = chrome_path  # Use Google Chrome path
    
    driver = webdriver.Chrome(options=options)
    driver.get(TARGET_URL)
    print(driver.title)

    app.run(debug=True)
