import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import joblib
import os

# Initialize Flask app
app = Flask(__name__)

# Print current working directory and model path for debugging
print("Current working directory: ", os.getcwd())

# Define the absolute path for the model and dataset
MODEL_PATH = os.path.join(os.getcwd(), 'models', 'full_checkup', 'diabetes_models', 'svc_diabetes.joblib')
DATASET_PATH = os.path.join(os.getcwd(), 'model-notebook', 'datasets', 'full_checkup', 'diabetes-dataset.csv')

print("Model path: ", MODEL_PATH)
print("Dataset path: ", DATASET_PATH)

# Load the trained model (SVC) using joblib
model = joblib.load(MODEL_PATH)

# Load and preprocess the dataset
dataset = pd.read_csv(DATASET_PATH)

# Select relevant features from the dataset for scaling
dataset_X = dataset.iloc[:, [1, 2, 5, 7]].values

# Apply MinMax scaling
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range=(0, 1))
dataset_scaled = sc.fit_transform(dataset_X)



@app.route('/fc-diabetes', methods=['POST'])
def predict():

    # Get input from JSON request body
    data = request.get_json()

    # Extract feature values from the JSON data
    try:
        # Pastikan data JSON memiliki semua fitur yang diperlukan
        glucose = float(data['glucose'])
        blood_pressure = float(data['bloodpressure'])
        bmi = float(data['bmi'])
        age = float(data['age'])

        float_features = [glucose, blood_pressure, bmi, age]
        final_features = [np.array(float_features)]

        # Transform features using MinMaxScaler
        scaled_features = sc.transform(final_features)

        # Predict using the model
        prediction = model.predict(scaled_features)

        # Interpretation of the prediction
        if prediction == 1:
            pred = "You have Diabetes, please consult a Doctor."
        else:
            pred = "You don't have Diabetes."

        # Return prediction as JSON response
        return jsonify({'prediction': pred})

    except KeyError as e:
        return jsonify({'error': f'Missing key: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': f'Invalid value: {str(e)}'}), 400


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
