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

def copy_update_script(repo_dir):
    update_script_src = os.path.join(repo_dir, "update_script.py")
    update_script_dst = os.path.join(repo_dir, "update_script.py")  # Same as source
    shutil.copyfile(update_script_src, update_script_dst)
    return update_script_dst

def setup_script():
    # Get the absolute path to main.py
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "main.py"))

    # Get the current user
    current_user = getpass.getuser()

    # Create systemd service
    service_path = create_service(script_path, os.path.dirname(script_path), current_user)

    # Copy update check script
    update_script_path = copy_update_script(os.path.dirname(__file__))

    # Enable and start the service
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", "parodypost.service"])
    subprocess.run(["sudo", "systemctl", "start", "parodypost.service"])

    # Run the update script
    subprocess.run(["/usr/bin/python3", update_script_path])

if __name__ == "__main__":
    setup_script()
