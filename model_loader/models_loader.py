from flask import Flask, request, jsonify
import requests
import json
import logging
import time

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define API URLs for each full checkup model
STROKE_API_URL = 'http://localhost:5001/fc-stroke'
HEARTD_API_URL = 'http://localhost:5002/fc-heartd'
DIABETES_API_URL = 'http://localhost:5003/fc-diabetes'

# Separate input data for each model
def prepare_data_for_models(data):
    # A. Stroke-specific data
    stroke_data = {
        'age': data.get('age'),
        'maritalstatus': data.get('maritalstatus'),
        'sex': data.get('sex'),
        'bmi': data.get('bmi'),
        'glucose': data.get('glucose'),
        'smoke': data.get('smoke'),
        'hypertension': data.get('hypertension'),
        'heartdis': data.get('heartdis')
    }

    # B. Heart Disease-specific data
    heartd_data = {
        'age': data.get('age'),
        'sex': data.get('sex'),
        'cp': data.get('cp'),
        'bloodpressure': data.get('bloodpressure'),
        'chol': data.get('chol'),
        'fbs': data.get('fbs'),
        'restecg': data.get('restecg'),
        'thalach': data.get('thalach'),
        'exang': data.get('exang'),
        'oldpeak': data.get('oldpeak'),
        'slope': data.get('slope'),
        'ca': data.get('ca'),
        'thal': data.get('thal')
    }

    # C. Diabetes-specific data
    diabetes_data = {
        'glucose': data.get('glucose'),
        'bloodpressure': data.get('bloodpressure'),
        'bmi': data.get('bmi'),
        'age': data.get('age')
    }

    return stroke_data, heartd_data, diabetes_data

# Function to make a POST request to an API endpoint with retries
def request_prediction(api_url, model_data, retries=3, delay=2):
    for i in range(retries):
        try:
            logging.info(f"Attempt {i+1}: Requesting prediction from {api_url}")
            response = requests.post(api_url, json=model_data, timeout=5)
            response.raise_for_status()
            logging.info(f"Received response from {api_url}: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {i+1} failed for {api_url}: {e}")
            time.sleep(delay)  # Wait before retrying
    return {'error': f"Failed to connect to {api_url} after {retries} retries"}

# Main route to handle JSON input and route to each model
@app.route('/predict', methods=['POST'])
def predict():
    if request.is_json:
        data = request.get_json()
        stroke_data, heartd_data, diabetes_data = prepare_data_for_models(data)
        
        stroke_result = request_prediction(STROKE_API_URL, stroke_data)
        heartd_result = request_prediction(HEARTD_API_URL, heartd_data)
        diabetes_result = request_prediction(DIABETES_API_URL, diabetes_data)
        
 # Update combined_results to access the correct key
        combined_results = {
            'stroke_prediction': stroke_result.get('stroke_prediction') or stroke_result.get('error', 'Error with stroke model'),
            'heart_disease_prediction': heartd_result.get('prediction') or heartd_result.get('error', 'Error with heart disease model'),
            'diabetes_prediction': diabetes_result.get('prediction') or diabetes_result.get('error', 'Error with diabetes model')
        }

        
        return jsonify(combined_results)
    else:
        return jsonify({"error": "Request must be JSON"}), 400

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
