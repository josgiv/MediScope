import subprocess
import sys
import os
import shutil
import logging
import multiprocessing
import platform

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Define directories
TEMP_DIR = "models_loader/temp"
LOG_DIR = "logs"

def setup_temp_dir():
    # Create a dedicated directory for temporary files
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    logger.info(f"Temporary files directory set up at: {TEMP_DIR}")

def cleanup_temp_dir():
    # Remove the temporary files directory if it exists
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        logger.info("Temporary files directory removed.")

def run_flask_app(script, log_file):
    # Start Flask app in background with log and CORS handling
    if os.path.exists(log_file):
        os.remove(log_file)

    logger.info(f"Starting Flask app {script} with log output to {log_file}")

    # Inject Flask-CORS if not already present
    temp_script_path = os.path.join(TEMP_DIR, os.path.basename(script) + ".temp")
    with open(script, 'r') as f:
        code = f.read()
        if 'from flask import Flask' in code and 'from flask_cors import CORS' not in code:
            logger.info(f"Injecting Flask-CORS into {script}")
            cors_injection = "\nfrom flask_cors import CORS\napp = Flask(__name__)\nCORS(app)\n"
            code = code.replace("app = Flask(__name__)", cors_injection)

            with open(temp_script_path, 'w') as temp_script:
                temp_script.write(code)
            script = temp_script_path

    # Run the Flask script with logging
    with open(log_file, 'w') as log:
        process = subprocess.Popen(
            [sys.executable, script],
            stdout=log,
            stderr=subprocess.STDOUT,
            shell=(platform.system() == 'Windows')
        )
    return process

def install_next_and_dependencies():
    web_dir = "web"
    package_json_path = os.path.join(web_dir, "package.json")
    node_modules_path = os.path.join(web_dir, "node_modules")

    if not os.path.exists(package_json_path):
        logger.error(f"No package.json found in {web_dir}. Ensure the directory is properly set up.")
        sys.exit(1)

    if not os.path.exists(node_modules_path):
        logger.info("Node modules not found. Running 'npm install'...")
        subprocess.run("npm install", shell=True, cwd=web_dir)
        logger.info("NPM dependencies installed successfully.")
    else:
        logger.info("Node modules already installed. Skipping 'npm install'.")

def run_npm_dev():
    install_next_and_dependencies()
    logger.info("Starting Next.js development server...")
    command = "npm run dev"
    process = subprocess.Popen(command, shell=True, cwd="web", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for stdout_line in iter(process.stdout.readline, b''):
        logger.info(stdout_line.decode('utf-8').strip())

    process.stdout.close()
    process.wait()

def run_all_flask_apps():
    flask_apps = {
        "models_loader/disease_loader/fc_diabetes.py": f"{LOG_DIR}/fc_diabetes.log",
        "models_loader/disease_loader/fc_heartd.py": f"{LOG_DIR}/fc_heartd.log",
        "models_loader/disease_loader/fc_stroke.py": f"{LOG_DIR}/fc_stroke.log",
        "models_loader/full_checkup.py": f"{LOG_DIR}/full_checkup.log",
        "models_loader/quick_checkup.py": f"{LOG_DIR}/quick_checkup.log"
    }

    processes = []
    for app, log_file in flask_apps.items():
        process = multiprocessing.Process(target=run_flask_app, args=(app, log_file))
        processes.append(process)
        process.start()

    return processes

def main():
    # Main function to manage Flask and Next.js apps
    os.makedirs(LOG_DIR, exist_ok=True)
    setup_temp_dir()

    logger.info("Starting Flask applications...")
    flask_processes = run_all_flask_apps()

    logger.info("Starting npm development server...")
    npm_process = multiprocessing.Process(target=run_npm_dev)
    npm_process.start()

    flask_processes.append(npm_process)

    try:
        for process in flask_processes:
            process.join()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Terminating processes...")
        for process in flask_processes:
            process.terminate()
    finally:
        cleanup_temp_dir()
        logger.info("Exiting program.")

if __name__ == "__main__":
    main()
