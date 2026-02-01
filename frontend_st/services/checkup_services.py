import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

# Define paths relative to frontend-st folder
# Assuming we run: streamlit run main_st.py inside frontend-st
BACKEND_DIR = os.path.abspath(os.path.join(os.getcwd(), '..', 'backend'))
ASSETS_DIR = os.path.join(BACKEND_DIR, 'assets')
NOTEBOOKS_DIR = os.path.join(BACKEND_DIR, 'notebooks')

class QuickCheckupService:
    def __init__(self):
        self.base_assets = os.path.join(ASSETS_DIR, 'models', 'quick_checkup')
        self.base_data = os.path.join(NOTEBOOKS_DIR, 'datasets', 'quick_checkup')
        
        self.model_path = os.path.join(self.base_assets, 'rf_QuickCheckup.joblib')
        self.desc_path = os.path.join(self.base_data, 'symptom_Description.csv')
        self.precaution_path = os.path.join(self.base_data, 'symptom_precaution.csv')
        self.severity_path = os.path.join(self.base_data, 'Symptom-severity.csv')
        
        self.model = None
        self.symptom_weights = {}
        self.desc_df = None
        self.prec_df = None
        
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            
            if os.path.exists(self.desc_path):
                self.desc_df = pd.read_csv(self.desc_path)
            
            if os.path.exists(self.precaution_path):
                self.prec_df = pd.read_csv(self.precaution_path)
                
            if os.path.exists(self.severity_path):
                sev_df = pd.read_csv(self.severity_path)
                self.symptom_weights = dict(zip(sev_df["Symptom"], sev_df["weight"]))
                
        except Exception as e:
            st.error(f"Error loading QuickCheckup resources: {e}")

    def predict(self, symptoms: list):
        if not self.model:
            return {'error': 'Model not loaded.'}

        try:
            input_vector = []
            for s in symptoms:
                s_clean = str(s).strip()
                weight = self.symptom_weights.get(s_clean, 0)
                input_vector.append(weight)
            
            required_len = 17
            current_len = len(input_vector)
            if current_len < required_len:
                input_vector.extend([0] * (required_len - current_len))
            elif current_len > required_len:
                input_vector = input_vector[:required_len]

            vector_np = np.array([input_vector])
            prediction = self.model.predict(vector_np)[0]
            
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
                    precautions = [str(p) for p in raw_p if pd.notna(p)]

            return {
                "Disease": prediction,
                "Description": desc,
                "Precautions": precautions
            }

        except Exception as e:
            return {'error': str(e)}

    # ... (QuickCheckupService remains same)

