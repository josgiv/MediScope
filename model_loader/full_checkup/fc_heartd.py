import os
import joblib
import numpy as np
from flask import Flask, request, jsonify

# Define the Flask application
app = Flask(__name__)

# Define the absolute path for the model
MODEL_PATH = os.path.join(os.getcwd(), 'models', 'full_checkup', 'heartd_models', 'heartD_model.joblib')

# Load the ML model
model = joblib.load(MODEL_PATH)

# Print current working directory and model path for debugging
print("Current working directory: ", os.getcwd())
print("Model loaded from: ", MODEL_PATH)

# Define the prediction endpoint
@app.route('/fc-heartd', methods=['POST'])
def predict():
    try:
        # Get JSON input from user
        data = request.get_json()

        # Mapping input fields
        features = [
            data['age'],
            data['sex'],
            data['cp'],
            data['bloodpressure'],
            data['chol'],
            data['fbs'],
            data['restecg'],
            data['thalach'],
            data['exang'],
            data['oldpeak'],
            data['slope'],
            data['ca'],
            data['thal']
        ]
        
        # Convert features to numpy array
        array_features = np.array(features).reshape(1, -1)

        # Perform prediction
        prediction = model.predict(array_features)

        # Return result
        if prediction == 1:
            result = 'The patient is not likely to have heart disease.'
        else:
            result = 'The patient is likely to have heart disease.'

        # Return the result in JSON format
        return jsonify({'prediction': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
