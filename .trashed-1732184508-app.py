from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask App!"  # A simple message for the root URL

@app.route('/login', methods=['POST'])
def login():
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Start a new Chrome browser session
    service = Service('/data/data/com.termux/files/home/chromedriver')  # Update this path

    try:
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            # Navigate to the sbobet login page
            driver.get("https://www.sbobet.com/login")

            # Wait for the username and password fields to be present
            wait = WebDriverWait(driver, 10)
            username_input = wait.until(EC.presence_of_element_located((By.ID, 'username')))
            password_input = wait.until(EC.presence_of_element_located((By.ID, 'password')))

            # Enter your login credentials
            username_input.send_keys(request.form['username'])
            password_input.send_keys(request.form['password'])

            # Click the login button
            login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()

            # Wait for the login process to complete
            time.sleep(3)

            # Check if login was successful
            if "login" not in driver.current_url:
                return jsonify({"success": True, "message": "Logged in successfully!"}), 200
            else:
                return jsonify({"success": False, "message": "Login failed."}), 403
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))  # Listen on all interfaces