class DiabetesService:
    def __init__(self):
        self.model_path = os.path.join(ASSETS_DIR, 'models', 'full_checkup', 'diabetes_models', 'svc_diabetes.joblib')
        self.dataset_path = os.path.join(NOTEBOOKS_DIR, 'datasets', 'full_checkup', 'diabetes-dataset.csv')
        self.risk_factors_path = os.path.join(NOTEBOOKS_DIR, 'datasets', 'full_checkup', 'disease_riskFactors.csv')
        
        self.model = None
        self.scaler = None
        self.feature_names = ['Glucose', 'BloodPressure', 'BMI', 'Age']
        
        self._init_service()

    def _init_service(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            
            if os.path.exists(self.dataset_path):
                raw_df = pd.read_csv(self.dataset_path)
                # Columns: [Glucose, BloodPressure, BMI, Age] -> Indices [1, 2, 5, 7]
                # We fit on these columns
                X = raw_df.iloc[:, [1, 2, 5, 7]].values
                self.scaler = MinMaxScaler(feature_range=(0, 1))
                self.scaler.fit(X)
        except Exception as e:
            st.error(f"Error loading DiabetesService: {e}")

    def predict(self, data: dict):
        if not self.model or not self.scaler:
            return {'error': 'Service not fully initialized.'}

        try:
            val_glucose = float(data.get('glucose', 0))
            val_bp = float(data.get('bloodpressure', 0))
            val_bmi = float(data.get('bmi', 0))
            val_age = float(data.get('age', 0))

            # Create DataFrame to satisfy feature name warnings (if scaler supports it)
            # Actually scaler was fit on numpy array in _init_service: X = raw_df.iloc[:, ...].values
            # So scaler expects array. The MODEL might expect array too if trained on array.
            # But SVC usually warns if feature names missing ONLY if fit with DF.
            # Let's stick to array for scaler, but maybe model needs DF? 
            # The warning said "GradientBoostingClassifier was fitted with feature names".
            # Diabetes uses SVC. Stroke likely used GradientBoosting.
            
            raw_input = np.array([[val_glucose, val_bp, val_bmi, val_age]])
            scaled_input = self.scaler.transform(raw_input)
            
            # For SVC, usually array is fine if scaler returned array.
            pred = self.model.predict(scaled_input)[0]
            
            precautions, risk_factors = self._get_context()

            if pred == 1:
                return {
                    'prediksi_diabetes': "Anda berkemungkinan terkena Diabetes, harap konsultasikan dengan dokter.",
                    'saran_diabetes': f"Saran: {precautions}",
                    'faktor_risiko_diabetes': f"Faktor Risiko: {risk_factors}"
                }
            else:
                return {
                    'prediksi_diabetes': "Anda tidak berkemungkinan terkena Diabetes.",
                    'saran_diabetes': f"Saran Pencegahan: {precautions}",
                    'faktor_risiko_diabetes': f"Faktor Risiko: {risk_factors}"
                }

        except Exception as e:
            return {'error': str(e)}

    def _get_context(self):
        try:
            if os.path.exists(self.risk_factors_path):
                df = pd.read_csv(self.risk_factors_path, encoding='latin1')
                row = df[df['DNAME'] == 'Diabetes']
                if not row.empty:
                    return row.iloc[0]['PRECAU'], row.iloc[0]['RISKFAC']
        except Exception:
            pass
        return "Informasi tidak tersedia.", "Informasi tidak tersedia."

class HeartService:
    def __init__(self):
        self.model_path = os.path.join(ASSETS_DIR, 'models', 'full_checkup', 'heartd_models', 'heartD_model.joblib')
        self.risk_factors_path = os.path.join(NOTEBOOKS_DIR, 'datasets', 'full_checkup', 'disease_riskFactors.csv')
        self.model = None
        # Heart dataset cols: age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal
        self.feature_names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
        
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)

    def predict(self, data: dict):
        if not self.model:
            return {'error': 'Model not loaded.'}

        try:
            features_dict = {
                'age': float(data.get('age', 0)),
                'sex': float(data.get('sex', 0)),
                'cp': float(data.get('cp', 0)),
                'trestbps': float(data.get('bloodpressure', 0)), # Note mapping: bloodpressure -> trestbps
                'chol': float(data.get('chol', 0)),
                'fbs': float(data.get('fbs', 0)),
                'restecg': float(data.get('restecg', 0)),
                'thalach': float(data.get('thalach', 0)),
                'exang': float(data.get('exang', 0)),
                'oldpeak': float(data.get('oldpeak', 0)),
                'slope': float(data.get('slope', 0)),
                'ca': float(data.get('ca', 0)),
                'thal': float(data.get('thal', 0))
            }
            
            # Create DataFrame
            input_df = pd.DataFrame([features_dict], columns=self.feature_names)
            
            prediction = self.model.predict(input_df)[0]
            
            precautions, risk_factors = self._get_context_data()

            if prediction == 1:
                return {
                    'prediksi_heartd': 'Pasien kemungkinan besar tidak memiliki penyakit jantung.',
                    'saran_heartd': f"Pencegahan: {precautions}",
                    'faktor_risiko_heartd': f"Faktor Risiko: {risk_factors}"
                }
            else:
                return {
                    'prediksi_heartd': 'Pasien kemungkinan besar memiliki penyakit jantung.',
                    'saran_heartd': f"Saran Penanganan: {precautions}",
                    'faktor_risiko_heartd': f"Faktor Risiko: {risk_factors}"
                }

        except Exception as e:
            return {'error': str(e)}

    def _get_context_data(self):
        try:
            if os.path.exists(self.risk_factors_path):
                df = pd.read_csv(self.risk_factors_path, encoding='latin1')
                # Try finding Heart
                row = df[df['DNAME'].str.contains('Heart', case=False, na=False)]
                if not row.empty:
                    return row.iloc[0]['PRECAU'], row.iloc[0]['RISKFAC']
        except Exception:
            pass
        return "Informasi tidak tersedia.", "Informasi tidak tersedia."

