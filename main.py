import subprocess
import sys
import os
import logging
import json

# Logging setup for clearer and structured output
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(message)s')
logger = logging.getLogger(__name__)

def run_flask_app(script, log_file):
    # Menjalankan file Python dengan subprocess, output dialihkan ke log file
    with open(log_file, 'w') as file:
        process = subprocess.Popen([sys.executable, script], stdout=file, stderr=subprocess.STDOUT)
    return process

def main():
    flask_apps = {
        "models_loader/disease_loader/fc_diabetes.py": "logs/fc_diabetes.log",
        "models_loader/disease_loader/fc_heartd.py": "logs/fc_heartd.log",
        "models_loader/disease_loader/fc_stroke.py": "logs/fc_stroke.log",
        "models_loader/full_checkup.py": "logs/full_checkup.log",
        "models_loader/quick_checkup.py": "logs/quick_checkup.log"
    }

    processes = []

    # Ensure the logs directory exists
    os.makedirs("logs", exist_ok=True)

    for app, log_file in flask_apps.items():
        logger.info(f"Starting {app} with log output to {log_file}")
        process = run_flask_app(app, log_file)
        processes.append(process)

    try:
        # Menunggu semua proses berjalan
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        # Menghentikan semua proses saat interupsi
        for process in processes:
            process.terminate()
        logger.info("Processes terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
