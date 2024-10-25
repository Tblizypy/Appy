from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set Chrome binary location and chromedriver path
    chrome_options.binary_location = '/usr/bin/google-chrome'
    service = Service('/usr/local/bin/chromedriver')
    
    # Start a new Chrome browser session
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to the sbobet login page
    driver.get("https://www.sbobet.com")

    # Wait for the username and password fields to be present
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.ID, 'username')))
    password_input = wait.until(EC.presence_of_element_located((By.ID, 'password')))

    # Enter the login credentials
    username_input.send_keys(request.form['username'])
    password_input.send_keys(request.form['password'])

    # Click the login button
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()

    # Wait for the login process to complete
    time.sleep(3)

    # Check if login was successful by checking the current URL or page title
    if "login" not in driver.current_url:
        return jsonify({"success": True, "message": "Logged in successfully!"}), 200
    else:
        return jsonify({"success": False, "message": "Login failed."}), 403

    driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
