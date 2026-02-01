# fc_heartd.py

import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS 

app = Flask(__name__)

# Enable CORS for the app
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


# Define the absolute path for the model and risk factors file
MODEL_PATH = os.path.join(os.getcwd(), 'assets', 'models', 'full_checkup', 'heartd_models', 'heartD_model.joblib')
RISK_FACTORS_PATH = os.path.join(os.getcwd(), 'notebooks', 'datasets', 'full_checkup', 'disease_riskFactors.csv')

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

        # Load risk factors for heart attack
        try:
            risk_factors_df = pd.read_csv(RISK_FACTORS_PATH, encoding='latin1')
            heart_attack_info = risk_factors_df[risk_factors_df['DNAME'] == 'Heart attack']

            # Extract precautions and risk factors if available
            if not heart_attack_info.empty:
                precautions_heartd = heart_attack_info.iloc[0]['PRECAU']
                risk_factors_heartd = heart_attack_info.iloc[0]['RISKFAC']
            else:
                precautions_heartd = "Informasi pencegahan tidak tersedia."
                risk_factors_heartd = "Informasi faktor risiko tidak tersedia."

        except Exception as e:
            return jsonify({'error': f'Gagal memuat data faktor risiko: {str(e)}'}), 500

        # Interpret the prediction
        if prediction == 1:
            prediction_heartd = 'Pasien kemungkinan besar tidak memiliki penyakit jantung.'
            advice_message_heartd = f"Anda dapat melakukan beberapa hal berikut untuk mencegah penyakit jantung: {precautions_heartd}"
            risk_message_heartd = f"Faktor-faktor risiko untuk penyakit jantung: {risk_factors_heartd}"
        else:
            prediction_heartd = 'Pasien kemungkinan besar memiliki penyakit jantung.'
            advice_message_heartd = f"Beberapa langkah pencegahan untuk mengurangi risiko penyakit jantung: {precautions_heartd}"
            risk_message_heartd = f"Faktor-faktor risiko untuk penyakit jantung: {risk_factors_heartd}"

        # Return the result in JSON format
        return jsonify({
            'prediksi_heartd': prediction_heartd,
            'saran_heartd': advice_message_heartd,
            'faktor_risiko_heartd': risk_message_heartd
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)
