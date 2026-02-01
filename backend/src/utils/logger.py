import logging
import os
import sys

def setup_logger(name=__name__, log_file='app.log', level=logging.INFO):
    """
    Setup a centralized logger.
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s]: %(message)s')
    
    handler = logging.FileHandler(os.path.join(log_dir, log_file))
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)
        logger.addHandler(console_handler)
        
    return logger
