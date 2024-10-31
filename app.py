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
    headers = {key: value for key, value in request.headers if key != 'Host'}

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
            
            # Update relative paths in the HTML content
            content = content.replace('href="/', f'href="{request.url_root}')
            content = content.replace('src="/', f'src="{request.url_root}')
            
            # Fix <base> tag if it exists
            content = content.replace('<base href="', f'<base href="{request.url_root}')
            
            # Redirect all links that point to help and info articles to your local /help path
            content = re.sub(r'https?://(?:help|info)\.sbobet\.com/article/([a-zA-Z0-9-]+)-(\d+)\.html',
                             f'{request.url_root}help/\\1-\\2',
                             content)
                             
            # Remove target="_blank" to prevent new tabs from opening
            content = re.sub(r'target="_blank"', '', content)

            # Replace all absolute URLs to ensure the user stays within your domain
            content = content.replace('https://account.sbobet.com', request.url_root)

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

# Create a route to handle help articles within your domain
@app.route('/help/<path:article>')
def help_redirect(article):
    # Construct the full help article URL
    help_url = f'https://help.sbobet.com/article/{article}'
    try:
        response = requests.get(help_url)
        content = response.content.decode('utf-8')
        
        # Update relative paths in the HTML content to stay within your domain
        content = content.replace('href="/', f'href="{request.url_root}')
        content = content.replace('src="/', f'src="{request.url_root}')
        
        # Remove target="_blank" to prevent new tabs from opening
        content = re.sub(r'target="_blank"', '', content)
        
        return Response(content, status=response.status_code, headers={'Content-Type': 'text/html'})

    except requests.RequestException:
        return Response("<h1>Error: Unable to retrieve help article</h1>", status=500)

if __name__ == '__main__':
    # Set up Selenium with Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.binary_location = chrome_path  # Use Google Chrome path
    
    driver = webdriver.Chrome(options=options)
    driver.get(TARGET_URL)
    print(driver.title)

    app.run(debug=True)
