import subprocess
import sys
import os
import logging
import multiprocessing
import platform
from flask_cors import CORS  # Tambahan untuk Flask CORS

# Set up logging for clear output
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(message)s')
logger = logging.getLogger(__name__)

def run_flask_app(script, log_file):
    """Run Flask app in background with logging and CORS injection."""
    # Remove the log file if it exists before starting
    if os.path.exists(log_file):
        os.remove(log_file)

    logger.info(f"Starting Flask app {script} with log output to {log_file}")
    with open(script, 'r') as f:
        code = f.read()
        if 'from flask import Flask' in code:
            # Tambahkan CORS jika belum diimplementasikan
            if 'from flask_cors import CORS' not in code:
                logger.info(f"Injecting Flask-CORS into {script}")
                cors_injection = "\nfrom flask_cors import CORS\napp = Flask(__name__)\nCORS(app)\n"
                code = code.replace("app = Flask(__name__)", cors_injection)

            temp_script = f"{script}.temp"
            with open(temp_script, 'w') as temp:
                temp.write(code)
            script = temp_script

    # Configure Popen based on OS
    if platform.system() == 'Windows':
        with open(log_file, 'w') as file:
            process = subprocess.Popen([sys.executable, script], stdout=file, stderr=subprocess.STDOUT, shell=True)
    else:
        with open(log_file, 'w') as file:
            process = subprocess.Popen([sys.executable, script], stdout=file, stderr=subprocess.STDOUT)
    
    process.wait()

    # Clean up temporary script
    if script.endswith('.temp'):
        os.remove(script)

def install_next_if_needed():
    """Check if Next.js is installed, if not, install it."""
    web_dir = "web"
    package_path = os.path.join(web_dir, "node_modules", "next")
    
    if not os.path.exists(package_path):
        logger.info("Next.js belum terinstall. Memulai instalasi...")
        install_command = "npm install" if platform.system() != "Windows" else "npm install"
        subprocess.run(install_command, shell=True, cwd=web_dir)
        logger.info("Next.js berhasil diinstall.")
    else:
        logger.info("Next.js sudah terinstall. Langsung menjalankan server dev.")

def run_npm_dev():
    """Ensure Next.js is installed and run npm dev server."""
    install_next_if_needed()
    logger.info("Starting Next.js development server.")
    command = "npm run dev" if platform.system() != "Windows" else "npm run dev"
    process = subprocess.Popen(command, shell=True, cwd="web")
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
    for app, log_file in flask_apps.items():
        process = multiprocessing.Process(target=run_flask_app, args=(app, log_file))
        processes.append(process)
        process.start()

    return processes

def main():
    """Main function to run Flask apps and npm server concurrently."""
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Run Flask applications in parallel
    logger.info("Starting Flask applications...")
    flask_processes = run_all_flask_apps()

    # Run npm development server in parallel
    logger.info("Starting npm dev server in 'web' directory")
    npm_process = multiprocessing.Process(target=run_npm_dev)
    npm_process.start()

    # Add the npm process to the list of processes to join
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
