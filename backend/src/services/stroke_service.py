import os
import joblib
import pandas as pd
import numpy as np
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class StrokeService:
    """
    Service for handling Stroke prediction logic.
    Encapsulates model loading, data preprocessing, and risk factor lookup.
    """
    def __init__(self):
        # We need to be careful with paths here since this is running from the root context
        cwd = os.getcwd()
        self.model_path = os.path.join(cwd, 'assets', 'models', 'full_checkup', 'stroke_model.joblib')
        self.risk_factors_path = os.path.join(cwd, 'notebooks', 'datasets', 'full_checkup', 'disease_riskFactors.csv')
        
        self.model = None
        self._load_resources()

    def _load_resources(self):
        """Loads the ML model from disk. Fails gracefully if missing."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Stroke model loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"CRITICAL: Failed to load stroke model: {e}")
        else:
            logger.error(f"CRITICAL: Stroke model not found at {self.model_path}")

    def predict(self, data: dict) -> dict:
        """
        Predict stroke probability based on patient data.
        
        Args:
            data: Dictionary containing patient attributes (age, bmi, etc.)
            
        Returns:
            Dictionary with prediction result, advice, and risk factors.
        """
        if not self.model:
            return {'error': 'Service unavailable: Model not loaded.'}

        try:
            # 1. Extract and normalize input data
            # The frontend sends lowercase keys (e.g. 'worktype'), but we handle 
            # legacy capitalization cases just to be safe.
            age = float(data.get('age', 0))
            bmi = float(data.get('bmi', 0))
            glucose = float(data.get('glucose', 0))
            
            # Helper to safely map categorical strings to the numeric values our model expects
            def get_mapped_value(key, options, default_val):
                raw_val = data.get(key, str(default_val))
                # If it's already a number, great
                if isinstance(raw_val, (int, float)):
                    # Check if this number is in our target values (safety check)
                    # Use set of values for O(1) lookup
                    if raw_val in options.values(): 
                        return int(raw_val)
                
                # If string, try to look it up
                s_val = str(raw_val)
                if s_val in options:
                    return options[s_val]
                
                logger.warning(f"Unknown value '{raw_val}' for field '{key}'. Using default.")
                return default_val

            # Mappings defined during model training
            # 1 = Urban, 0 = Rural
            residence = get_mapped_value('residence', {'urban': 1, 'rural': 0}, 1)
            
            # 1 = Male, 0 = Female
            # Legacy frontend might send '1'/'0' strings or 'Male'/'Female'
            sex_map = {'Male': 1, 'Female': 0, '1': 1, '0': 0}
            sex = get_mapped_value('sex', sex_map, 1)

            # 1 = Married, 0 = Not Married
            # Frontend sends 'yes' for married? Let's check page.tsx
            # page.tsx: "yes" -> "Pernah Menikah", "no" -> "Tidak Pernah"
            marital_map = {'married': 1, 'not married': 0, 'yes': 1, 'no': 0}
            marital_status = get_mapped_value('maritalstatus', marital_map, 0)

            # Job types: 0=NoJob, 1=Gov, 2=Private, 3=Self, 4=Children(Age)
            # Frontend values: nojob, age, govtemp, privatejob, selfemp
            work_map = {
                'nojob': 0, 'govtemp': 1, 'privatejob': 2, 'selfemp': 3, 'age': 4
            }
            # Default to Private (2) if unknown
            work_type = get_mapped_value('worktype', work_map, 2)

            # Smoking: 1=Formerly, 2=Non, 3=Smoker
            # Frontend: formerly_smoked, non_smoker, smoker
            smoke_map = {
                'formerly-smoked': 1, 'formerly_smoked': 1, 
                'non-smoker': 2, 'non_smoker': 2,
                'smoker': 3
            }
            smoke = get_mapped_value('smoke', smoke_map, 2)

            # Hypertension/HeartDisease: 1=Yes, 0=No
            # Frontend sends 'hypten'/'nohypten' strings based on checkbox
            hypertension = get_mapped_value('hypertension', {'hypten': 1, 'nohypten': 0, 'true': 1, 'false': 0}, 0)
            heart_disease = get_mapped_value('heartdisease', {'heartdis': 1, 'noheartdis': 0, 'true': 1, 'false': 0}, 0)

            # 2. Construct input vector
            # Strict order required by the model: 
            # [sex, age, hypertension, heartdisease, marital_status, work_type, residence, glucose, bmi, smoke]
            
            features = np.array([[
                sex, age, hypertension, heart_disease, marital_status, 
                work_type, residence, glucose, bmi, smoke
            ]], dtype=float)

            # 3. Predict via Model
            prediction_raw = self.model.predict(features)[0]
            is_stroke_risk = int(prediction_raw) == 1

            # 4. Fetch additional context (Risk Factors/Advice)
            # We wrap this in a try-except because missing CSV shouldn't crash the whole endpoint
            precautions, risk_factors = self._get_advice_context()

            # 5. Format User Response
            if is_stroke_risk:
                return {
                    'prediksi_stroke': "Anda berkemungkinan terkena Stroke, harap konsultasikan dengan dokter.",
                    'saran_stroke': f"Anda dapat melakukan beberapa hal berikut untuk menurunkan risiko stroke: {precautions}",
                    'faktor_risiko_stroke': f"Hal-hal yang dapat menyebabkan stroke: {risk_factors}"
                }
            else:
                return {
                    'prediksi_stroke': "Anda tidak berkemungkinan terkena Stroke.",
                    'saran_stroke': f"Anda tetap dapat melakukan hal ini untuk mencegah stroke: {precautions}",
                    'faktor_risiko_stroke': f"Hal-hal yang dapat menyebabkan stroke: {risk_factors}"
                }

        except Exception as e:
            logger.exception("Error during stroke prediction routine")
            return {'error': "An internal error occurred while processing stroke prediction."}

    def _get_advice_context(self):
        """Helper to retrieve advice text from the CSV database."""
        try:
            if not os.path.exists(self.risk_factors_path):
                return "Belum ada data.", "Belum ada data."

            df = pd.read_csv(self.risk_factors_path, encoding='latin1')
            row = df[df['DNAME'] == 'Stroke']
            
            if not row.empty:
                return row.iloc[0]['PRECAU'], row.iloc[0]['RISKFAC']
                
        except Exception:
            # Log needs to happen here if verbose, but silent failure + default text is safer for UX
            pass
            
        return "Informasi tidak tersedia saat ini.", "Informasi tidak tersedia saat ini."
