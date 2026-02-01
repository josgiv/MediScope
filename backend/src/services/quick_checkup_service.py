import os
import joblib
import pandas as pd
import numpy as np
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class QuickCheckupService:
    """
    Service for Quick Symptom-based Disease Prediction using Random Forest.
    """
    def __init__(self):
        # cwd = os.getcwd()
        # Use relative path from this file to ensure stability regardless of run location
        # File is in backend/src/services/
        # Root is backend/
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_root = os.path.dirname(os.path.dirname(current_dir))
        
        base_assets = os.path.join(backend_root, 'assets', 'models', 'quick_checkup')
        base_data = os.path.join(backend_root, 'notebooks', 'datasets', 'quick_checkup')
        
        self.model_path = os.path.join(base_assets, 'rf_QuickCheckup.joblib')
        self.weights_path = os.path.join(base_assets, 'symptom_weights.joblib')

        self.desc_path = os.path.join(base_data, 'symptom_Description.csv')
        self.precaution_path = os.path.join(base_data, 'symptom_precaution.csv')
        
        self.model = None
        self.model = None
        self.symptom_weights = None
        self.desc_df = None
        self.prec_df = None
        
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                logger.error(f"QuickCheckup model missing at {self.model_path}")
            
            if os.path.exists(self.weights_path):
                self.symptom_weights = joblib.load(self.weights_path)
            else:
                logger.error(f"QuickCheckup weights missing at {self.weights_path}")

            # Load Metadata
            if os.path.exists(self.desc_path):
                self.desc_df = pd.read_csv(self.desc_path)
            
            if os.path.exists(self.precaution_path):
                self.prec_df = pd.read_csv(self.precaution_path)
            
            logger.info("QuickCheckup resources initialized.")

        except Exception as e:
            logger.error(f"Partial failure initializing QuickCheckup: {e}")

    def predict(self, symptoms: list):
        """
        Predicts disease from a list of symptom strings.
        """
        if not self.model or not self.symptom_weights:
            return {'error': 'Model or weights not loaded.'}

        try:
            # 1. Convert to Sorted Weights
            input_weights = []
            
            for s in symptoms:
                s_clean = str(s).strip().replace('_', ' ')
                if s_clean in self.symptom_weights:
                    input_weights.append(self.symptom_weights[s_clean])
                else:
                    input_weights.append(0)
            
            # SORT DESCENDING: High severity first
            # This ensures [A, B] and [B, A] provide same vector
            input_weights.sort(reverse=True)
            
            # Pad to 17
            while len(input_weights) < 17:
                input_weights.append(0)
            
            # Truncate if too long (unlikely but safe)
            input_weights = input_weights[:17]

            # 2. Predict
            vector_np = np.array([input_weights])
            prediction = self.model.predict(vector_np)[0]
            
            # 4. Get Details
            desc = "Deskripsi tidak tersedia."
            precautions = []
            
            if self.desc_df is not None:
                row = self.desc_df[self.desc_df['Disease'] == prediction]
                if not row.empty:
                    desc = row.iloc[0]['Description']
            
            if self.prec_df is not None:
                row = self.prec_df[self.prec_df['Disease'] == prediction]
                if not row.empty:
                    # Precautions occupy columns 1 onwards
                    raw_p = row.iloc[0, 1:].tolist()
                    # Filter out NaNs if any
                    precautions = [str(p) for p in raw_p if pd.notna(p)]

            return {
                "Disease": prediction,
                "Description": desc,
                "Precautions": precautions
            }

        except Exception as e:
            logger.exception("Error in QuickCheckup predict")
            return {'error': f"Prediction error: {str(e)}"}
