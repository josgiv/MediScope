from flask import Flask, request, jsonify
import numpy as np
import os
from joblib import load

app = Flask(__name__)

# Print current working directory and model path for debugging
print("Current working directory: ", os.getcwd())

# Define the absolute path for the model
MODEL_PATH = os.path.join(os.getcwd(), 'models', 'full_checkup', 'stroke_model.joblib')

# Load model
try:
    model = load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Failed to load model. Error: {e}")

@app.route('/fc-stroke', methods=['POST'])
def predict():
    if request.is_json:
        data = request.get_json()
        
        # Extract and set default values
        age = data.get('age', 0)
        maritalstatus = data.get('maritalstatus', 'not married')
        worktype = data.get('Worktype', 'privatejob')
        residence = data.get('Residence', 'urban')
        sex = data.get('Sex', 'Male')
        bmi = data.get('bmi', 0.0)
        glucose = data.get('glucose', 0.0)
        smoke = data.get('Smoke', 'non-smoker')
        hypertension = data.get('Hypertension', 'nohypten')
        heartdisease = data.get('heartdis', 'noheartdis')

        # Input mapping for model
        mappings = {
            'residence': {'urban': 1, 'rural': 0},
            'sex': {'Female': 0, 'Male': 1},
            'maritalstatus': {'married': 1, 'not married': 0},
            'worktype': {'privatejob': 2, 'govtemp': 1, 'selfemp': 3},
            'smoke': {'formerly-smoked': 1, 'non-smoker': 2, 'smoker': 3},
            'hypertension': {'hypten': 1, 'nohypten': 0},
            'heartdisease': {'heartdis': 1, 'noheartdis': 0}
        }

        # Convert input values using mappings
        residence = mappings['residence'].get(residence, 1)
        sex = mappings['sex'].get(sex, 1)
        maritalstatus = mappings['maritalstatus'].get(maritalstatus, 0)
        worktype = mappings['worktype'].get(worktype, 2)
        smoke = mappings['smoke'].get(smoke, 2)
        hypertension = mappings['hypertension'].get(hypertension, 0)
        heartdisease = mappings['heartdisease'].get(heartdisease, 0)

        # Prepare input array for prediction
        input_array = np.array([[sex, age, hypertension, heartdisease, maritalstatus, worktype, residence, glucose, bmi, smoke]], dtype='float64')
        
        # Predict stroke
        try:
            pred_stroke = model.predict(input_array)
            result = int(pred_stroke[0])

            # JSON response
            response = {
                "stroke_prediction": "You will get stroke" if result == 1 else "You will not get stroke"
            }
            return jsonify(response)
        
        except Exception as e:
            return jsonify({"error": f"Prediction failed. Error: {e}"}), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
