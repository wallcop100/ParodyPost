import os
import subprocess
import requests
import zipfile
import shutil

# Constants for GitHub repository
GITHUB_REPO = "https://github.com/wallcop100/ParodyPost"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
LOCAL_VERSION_FILE = os.path.join(os.path.dirname(__file__), "version.txt")


def get_latest_release_info():
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching latest release info: {e}")
        return None


def download_latest_release(download_url, download_path):
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
        print("Latest release downloaded successfully.")
    except requests.RequestException as e:
        print(f"Error downloading latest release: {e}")


def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Release extracted successfully.")
    except zipfile.BadZipFile as e:
        print(f"Error extracting zip file: {e}")


def update_files(src_dir, dest_dir):
    try:
        # Remove old files
        for item in os.listdir(dest_dir):
            item_path = os.path.join(dest_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

        # Copy new files
        for item in os.listdir(src_dir):
            item_path = os.path.join(src_dir, item)
            shutil.move(item_path, dest_dir)
        print("Files updated successfully.")
    except Exception as e:
        print(f"Error updating files: {e}")


def update_version_file(version):
    try:
        with open(LOCAL_VERSION_FILE, 'w') as file:
            file.write(version)
        print("version.txt updated successfully.")
    except IOError as e:
        print(f"Error updating version.txt: {e}")


def update_script(repo_dir):
    try:
        # Stop the service
        subprocess.run(["sudo", "pkill", "-9", "-f", "main.py"])
        subprocess.run(["sudo", "systemctl", "stop", "parodypost.service"])

        # Get latest release info
        release_info = get_latest_release_info()
        if not release_info:
            return

        # Download the latest release
        download_url = release_info['zipball_url']
        version = release_info['tag_name']
        download_path = os.path.join(repo_dir, "latest_release.zip")
        download_latest_release(download_url, download_path)

        # Extract the downloaded release
        extract_path = os.path.join(repo_dir, "latest_release")
        extract_zip(download_path, extract_path)

        # Update files
        update_files(extract_path, repo_dir)

        # Clean up
        os.remove(download_path)
        shutil.rmtree(extract_path)

        # Update version file
        update_version_file(version)

        # Start the service
        subprocess.run(["sudo", "systemctl", "start", "parodypost.service"])

        print("Script updated successfully.")
    except Exception as e:
        print(f"Error updating script: {e}")


if __name__ == "__main__":
    # Specify the directory where the repository is located
    repo_dir = os.path.abspath(os.path.dirname(__file__))
    update_script(repo_dir)
