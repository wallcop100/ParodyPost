import os
import getpass
import subprocess
import shutil

def create_service(script_path, working_dir, user):
    service_content = f"""
[Unit]
Description=Parody Post Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 {script_path}
WorkingDirectory={working_dir}
Restart=always
User={user}

[Install]
WantedBy=multi-user.target
"""
    service_path = "/etc/systemd/system/parodypost.service"
    with open(service_path, "w") as service_file:
        service_file.write(service_content)
    return service_path

def copy_update_script(repo_url, script_dir):
    update_script_src = os.path.join(script_dir, "update_script.py")
    update_script_dst = os.path.join(os.getcwd(), "update_script.py")
    shutil.copyfile(update_script_src, update_script_dst)
    return update_script_dst


def setup_script(script_path, repo_url):
    # Clone the repository
    subprocess.run(["git", "clone", repo_url])
    repo_name = os.path.basename(repo_url).split('.')[0]
    script_dir = os.path.join(os.getcwd(), repo_name)

    # Get the current user
    current_user = getpass.getuser()

    # Create systemd service
    service_path = create_service(os.path.join(script_dir, script_path), script_dir, current_user)

    # Copy update check script
    update_script_path = copy_update_script(repo_url, script_dir)

    # Enable and start the service
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", "parodypost.service"])
    subprocess.run(["sudo", "systemctl", "start", "parodypost.service"])

if __name__ == "__main__":
    script_path = "main.py"
    repo_url = "https://github.com/wallcop100/SatericalHeadlines.git"
    setup_script(script_path, repo_url)
