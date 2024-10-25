from flask import Flask, request, Response
import requests
import chromedriver_autoinstaller  # Import the autoinstaller
from selenium import webdriver  # Import Selenium WebDriver

# Automatically install the correct version of ChromeDriver
chromedriver_autoinstaller.install()

app = Flask(__name__)

# Proxy URL
TARGET_URL = 'https://www.sbobet.com'

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
    # Set up Selenium with Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode if needed (no browser UI)
    driver = webdriver.Chrome(options=options)

    # Example usage: navigate to a webpage
    driver.get("https://www.sbobet.com")
    print(driver.title)  # Prints the title of the webpage

    app.run(debug=True)
