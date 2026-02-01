# Import necessary libraries
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import joblib
import os
import logging
from sklearn.preprocessing import MinMaxScaler
from flask_cors import CORS 

app = Flask(__name__)

# Enable CORS for the app
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Setup logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True) 
logging.basicConfig(filename=os.path.join(log_dir, 'fc_diabetes.log'),
                    level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting fc_diabetes service.")
logger.info(f"Current working directory: {os.getcwd()}")

# Define absolute paths for model and dataset
MODEL_PATH = os.path.join(os.getcwd(), 'assets', 'models', 'full_checkup', 'diabetes_models', 'svc_diabetes.joblib')
DATASET_PATH = os.path.join(os.getcwd(), 'notebooks', 'datasets', 'full_checkup', 'diabetes-dataset.csv')
RISK_FACTORS_PATH = os.path.join(os.getcwd(), 'notebooks', 'datasets', 'full_checkup', 'disease_riskFactors.csv')

logger.info(f"Model path: {MODEL_PATH}")
logger.info(f"Dataset path: {DATASET_PATH}")
logger.info(f"Risk factors path: {RISK_FACTORS_PATH}")

# Load trained model (SVC) using joblib
try:
    model_diabetes = joblib.load(MODEL_PATH)
    logger.info("Model successfully loaded.")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

# Load and process dataset
try:
    dataset_diabetes = pd.read_csv(DATASET_PATH)
    logger.info("Dataset successfully loaded.")
except Exception as e:
    logger.error(f"Error loading dataset: {e}")
    raise

# Select relevant features for scaling
dataset_X_diabetes = dataset_diabetes.iloc[:, [1, 2, 5, 7]].values

# Apply MinMax scaling
scaler_diabetes = MinMaxScaler(feature_range=(0, 1))
dataset_scaled_diabetes = scaler_diabetes.fit_transform(dataset_X_diabetes)
logger.info("Dataset scaling completed.")

@app.route('/fc-diabetes', methods=['POST'])
def predict_diabetes():
    logger.info("Received prediction request.")

    # Get input from JSON request body
    data = request.get_json()

    # Extract feature values from JSON data
    try:
        # Make sure the JSON data contains all necessary features
        glucose_level = float(data['glucose'])
        blood_pressure_level = float(data['bloodpressure'])
        bmi_level = float(data['bmi'])
        age_value = float(data['age'])

        input_features = [glucose_level, blood_pressure_level, bmi_level, age_value]
        features_final = [np.array(input_features)]

        # Log received features
        logger.info(f"Input features: {input_features}")

        # Transform features using MinMaxScaler
        scaled_features_diabetes = scaler_diabetes.transform(features_final)

        # Predict using the model
        prediction_diabetes = model_diabetes.predict(scaled_features_diabetes)

        # Try to load the diabetes risk factors data
        try:
            risk_factors_df = pd.read_csv(RISK_FACTORS_PATH, encoding='latin1')
            logger.info("Risk factors data successfully loaded.")
        except Exception as e:
            logger.error(f"Error loading risk factors data: {e}")
            return jsonify({'error': 'Failed to load risk factors data'}), 500

        # Search for diabetes-related information
        diabetes_info = risk_factors_df[risk_factors_df['DNAME'] == 'Diabetes']
        if not diabetes_info.empty:
            precautions_diabetes = diabetes_info.iloc[0]['PRECAU']
            risk_factors_diabetes = diabetes_info.iloc[0]['RISKFAC']
        else:
            precautions_diabetes = "Prevention information is not available."
            risk_factors_diabetes = "Risk factor information is not available."

        # Interpret prediction
        if prediction_diabetes == 1:
            prediction_message_diabetes = "Anda berkemungkinan terkena Diabetes, harap konsultasikan dengan dokter."
            advice_message_diabetes = f"Anda dapat melakukan beberapa hal berikut untuk menurunkan risiko diabetes: {precautions_diabetes}"
            risk_message_diabetes = f"Hal-hal yang menyebabkan dapat terkena diabetes: {risk_factors_diabetes}"
        else:
            prediction_message_diabetes = "Anda tidak berkemungkinan terkena Diabetes."
            advice_message_diabetes = f"Anda tetap dapat melakukan hal ini untuk mencegah terkena diabetes: {precautions_diabetes}"
            risk_message_diabetes = f"Hal-hal yang menyebabkan dapat terkena diabetes: {risk_factors_diabetes}"

        # Log prediction result
        logger.info(f"Prediction result: {prediction_message_diabetes}")

        # Return prediction as JSON response
        return jsonify({
            'prediksi_diabetes': prediction_message_diabetes,
            'saran_diabetes': advice_message_diabetes,
            'faktor_risiko_diabetes': risk_message_diabetes
        })

    except KeyError as e:
        logger.error(f"Missing key in input data: {e}")
        return jsonify({'error': f'Missing key: {str(e)}'}), 400
    except ValueError as e:
        logger.error(f"Invalid value in input data: {e}")
        return jsonify({'error': f'Invalid value: {str(e)}'}), 400

if __name__ == "__main__":
    logger.info("Starting Flask app.")
    app.run(debug=True, host='0.0.0.0', port=5003)
