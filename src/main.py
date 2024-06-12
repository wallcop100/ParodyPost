import logging
from waveshare_epd import epd2in7_V2
import time
import requests
import json
import os
from gpiozero import Button
from PIL import Image

# Set up logging
logging.basicConfig(level=logging.DEBUG)
LOCAL_JSON_PATH = 'local_satirical_content.json'
REMOTE_JSON_URL = 'https://wallcop100.github.io/SatericalHeadlineBackend/output/manifest.json'
CHECK_INTERVAL = 900  # 15 minutes in seconds
epd = epd2in7_V2.EPD()

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


def download_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Create content folder if it doesn't exist
        if not os.path.exists("content"):
            os.makedirs("content")

        filepath = os.path.join("content", filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        logging.info(f"Downloaded image: {filename}")
    except requests.RequestException as e:
        logging.error(f"Error downloading image: {url} - {e}")


def render_page(page):
    Render = Image.open(f'content/page_{page}.bmp')
    epd.display(epd.getbuffer(Render))


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
            render_page(1)
        elif btn.pin.number == 6:
            render_page(2)
        elif btn.pin.number == 13:
            render_page(3)
        elif btn.pin.number == 19:
            render_page(4)


def setup_buttons():
    for pin in BUTTON_PINS:
        btn = Button(pin)
        btn.when_pressed = button_callback


def check_for_updates():
    logging.info("Starting Data Update Check")
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

                # Clear content folder before downloading new images
                for filename in os.listdir("content"):
                    filepath = os.path.join("content", filename)
                    os.remove(filepath)
                    logging.info(f"Deleted old image: {filename}")

                # Download images from Page Files section
                page_files = remote_json_data["Page Files"]
                for name, image_url in page_files.items():
                    download_image(image_url, name)

                render_page("title")
                time.sleep(10)
                render_page(1)
            else:
                logging.info("No new data. Skipping update.")
        else:
            logging.ERROR("Failed to fetch remote data. Using local data if available.")
            if local_json_data:
                render_page(1)
            else:
                logging.CRITICAL("No local data available. Cannot update display.")

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