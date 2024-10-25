from flask import Flask, request, Response
import requests

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
    
    # Add User-Agent header to mimic a real browser
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'

    # Forward the cookies from the client
    cookies = {key: value for key, value in request.cookies.items()}

    # Forward GET and POST requests
    if request.method == 'POST':
        response = requests.post(target_url, headers=headers, data=request.form, cookies=cookies)
    else:
        response = requests.get(target_url, headers=headers, params=request.args, cookies=cookies)

    # Return the response from sbobet.com
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]

    return Response(response.content, response.status_code, headers)

if __name__ == '__main__':
    app.run(debug=True)
