import logging
import pages
from waveshare_epd import epd2in7_V2
import time
import requests
import json
import os
from gpiozero import Button

# Set up logging
logging.basicConfig(level=logging.DEBUG)

LOCAL_JSON_PATH = 'local_satirical_content.json'
REMOTE_JSON_URL = 'https://wallcop100.github.io/SatericalHeadlineBackend/satirical_content.json'
CHECK_INTERVAL = 900  # 15 minutes in seconds

# GPIO pins for the buttons
BUTTON_PINS = [5, 6, 13, 19]


def get_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching JSON data: {e}")
        return None


def load_local_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding local JSON file: {e}")
    return None


def save_local_json(path, data):
    try:
        with open(path, 'w') as file:
            json.dump(data, file)
    except IOError as e:
        logging.error(f"Error saving local JSON file: {e}")


def render_title_page(epd, json_data):
    date = json_data.get('Date', 'Unknown Date')
    time_of_day = json_data.get('Time', 'Unknown Time')
    politics_headline = json_data.get('Politics', {}).get('Headline', 'Default Politics Headline')
    newline = '\n'
    title_text = 'Parody Post'
    date_text = f"{date} {newline} {time_of_day} Edition"

    # Render and display the title page
    pages.render_title_page(epd, title_text, date_text)


def render_politics_headline(epd, json_data):
    politics_headline = json_data.get('Politics', {}).get('Headline', 'Default Politics Headline')
    # Render and display the title page
    pages.render_headline_page(epd, politics_headline)



def render_politics_page(epd, json_data):
    politics_article = json_data.get('Politics', {}).get('Article', 'Default Politics Article')

    # Render and display the politics page
    pages.render_body_page(epd, politics_article)



def render_general_page(epd, json_data):
    general_headline = json_data.get('General', {}).get('Headline', 'Default General Headline')


    # Render and display the general news page
    pages.render_headline_page(epd, general_headline)



def render_combined_page(epd, json_data):
    general_article = json_data.get('General', {}).get('Article', 'Default General Article')
    # Render and display the combined page
    pages.render_body_page(epd, general_article)



def button_callback(btn):
    logging.info(f"Button on GPIO {btn.pin.number} pressed.")
    epd = epd2in7_V2.EPD()
    epd.init()
    epd.Clear()

    # Load local JSON data
    local_json_data = load_local_json(LOCAL_JSON_PATH)

    if local_json_data:
        # Map each button to a specific page rendering function
        if btn.pin.number == 5:
            #render_title_page(epd, local_json_data)
            render_politics_headline(epd, local_json_data)
        elif btn.pin.number == 6:
            render_politics_page(epd, local_json_data)
        elif btn.pin.number == 13:
            render_general_page(epd, local_json_data)
        elif btn.pin.number == 19:
            render_combined_page(epd, local_json_data)





def setup_buttons():
    for pin in BUTTON_PINS:
        btn = Button(pin)
        btn.when_pressed = button_callback

def check_for_updates():
    logging.info("Starting Data Update Check")
    epd = epd2in7_V2.EPD()
    while True:
        # Load local JSON data
        local_json_data = load_local_json(LOCAL_JSON_PATH)

        # Fetch JSON data from remote
        remote_json_data = get_json_data(REMOTE_JSON_URL)

        if remote_json_data:
            # Check if the remote data is different from the local data
            if local_json_data != remote_json_data:
                logging.info("New data found. Updating display.")
                save_local_json(LOCAL_JSON_PATH, remote_json_data)
                render_title_page(epd, remote_json_data)
                time.sleep(10)
                render_politics_headline(epd, remote_json_data)
            else:
                logging.info("No new data. Skipping update.")
        else:
            logging.ERROR("Failed to fetch remote data. Using local data if available.")
            if local_json_data:
                pages.render_headline_page(epd, "Failed to fetch remote data. Using local data if available.")
                time.sleep(30)
                render_politics_headline(epd, local_json_data)

            else:
                logging.CRITICAL("No local data available. Cannot update display.")
                pages.render_headline_page(epd, "No local data available. Cannot update display.")

        # Sleep for the specified interval before checking again
        epd.sleep()
        logging.info("Sleeping for 15 Minutes")
        time.sleep(CHECK_INTERVAL)
def main():
    try:
        logging.info("Starting Up...")
        epd = epd2in7_V2.EPD()

        epd.init()
        # Button setup
        setup_buttons()

        check_for_updates()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd.sleep()
        src.waveshare_epd.epdconfig.module_exit(cleanup=True)
        exit()


if __name__ == "__main__":
    main()
