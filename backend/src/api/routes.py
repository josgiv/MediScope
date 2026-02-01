from flask import Blueprint, request, jsonify
from src.services.diabetes_service import DiabetesService
from src.services.heart_service import HeartService
from src.services.stroke_service import StrokeService
from src.services.quick_checkup_service import QuickCheckupService
from src.utils.logger import setup_logger

# Define Blueprint
bp = Blueprint('api', __name__)
logger = setup_logger(__name__)

# -- Service Initialization --
# We initialize services once at module level to keep the app fast.
# If these fail, we log critical errors but allow the app to start so `/health` still works.
try:
    diabetes_service = DiabetesService()
    heart_service = HeartService()
    stroke_service = StrokeService()
    quick_service = QuickCheckupService()
except Exception as e:
    logger.critical(f"Failed to initialize one or more services: {e}")

@bp.route('/full-checkup', methods=['POST'])
def full_checkup():
    """
    Aggregates predictions from Stroke, Heart, and Diabetes models.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
        
    data = request.get_json()
    logger.info("Processing Full Checkup request...")
    
    # Run predictions sequentially (could be parallelized if latency is an issue, 
    # but for local ML models this is usually micro-seconds).
    
    stroke_res = stroke_service.predict(data)
    heart_res = heart_service.predict(data)
    diabetes_res = diabetes_service.predict(data)
    
    # Structure the response to match what the frontend expects
    response_payload = {
        'results': {
            'Stroke': {
                'Prediksi': stroke_res.get('prediksi_stroke', 'Error'),
                'Saran': stroke_res.get('saran_stroke', 'N/A'),
                'Faktor Risiko': stroke_res.get('faktor_risiko_stroke', 'N/A')
            },
            'Heart Disease': {
                'Prediksi': heart_res.get('prediksi_heartd', 'Error'),
                'Saran': heart_res.get('saran_heartd', 'N/A'),
                'Faktor Risiko': heart_res.get('faktor_risiko_heartd', 'N/A')
            },
            'Diabetes': {
                'Prediksi': diabetes_res.get('prediksi_diabetes', 'Error'),
                'Saran': diabetes_res.get('saran_diabetes', 'N/A'),
                'Faktor Risiko': diabetes_res.get('faktor_risiko_diabetes', 'N/A')
            }
        }
    }
    
    return jsonify(response_payload), 200

@bp.route('/quick-checkup', methods=['POST'])
def quick_checkup():
    """
    Simple symptom-based checkup.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
        
    data = request.get_json()
    
    # Extract known symptom keys (Symptom_1 ... Symptom_17)
    # The frontend usually sends up to 4 or 5, but our model supports 17 slots.
    symptoms = []
    for i in range(1, 18):
        val = data.get(f"Symptom_{i}")
        if val:
            symptoms.append(val)
    
    if not symptoms:
         return jsonify({"error": "No symptoms provided."}), 400
         
    result = quick_service.predict(symptoms)
    
    if result.get('error'):
        return jsonify(result), 500
        
    return jsonify(result), 200

# -- Legacy / Individual Endpoints for Debugging --
# These can be useful if we want to test models in isolation without running the full aggregator.

@bp.route('/fc-stroke', methods=['POST'])
def check_stroke_only():
    return jsonify(stroke_service.predict(request.get_json() or {}))

@bp.route('/fc-heartd', methods=['POST'])
def check_heart_only():
    return jsonify(heart_service.predict(request.get_json() or {}))

@bp.route('/fc-diabetes', methods=['POST'])
def check_diabetes_only():
    return jsonify(diabetes_service.predict(request.get_json() or {}))
