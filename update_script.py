import os
import subprocess

def update_script():
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Change to the directory where this script is located
        subprocess.run(["git", "fetch", "--all"])  # Fetch changes from the remote repository
        subprocess.run(["git", "reset", "--hard", "origin/main"])  # Reset local changes to match the remote repository
        print("Repository updated successfully.")
    except Exception as e:
        print(f"Error updating repository: {e}")

if __name__ == "__main__":
    update_script()
