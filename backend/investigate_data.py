import pandas as pd
import numpy as np
import os
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier

# Setup paths
BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, 'backend/notebooks/datasets/quick_checkup/symptom-disease.csv')

print(f"Loading data from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

# Clean column names and values
for col in df.columns:
    df[col] = df[col].str.replace('_',' ').str.strip()

print(f"Original shape: {df.shape}")

# Check for duplicates
duplicates = df.duplicated().sum()
print(f"Number of duplicate rows: {duplicates}")
print(f"Percentage of duplicates: {duplicates/len(df)*100:.2f}%")

# Deduped data analysis
df_deduped = df.drop_duplicates()
print(f"Shape after dropping duplicates: {df_deduped.shape}")

# Check duplicates by Disease
print("\nDuplicates distribution by Disease (Top 5):")
print(df[df.duplicated()]['Disease'].value_counts().head())

# Preprocessing for Bag of Symptoms (reusing logic for consistency)
all_symptoms = set()
symptom_cols = [col for col in df.columns if 'Symptom' in col]
for col in symptom_cols:
    unique_vals = df[col].dropna().unique()
    all_symptoms.update(unique_vals)
feature_names = sorted(list(all_symptoms))

encoded_df = pd.DataFrame(0, index=df.index, columns=feature_names)
for i, row in df.iterrows():
    for col in symptom_cols:
        symptom = row[col]
        if pd.notna(symptom) and symptom in feature_names:
            encoded_df.at[i, symptom] = 1
encoded_df['Disease'] = df['Disease']

X = encoded_df.drop('Disease', axis=1)
y = encoded_df['Disease']

# Evaluate with Cross Validation on FULL dataset (including duplicates, to see the inflation)
rf = RandomForestClassifier(random_state=42)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(rf, X, y, cv=cv, scoring='accuracy')
print(f"\nCV Accuracy (Original Data): {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")

# Evaluate on Deduped Data
encoded_df_deduped = encoded_df.drop_duplicates()
X_dedup = encoded_df_deduped.drop('Disease', axis=1)
y_dedup = encoded_df_deduped['Disease']

# Check if there are overlapping symptoms for different diseases (ambiguity)
print("\nChecking for ambiguous symptom sets (same symptoms, different disease):")
ambiguous = encoded_df_deduped.groupby(feature_names).size()
ambiguous = ambiguous[ambiguous > 1]
print(f"Ambiguous symptom sets count: {len(ambiguous)}")

if len(X_dedup) < 5: 
    print("Not enough unique data for 5-fold CV.")
else:
    # Adjust n_splits if data is small
    n_splits = min(5, len(y_dedup.unique())) 
    if len(y_dedup) > n_splits:
        # Check class counts
        class_counts = y_dedup.value_counts()
        min_class_count = class_counts.min()
        if min_class_count < 2:
            print("Warning: Some classes have only 1 sample in deduped data. CV might fail or be unreliable.")
            n_splits = 2 # Minimal split
        
        cv_dedup = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        try:
            scores_dedup = cross_val_score(rf, X_dedup, y_dedup, cv=cv_dedup, scoring='accuracy')
            print(f"CV Accuracy (Deduped Data): {scores_dedup.mean():.4f} (+/- {scores_dedup.std() * 2:.4f})")
        except Exception as e:
            print(f"CV failed on deduped data: {e}")
    else:
         print("Deduped dataset too small for CV.")

