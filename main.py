import subprocess
import sys
import os
import logging
import multiprocessing
import platform
from flask_cors import CORS

# Set up logging for clear output
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(message)s')
logger = logging.getLogger(__name__)

def run_flask_app(script, log_file):
    """Run Flask app in background with logging and CORS injection."""
    if os.path.exists(log_file):
        os.remove(log_file)

    logger.info(f"Starting Flask app {script} with log output to {log_file}")
    with open(script, 'r') as f:
        code = f.read()
        if 'from flask import Flask' in code:
            if 'from flask_cors import CORS' not in code:
                logger.info(f"Injecting Flask-CORS into {script}")
                cors_injection = "\nfrom flask_cors import CORS\napp = Flask(__name__)\nCORS(app)\n"
                code = code.replace("app = Flask(__name__)", cors_injection)

            temp_script = f"{script}.temp"
            with open(temp_script, 'w') as temp:
                temp.write(code)
            script = temp_script

    # Configure Popen based on OS
    process = None
    if platform.system() == 'Windows':
        with open(log_file, 'w') as file:
            process = subprocess.Popen([sys.executable, script], stdout=file, stderr=subprocess.STDOUT, shell=True)
    else:
        with open(log_file, 'w') as file:
            process = subprocess.Popen([sys.executable, script], stdout=file, stderr=subprocess.STDOUT)
    
    return process

def install_next_if_needed():
    """Check if Next.js is installed, if not, install it in 'web' directory."""
    web_dir = "web"
    package_path = os.path.join(web_dir, "node_modules", "next")
    
    # Check if Next.js is already installed
    if not os.path.exists(package_path):
        logger.info("Next.js is not installed. Starting installation...")
        # Install Next.js and related dependencies (for cross-platform compatibility)
        install_command = "npm install next@latest react@latest react-dom@latest" if platform.system() != "Windows" else "npm install next"
        subprocess.run(install_command, shell=True, cwd=web_dir)
        
        logger.info("Next.js has been successfully installed.")
    else:
        logger.info("Next.js is already installed. Skipping installation.")

def run_npm_dev():
    """Ensure Next.js is installed and run npm dev server."""
    install_next_if_needed()
    logger.info("Starting Next.js development server.")
    
    # Running development server command for Next.js (cross-platform)
    command = "npm run dev" if platform.system() != "Windows" else "npm run dev"
    
    # Start the Next.js dev server process
    process = subprocess.Popen(command, shell=True, cwd="web", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Capture and log output of the Next.js server to console
    for stdout_line in iter(process.stdout.readline, b''):
        logger.info(stdout_line.decode('utf-8').strip())  # decode stdout line to str and log it

    # Wait for the process to finish
    process.stdout.close()
    process.wait()

def run_all_flask_apps():
    """Start all Flask apps using multiprocessing."""
    flask_apps = {
        "models_loader/disease_loader/fc_diabetes.py": "logs/fc_diabetes.log",
        "models_loader/disease_loader/fc_heartd.py": "logs/fc_heartd.log",
        "models_loader/disease_loader/fc_stroke.py": "logs/fc_stroke.log",
        "models_loader/full_checkup.py": "logs/full_checkup.log",
        "models_loader/quick_checkup.py": "logs/quick_checkup.log"
    }

    processes = []
    # Start each Flask application in a separate process
    for app, log_file in flask_apps.items():
        process = multiprocessing.Process(target=run_flask_app, args=(app, log_file))
        processes.append(process)
        process.start()

    return processes

def main():
    """Main function to run Flask apps and npm server concurrently."""
    os.makedirs("logs", exist_ok=True)

    # Run Flask applications in parallel
    logger.info("Starting Flask applications...")
    flask_processes = run_all_flask_apps()
    logger.info("Starting npm dev server in 'web' directory")
    npm_process = multiprocessing.Process(target=run_npm_dev)
    npm_process.start()

    flask_processes.append(npm_process)

    try:
        for process in flask_processes:
            process.join()
    except KeyboardInterrupt:
        for process in flask_processes:
            process.terminate()
        logger.info("Processes terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
