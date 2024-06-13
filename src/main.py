import logging
from waveshare_epd import epd2in7_V2
import time
import requests
import json
import os
import subprocess
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
import io



# Set up logging
logging.basicConfig(level=logging.DEBUG)
log_capture = io.StringIO()
logging.basicConfig(stream=log_capture, level=logging.ERROR)

# Define paths relative to the script location
REPO_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOCAL_JSON_PATH = os.path.join(REPO_ROOT_DIR, 'src/manifest.json')
LOCAL_VERSION_FILE = os.path.join(REPO_ROOT_DIR, 'version.txt')
UPDATE_SCRIPT = os.path.join(REPO_ROOT_DIR, 'update_script.py')
REMOTE_JSON_URL = 'https://wallcop100.github.io/SatericalHeadlineBackend/output/manifest.json'
GITHUB_REPO_API_URL = 'https://api.github.com/repos/wallcop100/ParodyPost/releases/latest'
CHECK_INTERVAL = 900  # 15 minutes in seconds
DEBUG_FONT = ImageFont.truetype(os.path.join(REPO_ROOT_DIR, 'src/Font.ttf'), 5)


# Configure logging to write to log_capture
logging.basicConfig(stream=log_capture, level=logging.DEBUG)
epd = epd2in7_V2.EPD()

# GPIO pins for the buttons
pressed_buttons = []
BUTTON_PINS = [5, 6, 13, 19]
last_press_time = 0
current_time = time.time()
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
        content_dir = os.path.join(REPO_ROOT_DIR, 'src/content')
        if not os.path.exists(content_dir):
            os.makedirs(content_dir)

        filepath = os.path.join(content_dir, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        logging.info(f"Downloaded image: {filename}")
    except requests.RequestException as e:
        logging.error(f"Error downloading image: {url} - {e}")


def render_page(page):
    image_path = os.path.join(REPO_ROOT_DIR, f'src/content/page_{page}.bmp')

    try:
        image = Image.open(image_path)
    except IOError as e:
        logging.error(f"Error opening image {image_path}: {e}")
        return

    try:
        epd.init()
        epd.display(epd.getbuffer(image))
    except IOError as e:
        logging.error(f"Error displaying image on EPD: {e}")
    finally:
        epd.sleep()


# Function to handle button presses
def button_callback(btn):
    global pressed_buttons, last_press_time, epd, current_time

    logging.info(f"Button on GPIO {btn.pin.number} pressed.")

    last_press_time = current_time
    # Check if it's been less than 2 seconds since last press
    if current_time - last_press_time <= 2:
        # Add the pressed button to the list
        if btn.pin.number not in pressed_buttons:
            pressed_buttons.append(btn.pin.number)

        # Check if two buttons are pressed together
        if len(pressed_buttons) == 2:
            # Perform action for two buttons pressed together
            if 5 in pressed_buttons and 19 in pressed_buttons:
                logging.info("Buttons 5 and 19 pressed together within 2 seconds. Performing action...")
                debug_info()
                return  # Exit the function to avoid single press action

            # Clear pressed_buttons list after action
            pressed_buttons = []
    else:
        # It's a single press scenario
        pressed_buttons = [btn.pin.number]

    # Perform individual button actions if needed
    local_json_data = load_local_json(LOCAL_JSON_PATH)
    if local_json_data:
        if btn.pin.number == 5:
            render_page(1)
        elif btn.pin.number == 6:
            render_page(2)
        elif btn.pin.number == 13:
            render_page(3)
        elif btn.pin.number == 19:
            render_page(4)

    # Update last press time regardless of single or double press
    last_press_time = current_time
def setup_buttons():
    for pin in BUTTON_PINS:
        btn = Button(pin)
        btn.when_pressed = button_callback


def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        try:
            with open(LOCAL_VERSION_FILE, 'r') as file:
                return file.read().strip()
        except IOError as e:
            logging.error(f"Error reading local version file: {e}")
    return None


def get_remote_version():
    try:
        response = requests.get(GITHUB_REPO_API_URL)
        response.raise_for_status()
        release_info = response.json()
        return release_info['tag_name']
    except requests.RequestException as e:
        logging.error(f"Error fetching remote version from GitHub: {e}")
        return None


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
                content_dir = os.path.join(REPO_ROOT_DIR, 'src/content')
                for filename in os.listdir(content_dir):
                    filepath = os.path.join(content_dir, filename)
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
                logging.info("No new content. Skipping update.")
        else:
            logging.error("Failed to fetch remote data. Using local data if available.")
            if local_json_data:
                render_page(1)
            else:
                logging.critical("No local data available. Cannot update display.")

        # Sleep for the specified interval before checking again
        epd.sleep()
        logging.info("Sleeping for 15 Minutes")
        time.sleep(CHECK_INTERVAL)


def check_for_software_update():
    while True:
        logging.info("Checking for software updates...")
        local_version = get_local_version()
        remote_version = get_remote_version()

        if local_version and remote_version:
            if local_version != remote_version:
                logging.info(f"New software version found: {remote_version}. Updating from version: {local_version}")
                # Run the update script as a separate process
                subprocess.Popen(['python3', UPDATE_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                logging.info("Software is up to date.")
        else:
            logging.error("Could not determine local or remote version.")
def debug_info():
    global epd
    local_version = get_local_version()
    log_content = log_capture.getvalue()
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    draw.text((50, 30), "DEBUG MODE", font=DEBUG_FONT, fill='black')
    draw.text((50, 30), local_version, font=DEBUG_FONT, fill='black')
    #draw.text((10, 50), log_content, font=DEBUG_FONT, fill='black')
    time.sleep(2)
    try:
        epd.init()
        epd.display_Base(epd.getbuffer(image))
    except IOError as e:
        logging.error(f"Error displaying image on EPD: {e}")
    finally:
        epd.sleep()

def main():
    try:
        logging.info("Starting Up...")
        epd = epd2in7_V2.EPD()
        epd.init()

        # Button setup
        setup_buttons()

        # Check for software updates before starting the update loop
        check_for_software_update()

        # Start the update loop
        check_for_updates()

    except IOError as e:
        logging.error(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd.sleep()
        epd2in7_V2.epdconfig.module_exit(cleanup=True)
        exit()


if __name__ == "__main__":
    main()
