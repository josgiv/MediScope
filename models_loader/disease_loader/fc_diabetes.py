import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import joblib
import os
import logging
from sklearn.preprocessing import MinMaxScaler

# Initialize Flask app
app = Flask(__name__)

# Set up logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)  # Ensure the logs directory exists
logging.basicConfig(filename=os.path.join(log_dir, 'fc_diabetes.log'),
                    level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Print current working directory and model path for debugging
logger.info("Starting fc_diabetes service.")
logger.info(f"Current working directory: {os.getcwd()}")

# Define the absolute path for the model and dataset
MODEL_PATH = os.path.join(os.getcwd(), 'models', 'full_checkup', 'diabetes_models', 'svc_diabetes.joblib')
DATASET_PATH = os.path.join(os.getcwd(), 'model-notebook', 'datasets', 'full_checkup', 'diabetes-dataset.csv')

logger.info(f"Model path: {MODEL_PATH}")
logger.info(f"Dataset path: {DATASET_PATH}")

# Load the trained model (SVC) using joblib
try:
    model = joblib.load(MODEL_PATH)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

# Load and preprocess the dataset
try:
    dataset = pd.read_csv(DATASET_PATH)
    logger.info("Dataset loaded successfully.")
except Exception as e:
    logger.error(f"Error loading dataset: {e}")
    raise

# Select relevant features from the dataset for scaling
dataset_X = dataset.iloc[:, [1, 2, 5, 7]].values

# Apply MinMax scaling
sc = MinMaxScaler(feature_range=(0, 1))
dataset_scaled = sc.fit_transform(dataset_X)
logger.info("Dataset scaling completed.")

@app.route('/fc-diabetes', methods=['POST'])
def predict():
    logger.info("Received a prediction request.")

    # Get input from JSON request body
    data = request.get_json()

    # Extract feature values from the JSON data
    try:
        # Ensure JSON data contains all necessary features
        glucose = float(data['glucose'])
        blood_pressure = float(data['bloodpressure'])
        bmi = float(data['bmi'])
        age = float(data['age'])

        float_features = [glucose, blood_pressure, bmi, age]
        final_features = [np.array(float_features)]

        # Log the received features
        logger.info(f"Input features: {float_features}")

        # Transform features using MinMaxScaler
        scaled_features = sc.transform(final_features)

        # Predict using the model
        prediction = model.predict(scaled_features)

        # Interpretation of the prediction
        if prediction == 1:
            pred = "You have Diabetes, please consult a Doctor."
        else:
            pred = "You don't have Diabetes."

        # Log the prediction result
        logger.info(f"Prediction result: {pred}")

        # Return prediction as JSON response
        return jsonify({'prediction': pred})

    except KeyError as e:
        logger.error(f"Missing key in input data: {e}")
        return jsonify({'error': f'Missing key: {str(e)}'}), 400
    except ValueError as e:
        logger.error(f"Invalid value in input data: {e}")
        return jsonify({'error': f'Invalid value: {str(e)}'}), 400

if __name__ == "__main__":
    logger.info("Starting Flask app.")
    app.run(debug=True, host='0.0.0.0', port=5003)
