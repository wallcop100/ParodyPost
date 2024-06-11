import os
import subprocess
import shutil

def create_service(script_path):
    service_content = f"""
[Unit]
Description=Parody Post Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 {script_path}
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
"""
    service_path = "/etc/systemd/system/parodypost.service"
    with open(service_path, "w") as service_file:
        service_file.write(service_content)
    return service_path

def create_update_script(repo_url, script_dir):
    update_script_content = f"""
import os
import subprocess

def update_script():
    try:
        os.chdir('{script_dir}')
        subprocess.run(["git", "pull"])
        print("Script updated successfully.")
    except Exception as e:
        print(f"Error updating script: {{e}}")

if __name__ == "__main__":
    update_script()
"""
    update_script_path = os.path.join(script_dir, "update_script.py")
    with open(update_script_path, "w") as update_script_file:
        update_script_file.write(update_script_content)
    return update_script_path

def setup_script(script_path, repo_url):
    # Clone the repository
    subprocess.run(["git", "clone", repo_url])
    repo_name = os.path.basename(repo_url).split('.')[0]
    script_dir = os.path.join(os.getcwd(), repo_name)

    # Create systemd service
    service_path = create_service(os.path.join(script_dir, script_path))

    # Create update check script
    update_script_path = create_update_script(repo_url, script_dir)

    # Enable and start the service
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", "parodypost.service"])
    subprocess.run(["sudo", "systemctl", "start", "parodypost.service"])

if __name__ == "__main__":
    script_path = "main.py"
    repo_url = "https://github.com/wallcop100/SatericalHeadlines.git"
    setup_script(script_path, repo_url)
