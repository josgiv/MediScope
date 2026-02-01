import os
import joblib
import pandas as pd
import numpy as np
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class HeartService:
    """
    Service responsible for Heart Disease predictions.
    """
    def __init__(self):
        cwd = os.getcwd()
        self.model_path = os.path.join(cwd, 'assets', 'models', 'full_checkup', 'heartd_models', 'heartD_model.joblib')
        self.risk_factors_path = os.path.join(cwd, 'notebooks', 'datasets', 'full_checkup', 'disease_riskFactors.csv')
        
        self.model = None
        
        # Load immediately on init
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Heart disease model loaded.")
            except Exception as e:
                logger.error(f"Failed to load heart model: {e}")
        else:
            logger.error(f"Heart model missing at {self.model_path}")

    def predict(self, data: dict):
        """
        Runs the heart disease prediction model.
        """
        if not self.model:
            return {'error': 'Heart Disease model is not loaded.'}

        try:
            # Extract features safely with defaults
            # Note: We trust the frontend to send mostly correct types, 
            # but using safe conversions prevents 500 crashes on bad input.
            features = [
                float(data.get('age', 0)),
                float(data.get('sex', 0)),
                float(data.get('cp', 0)),
                float(data.get('bloodpressure', 0)),
                float(data.get('chol', 0)),
                float(data.get('fbs', 0)),       # Fasting blood sugar
                float(data.get('restecg', 0)),   # Resting ECG
                float(data.get('thalach', 0)),   # Max Heart Rate
                float(data.get('exang', 0)),     # Angina
                float(data.get('oldpeak', 0)),   # ST Depression
                float(data.get('slope', 0)),     # ST Slope
                float(data.get('ca', 0)),        # Major Vessels
                float(data.get('thal', 0))       # Thalassemia
            ]
            
            # Scikit-learn expects 2D array
            input_vector = np.array(features).reshape(1, -1)
            
            prediction = self.model.predict(input_vector)[0]
            
            # Retrieve advice text
            precautions, risk_factors = self._get_context_data()

            # Interpret result
            # Based on existing logic: 1 = Healthy, 0 = Disease? (Or vice versa, sticking to legacy logic)
            # Legacy logic: if prediction == 1 -> "Tidak memiliki penyakit jantung" (Healthy)
            if prediction == 1:
                return {
                    'prediksi_heartd': 'Pasien kemungkinan besar tidak memiliki penyakit jantung.',
                    'saran_heartd': f"Anda dapat melakukan beberapa hal berikut untuk mencegah penyakit jantung: {precautions}",
                    'faktor_risiko_heartd': f"Faktor-faktor risiko untuk penyakit jantung: {risk_factors}"
                }
            else:
                return {
                    'prediksi_heartd': 'Pasien kemungkinan besar memiliki penyakit jantung.',
                    'saran_heartd': f"Beberapa langkah pencegahan untuk mengurangi risiko penyakit jantung: {precautions}",
                    'faktor_risiko_heartd': f"Faktor-faktor risiko untuk penyakit jantung: {risk_factors}"
                }

        except Exception as e:
            logger.exception("Unexpected error in HeartService prediction")
            return {'error': "An internal error occurred."}

    def _get_context_data(self):
        try:
            if os.path.exists(self.risk_factors_path):
                df = pd.read_csv(self.risk_factors_path, encoding='latin1')
                row = df[df['DNAME'] == 'Heart attack'] # Using 'Heart attack' as proxy for Heart Disease based on legacy
                if not row.empty:
                    return row.iloc[0]['PRECAU'], row.iloc[0]['RISKFAC']
        except Exception:
            pass # Silent fail for aux data
            
        return "Informasi tidak tersedia.", "Informasi tidak tersedia."
