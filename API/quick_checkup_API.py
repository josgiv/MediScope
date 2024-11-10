from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib


app = Flask(__name__)


try:
    loaded_rf = joblib.load("../models/rf_QuickCheckup.joblib")
    symptom_Description = pd.read_csv("../model-notebook/datasets/quick_checkup/symptom_Description.csv")
    Symptom_Precaution = pd.read_csv("../model-notebook/datasets/quick_checkup/symptom_precaution.csv")
    df1 = pd.read_csv('../model-notebook/datasets/quick_checkup/Symptom-severity.csv')
except Exception as e:
    print(f"Error loading resources: {e}")

def predict_disease(symptoms):
    symp_weights = []
    a = np.array(df1["Symptom"])
    b = np.array(df1["weight"])

    for symptom in symptoms:
        if symptom in a:
            idx = np.where(a == symptom)[0][0]
            symp_weights.append(b[idx])
        else:
            symp_weights.append(0) 
    
    symp_weights = symp_weights + [0] * (17 - len(symp_weights))
    
    try:
        pred_disease = loaded_rf.predict([symp_weights])[0]
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}

    disease_desc = symptom_Description[symptom_Description['Disease'] == pred_disease].iloc[0]['Description']
    precaution_list = Symptom_Precaution[Symptom_Precaution['Disease'] == pred_disease].iloc[0, 1:].tolist()
    
    return {
        "Disease": pred_disease,
        "Description": disease_desc,
        "Precautions": precaution_list
    }

@app.route('/quick-checkup', methods=['POST'])
def predict():

    data = request.get_json()
    symptoms = [
        data.get(f"Symptom_{i}", "") for i in range(1, 18)
    ]
    if not any(symptoms):
        return jsonify({"error": "Input tidak valid. Pastikan format JSON berisi Symptom_1 hingga Symptom_17."}), 400


    result = predict_disease(symptoms)
    
    if "error" in result:
        return jsonify(result), 500
    else:
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
