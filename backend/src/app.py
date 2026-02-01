from flask import Flask
from flask_cors import CORS
from src.utils.logger import setup_logger
from src.api.routes import bp

logger = setup_logger(__name__)

def create_app():
    logger.info("Initializing Flask App...")
    app = Flask(__name__)
    
    # Enable CORS for all routes (Unified)
    # allowing 3000 (React devs), 3001 (Next.js fallback), 5000 (self)
    CORS(app, resources={r"/*": {"origins": "*"}}) # Allow all for simplicity in dev/competition env, or strict list
    
    app.register_blueprint(bp)
    
    @app.route('/health')
    def health():
        return {"status": "ok"}
        
    return app
