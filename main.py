import subprocess
import sys
import os
import shutil
import logging
import platform
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting MediSCope-V1 Orchestrator (Enterprise Edition)...")
    
    processes = []
    
    # 1. Start Unified Backend
    logger.info("Launching Backend (Port 5000)...")
    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd="backend",
        shell=False # Run directly
    )
    processes.append(backend_process)
    
    # Wait for backend to be somewhat ready (optional, but good practice)
    time.sleep(2)
    
    # 2. Start Frontend
    logger.info("Launching Frontend...")
    # Using shell=True for npm/bun commands on Windows
    web_process = subprocess.Popen(
        ["bun", "run", "dev"], # Or "npm run dev"
        cwd="web",
        shell=True
    )
    processes.append(web_process)
    
    logger.info("Services started. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                logger.error(f"Backend exited with code {backend_process.returncode}")
                break
            # web_process.poll() might not work well with shell=True on windows for the actual node process, 
            # but we can check the shell handle or just wait.
            
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Shutting down...")
    finally:
        # Cleanup
        for p in processes:
            if p.poll() is None:
                if platform.system() == 'Windows':
                    logger.info(f"Killing process tree {p.pid}...")
                    os.system(f"taskkill /F /T /PID {p.pid}")
                else:
                    p.terminate()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
