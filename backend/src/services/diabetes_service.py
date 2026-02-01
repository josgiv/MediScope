import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DiabetesService:
    """
    Handles Diabetes prediction logic using SVC model.
    """
    def __init__(self):
        cwd = os.getcwd()
        self.model_path = os.path.join(cwd, 'assets', 'models', 'full_checkup', 'diabetes_models', 'svc_diabetes.joblib')
        self.dataset_path = os.path.join(cwd, 'notebooks', 'datasets', 'full_checkup', 'diabetes-dataset.csv')
        self.risk_factors_path = os.path.join(cwd, 'notebooks', 'datasets', 'full_checkup', 'disease_riskFactors.csv')
        
        self.model = None
        self.scaler = None
        
        self._init_service()

    def _init_service(self):
        """Loads model and fits the scaler based on the original dataset."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                logger.error(f"Diabetes model missing at {self.model_path}")
                return

            if os.path.exists(self.dataset_path):
                # We need to recreate the scaler state used during training
                # This seems inefficient to do on every startup, but necessary if the scaler wasn't saved.
                # Ideally, we should save/load the scaler object itself (todo for future).
                raw_df = pd.read_csv(self.dataset_path)
                # Columns used: [Glucose, BloodPressure, BMI, Age] -> Indices [1, 2, 5, 7]
                # Double check dataset columns if index based!
                # Assuming legacy code index [1, 2, 5, 7] is correct for that specific CSV structure.
                X = raw_df.iloc[:, [1, 2, 5, 7]].values
                self.scaler = MinMaxScaler(feature_range=(0, 1))
                self.scaler.fit(X)
                logger.info("Diabetes service initialized (Model + Scaler).")
            else:
                logger.error(f"Training dataset missing at {self.dataset_path}. Cannot initialize scaler.")

        except Exception as e:
            logger.error(f"Failed to initialize DiabetesService: {e}")

    def predict(self, data: dict):
        if not self.model or not self.scaler:
            return {'error': 'Service not fully initialized (Model or Scaler missing).'}

        try:
            # Inputs
            val_glucose = float(data.get('glucose', 0))
            val_bp = float(data.get('bloodpressure', 0))
            val_bmi = float(data.get('bmi', 0))
            val_age = float(data.get('age', 0))

            # Scale
            raw_input = np.array([[val_glucose, val_bp, val_bmi, val_age]])
            scaled_input = self.scaler.transform(raw_input)
            
            # Predict
            # Model returns 1 for Diabetes, 0 for healthy usually
            pred = self.model.predict(scaled_input)[0]
            
            precautions, risk_factors = self._get_context()

            if pred == 1:
                return {
                    'prediksi_diabetes': "Anda berkemungkinan terkena Diabetes, harap konsultasikan dengan dokter.",
                    'saran_diabetes': f"Anda dapat melakukan beberapa hal berikut untuk menurunkan risiko diabetes: {precautions}",
                    'faktor_risiko_diabetes': f"Hal-hal yang menyebabkan dapat terkena diabetes: {risk_factors}"
                }
            else:
                return {
                    'prediksi_diabetes': "Anda tidak berkemungkinan terkena Diabetes.",
                    'saran_diabetes': f"Anda tetap dapat melakukan hal ini untuk mencegah terkena diabetes: {precautions}",
                    'faktor_risiko_diabetes': f"Hal-hal yang menyebabkan dapat terkena diabetes: {risk_factors}"
                }

        except Exception as e:
            logger.exception("Diabetes prediction error")
            return {'error': str(e)}

    def _get_context(self):
        try:
            if os.path.exists(self.risk_factors_path):
                df = pd.read_csv(self.risk_factors_path, encoding='latin1')
                row = df[df['DNAME'] == 'Diabetes']
                if not row.empty:
                    return row.iloc[0]['PRECAU'], row.iloc[0]['RISKFAC']
        except:
            pass
        return "Info tidak tersedia", "Info tidak tersedia"
