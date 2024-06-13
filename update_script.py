import os
import subprocess
import requests
import zipfile
import shutil
import logging
import fcntl

# Constants for GitHub repository
GITHUB_REPO = "wallcop100/ParodyPost"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
LOCAL_VERSION_FILE = os.path.join(os.path.dirname(__file__), "version.txt")
LOCK_FILE = os.path.join(os.path.dirname(__file__), "update_script.lock")

# Set up logging
logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'update_script.log'),
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_latest_release_info():
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching latest release info: {e}")
        return None

def download_latest_release(download_url, download_path):
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
        logging.info("Latest release downloaded successfully.")
    except requests.RequestException as e:
        logging.error(f"Error downloading latest release: {e}")

def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all contents preserving directory structure
            zip_ref.extractall(path=extract_to)

        # After extraction, find the subdirectory created by GitHub and move its contents
        extracted_files = os.listdir(extract_to)
        if len(extracted_files) == 1 and os.path.isdir(os.path.join(extract_to, extracted_files[0])):
            extracted_subdir = os.path.join(extract_to, extracted_files[0])
            for item in os.listdir(extracted_subdir):
                item_path = os.path.join(extracted_subdir, item)
                shutil.move(item_path, extract_to)
            os.rmdir(extracted_subdir)  # Remove the empty extracted subdirectory

        logging.info(f"Release extracted successfully to {extract_to}.")
    except zipfile.BadZipFile as e:
        logging.error(f"Error extracting zip file: {e}")
    except Exception as e:
        logging.error(f"Error extracting zip file: {e}")

def update_files(src_dir, dest_dir):
    try:
        # List of files/directories to exclude from deletion
        exclude_files = ['update_script.log', 'latest_release', 'latest_release.zip', 'version.txt']  # Add more files/directories as needed

        # Remove old files, excluding those in exclude_files
        for item in os.listdir(dest_dir):
            item_path = os.path.join(dest_dir, item)
            if item in exclude_files:
                continue  # Skip this file/directory
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

        # Copy new files
        for item in os.listdir(src_dir):
            src_item_path = os.path.join(src_dir, item)
            dest_item_path = os.path.join(dest_dir, item)
            if os.path.isdir(src_item_path):
                shutil.copytree(src_item_path, dest_item_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_item_path, dest_item_path)

        logging.info("Files updated successfully.")
    except Exception as e:
        logging.error(f"Error updating files: {e}")

def update_version_file(version):
    try:
        with open(LOCAL_VERSION_FILE, 'w') as file:
            file.write(version)
        logging.info("version.txt updated successfully.")
    except IOError as e:
        logging.error(f"Error updating version.txt: {e}")

def get_local_version():
    try:
        if os.path.exists(LOCAL_VERSION_FILE):
            with open(LOCAL_VERSION_FILE, 'r') as file:
                return file.read().strip()
        else:
            return None
    except IOError as e:
        logging.error(f"Error reading version.txt: {e}")
        return None

def update_script(repo_dir):
    lock_file = None
    try:
        # Acquire lock
        lock_file = open(LOCK_FILE, 'w')
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)

        # Stop the service
        subprocess.run(["sudo", "systemctl", "stop", "parodypost_main.service"])

        # Get latest release info
        release_info = get_latest_release_info()
        if not release_info:
            return

        # Check current version
        current_version = get_local_version()
        latest_version = release_info['tag_name']

        if current_version == latest_version:
            logging.info(f"Current version ({current_version}) is up to date. No need to update.")
            subprocess.run(["sudo", "systemctl", "start", "parodypost_main.service"])
            return

        # Stop the service
        subprocess.run(["sudo", "pkill", "-9", "-f", "main.py"])

        # Download the latest release
        download_url = release_info['zipball_url']
        download_path = os.path.join(repo_dir, "latest_release.zip")
        download_latest_release(download_url, download_path)

        # Extract the downloaded release
        extract_path = os.path.join(repo_dir, "latest_release")
        extract_zip(download_path, extract_path)
        logging.info(f"Release extracted successfully to {extract_path}.")

        # Update files
        update_files(extract_path, repo_dir)

        # Start the service
        subprocess.run(["sudo", "systemctl", "restart", "parodypost_main.service"])

        # Clean up
        os.remove(download_path)
        shutil.rmtree(extract_path)

        # Update version file
        update_version_file(latest_version)
        logging.info("Script updated successfully.")
    except OSError as e:
        if e.errno == 11:  # EAGAIN, indicating the lock is already held
            logging.error("Another instance of the update script is already running.")
        else:
            logging.error(f"Error acquiring lock: {e}")
    except Exception as e:
        logging.error(f"Error updating script: {e}")
        subprocess.run(["sudo", "systemctl", "restart", "parodypost_main.service"])
    finally:
        if lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()

if __name__ == "__main__":
    # Specify the directory where the repository is located
    repo_dir = os.path.abspath(os.path.dirname(__file__))
    update_script(repo_dir)
