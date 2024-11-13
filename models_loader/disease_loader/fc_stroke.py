# fc_stroke.py

from flask import Flask, request, jsonify
import numpy as np
import os
import pandas as pd
import logging
from joblib import load

# Initialize Flask app
app = Flask(__name__)

# Set up logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, 'fc_stroke.log'),
                    level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting fc_stroke service.")
logger.info(f"Current working directory: {os.getcwd()}")

# Define paths
MODEL_PATH = os.path.join(os.getcwd(), 'models', 'full_checkup', 'stroke_model.joblib')
RISK_FACTORS_PATH = os.path.join(os.getcwd(), 'model-notebook', 'datasets', 'full_checkup', 'disease_riskFactors.csv')

# Load model
try:
    model = load(MODEL_PATH)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to load model. Error: {e}")
    raise

@app.route('/fc-stroke', methods=['POST'])
def predict():
    logger.info("Received a stroke prediction request.")
    if request.is_json:
        data = request.get_json()
        
        # Extract input features with default values
        age = data.get('age', 0)
        maritalstatus = data.get('maritalstatus', 'not married')
        worktype = data.get('Worktype', 'privatejob')
        residence = data.get('Residence', 'urban')
        sex = data.get('Sex', 'Male')
        bmi = data.get('bmi', 0.0)
        glucose = data.get('glucose', 0.0)
        smoke = data.get('Smoke', 'non-smoker')
        hypertension = data.get('Hypertension', 'nohypten')
        heartdisease = data.get('heartdis', 'noheartdis')

        # Mapping categorical values to numeric for the model
        mappings = {
            'residence': {'urban': 1, 'rural': 0},
            'sex': {'Female': 0, 'Male': 1},
            'maritalstatus': {'married': 1, 'not married': 0},
            'worktype': {'privatejob': 2, 'govtemp': 1, 'selfemp': 3},
            'smoke': {'formerly-smoked': 1, 'non-smoker': 2, 'smoker': 3},
            'hypertension': {'hypten': 1, 'nohypten': 0},
            'heartdisease': {'heartdis': 1, 'noheartdis': 0}
        }

        # Convert input features to numeric values
        residence = mappings['residence'].get(residence, 1)
        sex = mappings['sex'].get(sex, 1)
        maritalstatus = mappings['maritalstatus'].get(maritalstatus, 0)
        worktype = mappings['worktype'].get(worktype, 2)
        smoke = mappings['smoke'].get(smoke, 2)
        hypertension = mappings['hypertension'].get(hypertension, 0)
        heartdisease = mappings['heartdisease'].get(heartdisease, 0)

        # Prepare input array for prediction
        input_array = np.array([[sex, age, hypertension, heartdisease, maritalstatus, worktype, residence, glucose, bmi, smoke]], dtype='float64')
        
        # Predict stroke
        try:
            pred_stroke = model.predict(input_array)
            result = int(pred_stroke[0])

            # Load risk factors and precautions data
            try:
                risk_factors_df = pd.read_csv(RISK_FACTORS_PATH, encoding='latin1')
                logger.info("Risk factors data loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading risk factors data: {e}")
                return jsonify({'error': 'Error loading risk factors data'}), 500

            # Find Stroke-related information
            stroke_info = risk_factors_df[risk_factors_df['DNAME'] == 'Stroke']
            if not stroke_info.empty:
                precautions = stroke_info.iloc[0]['PRECAU']
                risk_factors = stroke_info.iloc[0]['RISKFAC']
            else:
                precautions = "Informasi pencegahan tidak tersedia."
                risk_factors = "Informasi faktor risiko tidak tersedia."

            # Interpretation of the prediction
            if result == 1:
                prediksi_stroke = "Anda berkemungkinan terkena Stroke, harap konsultasikan dengan dokter."
                saran_stroke = f"Anda dapat melakukan beberapa hal berikut untuk menurunkan risiko stroke: {precautions}"
                faktor_risiko_stroke = f"Hal-hal yang dapat menyebabkan stroke: {risk_factors}"
            else:
                prediksi_stroke = "Anda tidak berkemungkinan terkena Stroke."
                saran_stroke = f"Anda tetap dapat melakukan hal ini untuk mencegah stroke: {precautions}"
                faktor_risiko_stroke = f"Hal-hal yang dapat menyebabkan stroke: {risk_factors}"

            # Log the prediction result
            logger.info(f"Prediction result: {prediksi_stroke}")

            # Return prediction as JSON response
            return jsonify({
                'prediksi_stroke': prediksi_stroke,
                'saran_stroke': saran_stroke,
                'faktor_risiko_stroke': faktor_risiko_stroke
            })

        except Exception as e:
            logger.error(f"Prediction failed. Error: {e}")
            return jsonify({"error": f"Prediction failed. Error: {e}"}), 500
    else:
        logger.error("Request content-type is not JSON.")
        return jsonify({"error": "Request must be JSON"}), 400

if __name__ == "__main__":
    logger.info("Starting Flask app for Stroke prediction.")
    app.run(debug=True, host='0.0.0.0', port=5001)
