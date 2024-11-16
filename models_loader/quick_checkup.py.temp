import os
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
from flask_cors import CORS 

app = Flask(__name__)

# Enable CORS for the app
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/quick_checkup/rf_QuickCheckup.joblib")
SYMP_DESC_PATH = os.path.join(BASE_DIR, "../model-notebook/datasets/quick_checkup/symptom_Description.csv")
SYMPTOM_PRECAUTION_PATH = os.path.join(BASE_DIR, "../model-notebook/datasets/quick_checkup/symptom_precaution.csv")
SYMP_SEVERITY_PATH = os.path.join(BASE_DIR, "../model-notebook/datasets/quick_checkup/Symptom-severity.csv")

try:    
    loaded_rf = joblib.load(MODEL_PATH)
    symptom_Description = pd.read_csv(SYMP_DESC_PATH)
    Symptom_Precaution = pd.read_csv(SYMPTOM_PRECAUTION_PATH)
    df1 = pd.read_csv(SYMP_SEVERITY_PATH)
except Exception as e:
    print(f"Error loading resources: {e}")

def predict_disease(symptoms):
    """Predict the disease based on input symptoms."""
    symp_weights = []
    a = np.array(df1["Symptom"])
    b = np.array(df1["weight"])

    for symptom in symptoms:
        if symptom in a:
            idx = np.where(a == symptom)[0][0]
            symp_weights.append(b[idx])
        else:
            symp_weights.append(0)  # Add zero weight for missing symptoms
    
    # Ensure input array has a fixed size for prediction
    symp_weights = symp_weights + [0] * (17 - len(symp_weights))
    
    try:
        # Make prediction
        pred_disease = loaded_rf.predict([symp_weights])[0]
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}

    try:
        # Retrieve disease description
        disease_desc = symptom_Description[symptom_Description['Disease'] == pred_disease].iloc[0]['Description']
        
        # Retrieve precautionary measures
        precaution_list = Symptom_Precaution[Symptom_Precaution['Disease'] == pred_disease].iloc[0, 1:].tolist()
    except Exception as e:
        return {"error": f"Error retrieving disease details: {e}"}
    
    return {
        "Disease": pred_disease,
        "Description": disease_desc,
        "Precautions": precaution_list
    }

@app.route('/quick-checkup', methods=['POST'])
def predict():
    """API endpoint to predict disease based on symptoms."""
    data = request.get_json()
    
    # Extract symptoms from the request JSON
    symptoms = [
        data.get(f"Symptom_{i}", "") for i in range(1, 18)
    ]
    
    # Validate the input
    if not any(symptoms):
        return jsonify({"error": "Invalid input. Ensure JSON contains Symptom_1 to Symptom_17."}), 400

    # Call the prediction function
    result = predict_disease(symptoms)
    
    # Check for errors in the prediction result
    if "error" in result:
        return jsonify(result), 500
    else:
        return jsonify(result)

if __name__ == "__main__":
    # Start the Flask app with debugging enabled
    app.run(debug=True, host='0.0.0.0', port=5010)
