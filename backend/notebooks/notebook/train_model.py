import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, '..', 'datasets', 'quick_checkup')
ASSETS_DIR = os.path.join(BASE_DIR, '..', '..', '..', 'assets', 'models', 'quick_checkup')

if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

DATA_PATH = os.path.join(DATASET_DIR, 'symptom-disease.csv')

print("Loading data...")
df = pd.read_csv(DATA_PATH)

# Get all symptom columns (exclude Disease)
symptom_cols = [col for col in df.columns if 'Symptom' in col]

# 1. Collect all unique symptoms
print("Extracting unique symptoms...")
all_symptoms = df[symptom_cols].values.flatten()
# FIX: Use set() to deduplicate
unique_symptoms = sorted(list(set([s.strip() for s in all_symptoms if pd.notna(s) and str(s).strip() != ''])))
print(f"Found {len(unique_symptoms)} unique symptoms.")

# 2. Create Bag of Symptoms (One-Hot / Multi-label)
# Initialize zero matrix
X = pd.DataFrame(0, index=df.index, columns=unique_symptoms)

# Fill 1s where symptom exists
print("Encoding data...")
for i, row in df.iterrows():
    # Get symptoms for this row
    row_symptoms = [str(val).strip() for val in row[symptom_cols].values if pd.notna(val)]
    # Set 1 for these symptoms
    for sym in row_symptoms:
        if sym in unique_symptoms:
            X.at[i, sym] = 1

y = df['Disease']

# 3. Train Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train Model
print("Training Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# 5. Evaluate
preds = rf.predict(X_test)
acc = accuracy_score(y_test, preds)
print(f"Model Accuracy: {acc:.2%}")
# print("Classification Report:\n", classification_report(y_test, preds))

# 6. Save Artifacts
print("Saving artifacts...")
joblib.dump(rf, os.path.join(ASSETS_DIR, 'rf_QuickCheckup.joblib'))
joblib.dump(unique_symptoms, os.path.join(ASSETS_DIR, 'symptom_features.joblib'))

print("Done! Model and features saved.")
