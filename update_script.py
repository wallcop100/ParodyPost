import subprocess
import os

def update_repository():
    try:
        # Get the directory path where the script is located
        script_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_directory)
        # Pull the latest changes from the remote repository
        subprocess.run(["git", "pull"])
        print("Repository updated successfully.")
    except Exception as e:
        print(f"Error updating repository: {e}")

if __name__ == "__main__":
    update_repository()
