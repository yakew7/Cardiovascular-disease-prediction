# Cardiovascular Disease Prediction

An AI-powered web application that predicts cardiovascular disease risk using Machine Learning and real-world medical datasets.
Built with Flask, Python, Pandas, NumPy, and Scikit-learn.

## Features

* Cardiovascular disease risk prediction
* Interactive Flask web application
* Machine Learning model integration
* BMI and blood pressure analysis
* Dataset visualizations and statistics
* Multiple dataset support
* REST API for predictions
* Fallback heuristic prediction system

---

## Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Flask
* Python

### Machine Learning & Data Processing

* Scikit-learn
* Pandas
* NumPy
* Joblib

---

## Datasets Used

This project uses cardiovascular health datasets containing medical indicators such as:

* Age
* Gender
* Height
* Weight
* Blood Pressure
* Cholesterol
* Glucose Levels
* Smoking Habits
* Alcohol Intake
* Physical Activity

The primary target variable predicts the presence or absence of cardiovascular disease.

Example datasets include:

* `cardio_train.csv`
* `shanxi_cardio.csv`

---

## Project Structure

```bash
Cardiovascular-disease-prediction/
│
├── app.py
├── dataset.py
├── model.pkl
├── cardio_train.csv
├── shanxi_cardio.csv
│
├── templates/
│   ├── index.html
│   ├── risk.html
│   ├── reduce.html
│   ├── visualize.html
│   └── faq.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yakew7/Cardiovascular-disease-prediction.git
cd Cardiovascular-disease-prediction
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Train / Prepare Dataset

```bash
python3 dataset.py
```

### 4. Start Flask Server

```bash
python3 app.py
```

### 5. Open in Browser

```txt
http://localhost:5000
```

---

## API Endpoint

### Predict Cardiovascular Risk

#### POST `/predict`

Example JSON request:

```json
{
  "age": 45,
  "gender": 1,
  "height": 170,
  "weight": 75,
  "ap_hi": 140,
  "ap_lo": 90,
  "cholesterol": 2,
  "gluc": 1,
  "smoke": 0,
  "alco": 0,
  "active": 1
}
```

Example response:

```json
{
  "prediction": 1,
  "probability": 0.78
}
```

---

## Machine Learning

The application supports:

* Trained ML model (`model.pkl`)
* Automatic fallback heuristic system if model is unavailable

The fallback logic evaluates:

* BMI
* Blood pressure
* Cholesterol
* Glucose
* Smoking
* Alcohol consumption
* Physical activity
* Age

---

## Visualizations

The `/visualize` page provides:

* Age distribution analysis
* Gender-based disease comparison
* Cholesterol risk analysis
* Smoking impact visualization
* BMI vs Blood Pressure scatter plots
* Physical activity comparisons

---

## Future Improvements

* Deep Learning integration
* Real-time health monitoring
* User authentication
* Medical report uploads
* Cloud deployment
* Advanced analytics dashboard
* SHAP/XAI explainability

---

## Disclaimer

This project is for educational and research purposes only.
It is NOT a substitute for professional medical advice, diagnosis, or treatment.

---

## Author

Yash Kewlani

GitHub: https://github.com/yakew7
