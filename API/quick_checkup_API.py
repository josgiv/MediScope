from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Load model dan dataset yang diperlukan
try:
    loaded_rf = joblib.load("../models/rf_QuickCheckup.joblib")
    symptom_Description = pd.read_csv("../model-notebook/datasets/quick_checkup/symptom_Description.csv")
    Symptom_Precaution = pd.read_csv("../model-notebook/datasets/quick_checkup/symptom_precaution.csv")
    df1 = pd.read_csv('../model-notebook/datasets/quick_checkup/Symptom-severity.csv')
except Exception as e:
    print(f"Error loading resources: {e}")

# Fungsi untuk melakukan prediksi
def predict_disease(symptoms):
    # Konversi gejala ke dalam format yang diperlukan oleh model
    symp_weights = []
    a = np.array(df1["Symptom"])
    b = np.array(df1["weight"])
    
    # Loop untuk konversi gejala menjadi bobot sesuai model
    for symptom in symptoms:
        if symptom in a:
            idx = np.where(a == symptom)[0][0]
            symp_weights.append(b[idx])
        else:
            symp_weights.append(0)  # Jika tidak ditemukan, isi dengan 0
    
    # Isi kekurangan gejala dengan 0 hingga mencapai panjang input yang diperlukan model
    symp_weights = symp_weights + [0] * (4 - len(symp_weights))  # Pastikan hanya 4 fitur
    
    # Prediksi penyakit
    try:
        pred_disease = loaded_rf.predict([symp_weights])[0]
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}
    
    # Mengambil deskripsi penyakit dan rekomendasi
    disease_desc = symptom_Description[symptom_Description['Disease'] == pred_disease].iloc[0]['Description']
    precaution_list = Symptom_Precaution[Symptom_Precaution['Disease'] == pred_disease].iloc[0, 1:].tolist()
    
    return {
        "Disease": pred_disease,
        "Description": disease_desc,
        "Precautions": precaution_list
    }

# Endpoint untuk menerima gejala dan memberikan prediksi penyakit
@app.route('/predict', methods=['POST'])
def predict():
    # Mendapatkan data gejala dari request JSON
    data = request.get_json()
    
    # Ambil gejala dari JSON dengan key khusus
    symptoms = [
        data.get("Symptom_1", ""),
        data.get("Symptom_2", ""),
        data.get("Symptom_3", ""),
        data.get("Symptom_4", "")
    ]
    
    # Validasi input
    if not any(symptoms):
        return jsonify({"error": "Input tidak valid. Pastikan format JSON berisi Symptom_1 hingga Symptom_4."}), 400

    # Melakukan prediksi
    result = predict_disease(symptoms)
    
    # Mengirimkan respons
    if "error" in result:
        return jsonify(result), 500
    else:
        return jsonify(result)

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True)
