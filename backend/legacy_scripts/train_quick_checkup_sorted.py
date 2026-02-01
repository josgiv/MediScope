import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Setup paths
BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, 'backend/notebooks/datasets/quick_checkup/symptom-disease.csv')
SEVERITY_PATH = os.path.join(BASE_DIR, 'backend/notebooks/datasets/quick_checkup/Symptom-severity.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'backend/assets/models/quick_checkup')
MODEL_PATH = os.path.join(MODEL_DIR, 'rf_QuickCheckup.joblib')
WEIGHTS_PATH = os.path.join(MODEL_DIR, 'symptom_weights.joblib')

print(f"Loading data from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)
severity_df = pd.read_csv(SEVERITY_PATH)

# Clean column names and values in dataset
for col in df.columns:
    df[col] = df[col].str.replace('_',' ').str.strip()

# Create Symptom -> Weight Map
# Clean severity strings too (remove underscores)
severity_df['Symptom'] = severity_df['Symptom'].str.replace('_',' ').str.strip()
symptom_weights = dict(zip(severity_df['Symptom'], severity_df['weight']))

print(f"Loaded {len(symptom_weights)} symptom weights.")

# Preprocessing: Convert Symptoms to Sorted Weights
X_list = []
y_list = []

symptom_cols = [col for col in df.columns if 'Symptom' in col]

for i, row in df.iterrows():
    weights = []
    for col in symptom_cols:
        symptom = row[col]
        if pd.notna(symptom) and symptom in symptom_weights:
            weights.append(symptom_weights[symptom])
        elif pd.notna(symptom):
            # Unknown symptom? Assign 0 or log warning?
            # For now, 0
            weights.append(0)
    
    # CRITICAL FIX: SORT DESCENDING
    # This ensures [HighSev, LowSev] and [LowSev, HighSev] become the same vector
    weights.sort(reverse=True)
    
    # Pad to 17
    while len(weights) < 17:
        weights.append(0)
    
    # If > 17 (unlikely given columns), truncate
    weights = weights[:17]
    
    X_list.append(weights)
    y_list.append(row['Disease'])

X = np.array(X_list)
y = np.array(y_list)

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
print(f"Saving weights map to {WEIGHTS_PATH}...")
joblib.dump(symptom_weights, WEIGHTS_PATH)

print("Done.")