class StrokeService:
    def __init__(self):
        self.model_path = os.path.join(ASSETS_DIR, 'models', 'full_checkup', 'stroke_model.joblib')
        self.risk_factors_path = os.path.join(NOTEBOOKS_DIR, 'datasets', 'full_checkup', 'disease_riskFactors.csv')
        self.model = None
        # Stroke cols: gender,age,hypertension,heart_disease,ever_married,work_type,Residence_type,avg_glucose_level,bmi,smoking_status
        self.feature_names = [
            'gender', 'age', 'hypertension', 'heart_disease', 'ever_married', 
            'work_type', 'Residence_type', 'avg_glucose_level', 'bmi', 'smoking_status'
        ]
        
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)

    def predict(self, data: dict):
        if not self.model:
            return {'error': 'Model not loaded.'}

        try:
            # --- Input Mappings ---
            # Work Type: children=0, Govt_job=1, Never_worked=2, Private=3, Self-employed=4
            w_map = {'children': 0, 'govtemp': 1, 'never_worked': 2, 'privatejob': 3, 'selfemp': 4}
            
            # Smoking: Unknown=0, formerly smoked=1, never smoked=2, smokes=3
            s_map = {'Unknown': 0, 'formerly_smoked': 1, 'never_smoked': 2, 'smokes': 3}
            
            w_val = w_map.get(data.get('worktype'), 3) # default Private
            s_val = s_map.get(data.get('smoke'), 2)    # default never_smoked
            
            # Map backend inputs to model features
            row = {
                'gender': int(data.get('sex', 1)), # 1=Male
                'age': float(data.get('age', 0)),
                'hypertension': int(data.get('hypertension', 0)),
                'heart_disease': int(data.get('heartdisease', 0)),
                'ever_married': int(data.get('maritalstatus', 0)), # 1=Married
                'work_type': int(w_val),
                'Residence_type': int(data.get('residence', 1)), # 1=Urban
                'avg_glucose_level': float(data.get('glucose', 0)),
                'bmi': float(data.get('bmi', 0)),
                'smoking_status': int(s_val)
            }
            
            # Construct DataFrame with proper feature names
            input_df = pd.DataFrame([row], columns=self.feature_names)
    
            prediction_raw = self.model.predict(input_df)[0]
            is_stroke_risk = int(prediction_raw) == 1
            
            precautions, risk_factors = self._get_advice_context()

            if is_stroke_risk:
                return {
                    'prediksi_stroke': "Anda berkemungkinan terkena Stroke.",
                    'saran_stroke': f"Saran: {precautions}",
                    'faktor_risiko_stroke': f"Faktor Risiko: {risk_factors}"
                }
            else:
                return {
                    'prediksi_stroke': "Anda tidak berkemungkinan terkena Stroke.",
                    'saran_stroke': f"Pencegahan: {precautions}",
                    'faktor_risiko_stroke': f"Faktor Risiko: {risk_factors}"
                }

        except Exception as e:
            # Fallback if model was trained on array
            try:
                features = np.array([list(row.values())], dtype=float)
                prediction_raw = self.model.predict(features)[0]
                is_stroke_risk = int(prediction_raw) == 1
                precautions, risk_factors = self._get_advice_context()
                if is_stroke_risk:
                    return {
                        'prediksi_stroke': "Anda berkemungkinan terkena Stroke.",
                        'saran_stroke': f"Saran: {precautions}",
                        'faktor_risiko_stroke': f"Faktor Risiko: {risk_factors}"
                    }
                else:
                    return {
                        'prediksi_stroke': "Anda tidak berkemungkinan terkena Stroke.",
                        'saran_stroke': f"Pencegahan: {precautions}",
                        'faktor_risiko_stroke': f"Faktor Risiko: {risk_factors}"
                    }
            except Exception as e2:
                return {'error': f"Main: {str(e)} | Backup: {str(e2)}"}

    def _get_advice_context(self):
        try:
            if os.path.exists(self.risk_factors_path):
                df = pd.read_csv(self.risk_factors_path, encoding='latin1')
                # Try finding Stroke
                row = df[df['DNAME'].str.contains('Stroke', case=False, na=False)]
                if not row.empty:
                    return row.iloc[0]['PRECAU'], row.iloc[0]['RISKFAC']
        except Exception:
            pass
        return "Informasi tidak tersedia.", "Informasi tidak tersedia."

# Singleton instances wrapped for caching
@st.cache_resource
def get_quick_checkup_service():
    return QuickCheckupService()

@st.cache_resource
def get_diabetes_service():
    return DiabetesService()

@st.cache_resource
def get_heart_service():
    return HeartService()

@st.cache_resource
def get_stroke_service():
    return StrokeService()
