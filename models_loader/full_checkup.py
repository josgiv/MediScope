from flask import Flask, request, jsonify
import requests
import json
import logging
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define API URLs for each full checkup model
STROKE_API_URL = os.getenv('STROKE_API_URL', 'http://localhost:5001/fc-stroke')
HEARTD_API_URL = os.getenv('HEARTD_API_URL', 'http://localhost:5002/fc-heartd')
DIABETES_API_URL = os.getenv('DIABETES_API_URL', 'http://localhost:5003/fc-diabetes')

# Separate input data for each model
def prepare_data_for_models(data):
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

    diabetes_data = {
        'glucose': data.get('glucose'),
        'bloodpressure': data.get('bloodpressure'),
        'bmi': data.get('bmi'),
        'age': data.get('age')
    }

    return stroke_data, heartd_data, diabetes_data

# Caching API results based on input data to reduce redundant calls
@lru_cache(maxsize=100)
def cached_request_prediction(api_url, model_data):
    return request_prediction(api_url, model_data)

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

# Function to execute parallel requests for predictions
def parallel_requests(url_data_pairs):
    results = {}
    with ThreadPoolExecutor() as executor:
        future_to_url = {
            executor.submit(request_prediction, url, data): url for url, data in url_data_pairs
        }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                logging.error(f"Request to {url} generated an exception: {e}")
                results[url] = {'error': f"Error in prediction request for {url}"}
    return results

# Main route to handle JSON input and route to each model
@app.route('/predict', methods=['POST'])
def predict():
    if request.is_json:
        data = request.get_json()
        stroke_data, heartd_data, diabetes_data = prepare_data_for_models(data)

        # Prepare URL-data pairs for parallel requests
        url_data_pairs = [
            (STROKE_API_URL, stroke_data),
            (HEARTD_API_URL, heartd_data),
            (DIABETES_API_URL, diabetes_data)
        ]

        # Execute requests in parallel
        model_results = parallel_requests(url_data_pairs)

        # Update combined_results to access the correct key
        combined_results = {
            'stroke_prediction': model_results[STROKE_API_URL].get('stroke_prediction') or model_results[STROKE_API_URL].get('error', 'Error with stroke model'),
            'heart_disease_prediction': model_results[HEARTD_API_URL].get('prediction') or model_results[HEARTD_API_URL].get('error', 'Error with heart disease model'),
            'diabetes_prediction': model_results[DIABETES_API_URL].get('prediction') or model_results[DIABETES_API_URL].get('error', 'Error with diabetes model')
        }

        return jsonify(combined_results)
    else:
        return jsonify({"error": "Request must be JSON"}), 400

# Run the Flask app with a specific timeout to handle long requests
if __name__ == "__main__":
    app.run(debug=True, port=5000)
