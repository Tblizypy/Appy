from flask import Flask, request, Response, render_template_string
import requests
import os
import chromedriver_autoinstaller
from selenium import webdriver
from flask_caching import Cache
from flask_compress import Compress

app = Flask(__name__)

# Set up caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
Compress(app)  # Enable Gzip compression

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
@cache.cached(timeout=60, query_string=True)  # Cache the proxy responses
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
        
        # Inject JavaScript for link interception
        js_intercept_script = '''
            <script>
                document.addEventListener('DOMContentLoaded', function () {
                    const links = document.querySelectorAll('a');

                    links.forEach(link => {
                        link.addEventListener('click', function (event) {
                            // Check if the link is external by comparing the hostname
                            const linkHost = new URL(link.href).hostname;
                            if (linkHost !== window.location.hostname) {
                                event.preventDefault();
                                window.location.href = '/error';
                            }
                        });
                    });
                });
            </script>
        '''
        
        # Inject JavaScript into HTML content
        content = content.replace('</body>', f'{js_intercept_script}</body>')
        
        response_content = content.encode('utf-8')
        headers.append(('Content-Type', 'text/html'))  # Explicitly set Content-Type
        return Response(response_content, response.status_code, headers)

    return Response(response.content, response.status_code, headers)

@app.route('/error')
def error_page():
    error_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bandwidth Limit Exceeded</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body { background-color: #f8f8f8; }
            .error-container { text-align: center; max-width: 600px; margin: auto; padding: 20px; background: #fff; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); border-radius: 8px; }
            h1 { color: #d9534f; }
            p { font-size: 1.1em; }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>Bandwidth Limit Exceeded</h1>
            <p>We're currently unable to display this content as our hosting bandwidth is limited. Please upgrade the hosting plan or try again later.</p>
        </div>
    </body>
    </html>
    '''
    return render_template_string(error_html)

if __name__ == '__main__':
    # Set up Selenium with Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.binary_location = chrome_path  # Use Google Chrome path
    
    driver = webdriver.Chrome(options=options)
    driver.get(TARGET_URL)
    print(driver.title)

    app.run(debug=True)
