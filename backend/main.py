import sys
import os

# Add backend directory to sys.path so we can import src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

app = create_app()

if __name__ == "__main__":
    logger.info("Starting Unified Backend Server on port 5000")
    # Run single process
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False) 
    # use_reloader=False to avoid double loading/looping in some environments governed by main.py
