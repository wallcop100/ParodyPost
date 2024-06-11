import os
import subprocess


def update_script(repo_dir):
    try:
        # Navigate to the root directory of the cloned repository
        os.chdir(repo_dir)

        # Pull changes from the remote repository
        subprocess.run(["git", "pull"])

        # Navigate to the src directory
        src_dir = os.path.join(repo_dir, "src")
        os.chdir(src_dir)

        # Pull changes from the remote repository for the src directory only
        subprocess.run(["git", "pull"])

        print("Script updated successfully.")
    except Exception as e:
        print(f"Error updating script: {e}")


if __name__ == "__main__":
    # Specify the directory where the repository is cloned
    repo_dir = os.path.abspath(os.path.dirname(__file__))
    update_script(repo_dir)
