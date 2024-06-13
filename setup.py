import os
import getpass
import subprocess

def create_main_service(script_path, working_dir, user):
    service_content = f"""
[Unit]
Description=Main Service for Parody Post
After=network.target

[Service]
ExecStart=/usr/bin/python3 {script_path}
WorkingDirectory={working_dir}
Restart=always
User={user}

[Install]
WantedBy=multi-user.target
"""
    service_path = "/etc/systemd/system/parodypost_main.service"
    try:
        with open(service_path, "w") as service_file:
            service_file.write(service_content)
        print(f"Service file created at {service_path}")
    except Exception as e:
        print(f"Failed to create service file: {e}")
    return service_path

def create_cron_job(script_path, user):
    cron_job = f"* * * * * {user} /usr/bin/python3 {script_path}\n"
    cron_path = "/etc/cron.d/parodypost_update_cron"
    try:
        with open(cron_path, "w") as cron_file:
            cron_file.write(cron_job)
        print(f"Cron job created at {cron_path}")
    except Exception as e:
        print(f"Failed to create cron job: {e}")
    return cron_path

def setup_script():
    # Get absolute paths to scripts
    main_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "main.py"))
    update_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "update_script.py"))

    print(f"Main script path: {main_script_path}")
    print(f"Update script path: {update_script_path}")

    # Get the current user
    current_user = getpass.getuser()
    print(f"Current user: {current_user}")

    # Create systemd service for main.py
    main_service_path = create_main_service(main_script_path, os.path.dirname(main_script_path), current_user)

    # Verify service file creation
    if os.path.exists(main_service_path):
        print(f"Service file {main_service_path} successfully created.")
    else:
        print(f"Service file {main_service_path} not found after creation attempt.")

    # Create cron job for update_script.py
    cron_path = create_cron_job(update_script_path, current_user)

    # Verify cron job creation
    if os.path.exists(cron_path):
        print(f"Cron job file {cron_path} successfully created.")
    else:
        print(f"Cron job file {cron_path} not found after creation attempt.")

    # Enable and start the main service
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", "parodypost_main.service"])
    subprocess.run(["sudo", "systemctl", "start", "parodypost_main.service"])

if __name__ == "__main__":
    setup_script()
