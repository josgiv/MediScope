
# MediScope: Full Checkup Prediction Service

## Overview

MediScope is a predictive healthcare service designed to assess the likelihood of certain health conditions based on a patient's data. The service uses machine learning models to predict three major health conditions:
- **Stroke**
- **Heart Disease**
- **Diabetes**

This project provides an API endpoint that accepts patient data as input and returns predictions from the three models. Additionally, the service includes a **Quick Checkup** feature for users who want a rapid assessment of their health condition.

## Features
- **Predicts Stroke**: Using factors such as age, marital status, BMI, glucose levels, smoking status, and more.
- **Predicts Heart Disease**: Based on data like blood pressure, cholesterol levels, and physical activity.
- **Predicts Diabetes**: Taking into account factors like glucose levels, blood pressure, BMI, and age.
- **Quick Checkup**: A feature that provides a fast health prediction based on minimal input data. This can be used for users who do not want to provide all the details for a full checkup.

## System Architecture
The system consists of three models running on separate Flask APIs, each serving predictions for a specific health condition:
1. **Stroke Model**: Hosted on `http://localhost:5001/fc-stroke`
2. **Heart Disease Model**: Hosted on `http://localhost:5002/fc-heartd`
3. **Diabetes Model**: Hosted on `http://localhost:5003/fc-diabetes`

### Main API
The main Flask app, hosted on `http://localhost:5000/predict`, communicates with these three models and aggregates the results.

## Requirements
- Python 3.7 or higher
- Flask
- Requests
- Logging
- Time
- OS
- concurrent.futures (for parallel request execution)

## Installation
1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/medi-scope.git
    cd medi-scope
    ```

2. **Install required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Environment Configuration
The URLs for the three model APIs can be set via environment variables:
- `STROKE_API_URL`: URL for the stroke prediction model (default: `http://localhost:5001/fc-stroke`)
- `HEARTD_API_URL`: URL for the heart disease prediction model (default: `http://localhost:5002/fc-heartd`)
- `DIABETES_API_URL`: URL for the diabetes prediction model (default: `http://localhost:5003/fc-diabetes`)

Set these variables in your environment:
```bash
export STROKE_API_URL=http://localhost:5001/fc-stroke
export HEARTD_API_URL=http://localhost:5002/fc-heartd
export DIABETES_API_URL=http://localhost:5003/fc-diabetes


Alternatively, you can modify the URLs directly in the `models_loader.py` script.

## Running the Service
To start the service, run the Flask app:

```bash
python models_loader.py
```

By default, the Flask app will run on port 5000. You can change the port or other configurations in the script or environment.

## API Usage

### Predict Endpoint

- **URL**: `/predict`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
    The request must contain a JSON object with the necessary fields for each model. The fields are as follows:
    - `age`: (integer)
    - `maritalstatus`: (string)
    - `sex`: (string)
    - `bmi`: (float)
    - `glucose`: (float)
    - `smoke`: (string)
    - `hypertension`: (string)
    - `heartdis`: (string)
    - `cp`: (string)
    - `bloodpressure`: (integer)
    - `chol`: (float)
    - `fbs`: (float)
    - `restecg`: (string)
    - `thalach`: (integer)
    - `exang`: (string)
    - `oldpeak`: (float)
    - `slope`: (string)
    - `ca`: (string)
    - `thal`: (string)

- **Example Request Body**:
    ```json
    {
        "age": 45,
        "maritalstatus": "married",
        "sex": "male",
        "bmi": 25.4,
        "glucose": 98.5,
        "smoke": "no",
        "hypertension": "yes",
        "heartdis": "no",
        "cp": "typical angina",
        "bloodpressure": 120,
        "chol": 230,
        "fbs": 0.2,
        "restecg": "normal",
        "thalach": 150,
        "exang": "yes",
        "oldpeak": 1.2,
        "slope": "upsloping",
        "ca": "0",
        "thal": "normal"
    }
    ```

- **Example Response**:
    ```json
    {
        "stroke_prediction": "You will not get stroke",
        "heart_disease_prediction": "The patient is not likely to have heart disease.",
        "diabetes_prediction": "You have Diabetes, please consult a Doctor."
    }
    ```

### Quick Checkup Endpoint

- **URL**: `/quick_checkup`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
    The request should contain basic health information. Fields may include:
    - `age`: (integer)
    - `sex`: (string)
    - `bmi`: (float)

- **Example Request Body**:
    ```json
{
  "Symptom_1": "itching",
  "Symptom_2": "sneezing",
  "Symptom_3": "headache",
  "Symptom_4": "fever"
}

    ```

- **Example Response**:
    ```json
    {
        "disease": "fever"
    }
    ```

### Error Handling
If the request is not in JSON format, the response will be:
```json
{
    "error": "Request must be JSON"
}
```

If there is an issue with connecting to any of the model APIs, the response will include an error message specific to the model:
```json
{
    "stroke_prediction": "Error with stroke model",
    "heart_disease_prediction": "Error with heart disease model",
    "diabetes_prediction": "Error with diabetes model"
}
```

## Code Explanation

### `models_loader.py`
This file is responsible for:
1. **Receiving POST requests** and parsing input data.
2. **Preparing data for each model** by formatting the input into appropriate fields.
3. **Sending POST requests to the respective model APIs** with retries in case of failure.
4. **Aggregating the results** from each model and returning them as a single response.

The app utilizes logging to track requests and responses, retries API calls in case of failure, and handles errors gracefully.

### Performance Enhancements
- **Parallel Requests**: The `ThreadPoolExecutor` is used to execute API requests in parallel, reducing the overall response time.
- **Caching**: The `@lru_cache` decorator is used to cache model responses for frequent requests to avoid redundant calculations.

### Dependencies
- **Flask**: Web framework for handling the API.
- **Requests**: Library to make HTTP requests to the individual model APIs.
- **Logging**: For tracking request and response logs.
- **ThreadPoolExecutor**: To handle parallel requests for performance.
- **lru_cache**: To cache frequent API responses.

## Troubleshooting
1. **API not responding**: Make sure that all model APIs (`fc-stroke`, `fc-heartd`, `fc-diabetes`) are running and accessible.
2. **Model API error**: If a model is returning an error, check the logs for the specific error message to diagnose the issue.
3. **Slow performance**: Ensure that the Flask app is running with sufficient resources, and consider scaling the model APIs if needed.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
This project is powered by Flask and Python's machine learning models. Thanks to all contributors who helped in refining the predictions and improving the architecture.
```

### Key Changes:
1. **Quick Checkup Feature**: A new `/quick_checkup` endpoint has been added. This allows users to get a rapid assessment based on limited health data (age, sex, and BMI).
2. **Updated API Usage Section**: Detailed usage instructions for both the **Full Checkup** and **Quick Checkup** endpoints.
3. **Additional Details**: Included more comprehensive examples and explanations for each feature.

This updated `README.md` provides users with clear instructions on both the main and quick checkup functionalities.