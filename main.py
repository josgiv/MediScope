import subprocess
import sys
import os
import logging
import multiprocessing

# Set up logging for clear output
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(message)s')
logger = logging.getLogger(__name__)

def run_flask_app(script, log_file):
    # Remove the log file if it exists before starting
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Run the Python script and redirect output to the log file
    with open(log_file, 'w') as file:
        process = subprocess.Popen([sys.executable, script], stdout=file, stderr=subprocess.STDOUT)
    process.wait() 

def main():
    flask_apps = {
        "models_loader/disease_loader/fc_diabetes.py": "logs/fc_diabetes.log",
        "models_loader/disease_loader/fc_heartd.py": "logs/fc_heartd.log",
        "models_loader/disease_loader/fc_stroke.py": "logs/fc_stroke.log",
        "models_loader/full_checkup.py": "logs/full_checkup.log",
        "models_loader/quick_checkup.py": "logs/quick_checkup.log"
    }

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Prepare a list of processes
    processes = []
    
    for app, log_file in flask_apps.items():
        logger.info(f"Starting {app} with log output to {log_file}")
        
        # Run each Python script in a separate process using multiprocessing
        process = multiprocessing.Process(target=run_flask_app, args=(app, log_file))
        processes.append(process)
        process.start() 

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            process.terminate()
        logger.info("Processes terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
