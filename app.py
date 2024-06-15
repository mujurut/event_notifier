from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# Function to filter and return event information based on location
def get_events_by_location(location):
    # Set up the Selenium WebDriver with headless option
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    # Navigate to the webpage
    driver.get('https://caseyrocket.komi.io/')

    # Wait for the JavaScript to load the content
    time.sleep(5)  # Adjust this time based on your internet speed and page load time

    # Get the page source after the JavaScript has loaded
    page_source = driver.page_source

    # Close the driver
    driver.quit()

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Find the div with the specified ID
    tour_events_div = soup.find('div', id='6359b75d-2ae7-4075-8b11-5738010a081f')

    events = []

    if tour_events_div:
        # Find all the divs with class "swiper-slide" within the specified div
        swiper_slides = tour_events_div.find_all("div", class_="swiper-slide")

        for divv in swiper_slides:
            text_elements = divv.find_all(class_="text")
            event_details = [tx.get_text() for tx in text_elements]

            if len(event_details) >= 5:  # Ensure there are at least 5 elements to prevent index errors
                event_location = event_details[4]
                if location.lower() in event_location.lower():
                    event = {
                        "Month": event_details[0],
                        "Day": event_details[1],
                        "Year": event_details[2],
                        "Comedy Club": event_details[3],
                        "Location": event_location
                    }
                    events.append(event)
    return events

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()  # Get JSON data from the request
    location = data.get('location', '')  # Safely get the location key
    events = get_events_by_location(location)
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
