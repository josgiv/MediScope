# fc_diabetes.py

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import joblib
import os
import logging
from sklearn.preprocessing import MinMaxScaler

# Inisialisasi Flask app
app = Flask(__name__)

# Konfigurasi logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)  # Pastikan direktori logs tersedia
logging.basicConfig(filename=os.path.join(log_dir, 'fc_diabetes.log'),
                    level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

logger.info("Memulai layanan fc_diabetes.")
logger.info(f"Direktori kerja saat ini: {os.getcwd()}")

# Definisikan jalur absolut untuk model dan dataset
MODEL_PATH = os.path.join(os.getcwd(), 'models', 'full_checkup', 'diabetes_models', 'svc_diabetes.joblib')
DATASET_PATH = os.path.join(os.getcwd(), 'model-notebook', 'datasets', 'full_checkup', 'diabetes-dataset.csv')
RISK_FACTORS_PATH = os.path.join(os.getcwd(), 'model-notebook', 'datasets', 'full_checkup', 'disease_riskFactors.csv')

logger.info(f"Jalur model: {MODEL_PATH}")
logger.info(f"Jalur dataset: {DATASET_PATH}")
logger.info(f"Jalur faktor risiko: {RISK_FACTORS_PATH}")

# Muat model yang telah dilatih (SVC) menggunakan joblib
try:
    model_diabetes = joblib.load(MODEL_PATH)
    logger.info("Model berhasil dimuat.")
except Exception as e:
    logger.error(f"Kesalahan saat memuat model: {e}")
    raise

# Muat dan proses dataset
try:
    dataset_diabetes = pd.read_csv(DATASET_PATH)
    logger.info("Dataset berhasil dimuat.")
except Exception as e:
    logger.error(f"Kesalahan saat memuat dataset: {e}")
    raise

# Pilih fitur relevan dari dataset untuk skala
dataset_X_diabetes = dataset_diabetes.iloc[:, [1, 2, 5, 7]].values

# Terapkan MinMax scaling
scaler_diabetes = MinMaxScaler(feature_range=(0, 1))
dataset_scaled_diabetes = scaler_diabetes.fit_transform(dataset_X_diabetes)
logger.info("Skala dataset selesai.")

@app.route('/fc-diabetes', methods=['POST'])
def predict_diabetes():
    logger.info("Menerima permintaan prediksi.")

    # Ambil input dari body permintaan JSON
    data = request.get_json()

    # Ekstrak nilai fitur dari data JSON
    try:
        # Pastikan data JSON berisi semua fitur yang diperlukan
        glucose_level = float(data['glucose'])
        blood_pressure_level = float(data['bloodpressure'])
        bmi_level = float(data['bmi'])
        age_value = float(data['age'])

        input_features = [glucose_level, blood_pressure_level, bmi_level, age_value]
        features_final = [np.array(input_features)]

        # Log fitur yang diterima
        logger.info(f"Fitur input: {input_features}")

        # Transformasi fitur menggunakan MinMaxScaler
        scaled_features_diabetes = scaler_diabetes.transform(features_final)

        # Prediksi menggunakan model
        prediction_diabetes = model_diabetes.predict(scaled_features_diabetes)

        # Coba memuat data faktor risiko diabetes
        try:
            risk_factors_df = pd.read_csv(RISK_FACTORS_PATH, encoding='latin1')
            logger.info("Data faktor risiko berhasil dimuat.")
        except Exception as e:
            logger.error(f"Kesalahan saat memuat data faktor risiko: {e}")
            return jsonify({'error': 'Gagal memuat data faktor risiko'}), 500

        # Cari informasi terkait diabetes
        diabetes_info = risk_factors_df[risk_factors_df['DNAME'] == 'Diabetes']
        if not diabetes_info.empty:
            precautions_diabetes = diabetes_info.iloc[0]['PRECAU']
            risk_factors_diabetes = diabetes_info.iloc[0]['RISKFAC']
        else:
            precautions_diabetes = "Informasi pencegahan tidak tersedia."
            risk_factors_diabetes = "Informasi faktor risiko tidak tersedia."

        # Interpretasi prediksi
        if prediction_diabetes == 1:
            prediction_message_diabetes = "Anda berkemungkinan terkena Diabetes, harap konsultasikan dengan dokter."
            advice_message_diabetes = f"Anda dapat melakukan beberapa hal berikut untuk menurunkan risiko diabetes: {precautions_diabetes}"
            risk_message_diabetes = f"Hal-hal yang menyebabkan dapat terkena diabetes: {risk_factors_diabetes}"
        else:
            prediction_message_diabetes = "Anda tidak berkemungkinan terkena Diabetes."
            advice_message_diabetes = f"Anda tetap dapat melakukan hal ini untuk mencegah terkena diabetes: {precautions_diabetes}"
            risk_message_diabetes = f"Hal-hal yang menyebabkan dapat terkena diabetes: {risk_factors_diabetes}"

        # Log hasil prediksi
        logger.info(f"Hasil prediksi: {prediction_message_diabetes}")

        # Kembalikan prediksi sebagai respons JSON
        return jsonify({
            'prediksi_diabetes': prediction_message_diabetes,
            'saran_diabetes': advice_message_diabetes,
            'faktor_risiko_diabetes': risk_message_diabetes
        })

    except KeyError as e:
        logger.error(f"Kunci hilang dalam data input: {e}")
        return jsonify({'error': f'Kunci hilang: {str(e)}'}), 400
    except ValueError as e:
        logger.error(f"Nilai tidak valid dalam data input: {e}")
        return jsonify({'error': f'Nilai tidak valid: {str(e)}'}), 400

if __name__ == "__main__":
    logger.info("Memulai Flask app.")
    app.run(debug=True, host='0.0.0.0', port=5003)
