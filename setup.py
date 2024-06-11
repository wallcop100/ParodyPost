import os
import getpass
import subprocess

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

def create_cron_job(script_path, user):
    cron_job = f"* * * * * {user} /usr/bin/python3 {script_path}\n"
    cron_path = "/etc/cron.d/parodypost_cron"
    with open(cron_path, "w") as cron_file:
        cron_file.write(cron_job)
    return cron_path

def setup_script():
    # Get the absolute path to update_script.py
    update_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "update_script.py"))

    # Get the current user
    current_user = getpass.getuser()

    # Create cron job
    cron_path = create_cron_job(update_script_path, current_user)

    # Enable and start the service
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", "parodypost.service"])
    subprocess.run(["sudo", "systemctl", "start", "parodypost.service"])

if __name__ == "__main__":
    setup_script()
