import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Setup paths
BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, 'backend/notebooks/datasets/quick_checkup/symptom-disease.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'backend/assets/models/quick_checkup')
MODEL_PATH = os.path.join(MODEL_DIR, 'rf_QuickCheckup.joblib')
FEATURES_PATH = os.path.join(MODEL_DIR, 'symptom_features.joblib')

print(f"Loading data from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

# Clean column names and values
for col in df.columns:
    df[col] = df[col].str.replace('_',' ').str.strip()

print("Preprocessing data...")
# Get all unique symptoms
all_symptoms = set()
symptom_cols = [col for col in df.columns if 'Symptom' in col]

for col in symptom_cols:
    unique_vals = df[col].dropna().unique()
    all_symptoms.update(unique_vals)

feature_names = sorted(list(all_symptoms))
print(f"Found {len(feature_names)} unique symptoms.")

# Create Bag of Symptoms DataFrame
# Initialize with zeros
encoded_df = pd.DataFrame(0, index=df.index, columns=feature_names)

# Fill 1s where symptom is present
for i, row in df.iterrows():
    for col in symptom_cols:
        symptom = row[col]
        if pd.notna(symptom) and symptom in feature_names:
            encoded_df.at[i, symptom] = 1

# Add target
encoded_df['Disease'] = df['Disease']

# X and y
X = encoded_df.drop('Disease', axis=1)
y = encoded_df['Disease']

print(f"Training shape: {X.shape}")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train
print("Training Random Forest...")
rf = RandomForestClassifier(random_state=42)
rf.fit(X_train, y_train)

# Evaluate
preds = rf.predict(X_test)
acc = accuracy_score(y_test, preds)
print(f"Model Accuracy: {acc:.4f}")

# Save
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

print(f"Saving model to {MODEL_PATH}...")
joblib.dump(rf, MODEL_PATH)
print(f"Saving features to {FEATURES_PATH}...")
joblib.dump(feature_names, FEATURES_PATH)

print("Done.")
