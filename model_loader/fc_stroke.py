from flask import Flask, request, jsonify
import joblib
import numpy as np

# Load model yang telah dilatih
model = joblib.load('models/stroke_model.joblib')  # ganti dengan nama file model yang sudah kamu simpan

# Inisiasi Flask
app = Flask(__name__)

# Endpoint untuk prediksi stroke
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)  # Menerima JSON input
    
    # Ambil data dari JSON input
    try:
        features = np.array([[
            data['gender'],
            data['age'],
            data['hypertension'],
            data['heart_disease'],
            data['ever_married'],
            data['work_type'],
            data['Residence_type'],
            data['avg_glucose_level'],
            data['bmi'],
            data['smoking_status']
        ]])
    except KeyError as e:
        return jsonify({'error': f'Missing key {e} in JSON data'}), 400

    # Prediksi menggunakan model yang telah dilatih
    prediction = model.predict(features)
    probability = model.predict_proba(features)[:, 1]

    # Kembalikan hasil prediksi sebagai JSON
    output = {
        'stroke_prediction': int(prediction[0]),
        'stroke_probability': float(probability[0])
    }
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
