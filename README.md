# Cardiovascular Disease Prediction

> *A machine learning web app that predicts cardiovascular disease risk from clinical indicators — trained on 70,000+ real patient records. Now extended with a hypertension risk module covering a second disease using a dedicated hypertension dataset.*

**by Yash Kewlani · [Live Demo](https://cardiovascular-disease-prediction-sandy.vercel.app)**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python) ![Flask](https://img.shields.io/badge/Flask-Backend-lightgrey?style=flat-square&logo=flask) ![scikit-learn](https://img.shields.io/badge/scikit--learn-GradientBoosting-orange?style=flat-square&logo=scikit-learn) ![Deployed](https://img.shields.io/badge/Deployed-Vercel-black?style=flat-square&logo=vercel) ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What This Is

A full-stack AI web application that takes 11 clinical inputs — age, blood pressure, cholesterol, BMI, lifestyle factors — and predicts whether a patient is at high or low risk for cardiovascular disease.

The app now covers **two diseases**. Alongside the main cardiovascular model, a separate **hypertension risk module** is trained on `hypertension_dataset.csv` — a dedicated dataset with its own features (family history, stress level, salt intake) not present in the cardio datasets. The two models run independently and show results side by side.

Built end-to-end: data cleaning, model training, REST API, and a full interactive frontend with risk visualizations.

**[→ Try it live](https://cardiovascular-disease-prediction-sandy.vercel.app)**

---

## Model Performance

### Cardiovascular Disease Model

| Metric | Score |
| --- | --- |
| Model | Gradient Boosting Classifier |
| Accuracy | ~73% |
| AUC-ROC | ~0.80 |
| Training records | 70,000+ |
| Datasets | cardio_train.csv + shanxi_cardio.csv |

### Hypertension Model

| Metric | Score |
| --- | --- |
| Model | Gradient Boosting Classifier |
| Dataset | hypertension_dataset.csv |
| Features | Family history, stress level, salt intake, age, BMI, blood pressure |

The app also includes a **heuristic fallback** system — if a model file isn't available, risk is calculated from clinical thresholds for BMI, blood pressure, cholesterol, glucose, and lifestyle factors.

---

## Features

- **Cardiovascular risk prediction** — input 11 clinical indicators, get a probability score and high/low risk classification
- **Hypertension risk module** — a separate model trained on `hypertension_dataset.csv`, covering a second disease with its own dedicated features and scoring
- **Interactive visualizations** — age distribution, gender comparison, cholesterol risk, BMI vs blood pressure scatter, physical activity analysis
- **Multi-dataset support** — Kaggle cardio dataset + Shanxi regional dataset
- **REST API** — `POST /predict` endpoint for programmatic access
- **Fallback heuristics** — works without the model file using clinical thresholds

---

## Tech Stack

**Backend:** Flask, Python, scikit-learn, pandas, NumPy, joblib

**Frontend:** HTML, CSS, JavaScript (Chart.js for visualizations)

**Deployment:** Vercel

---

## Project Structure

```
Cardiovascular-disease-prediction/
│
├── App.py                        # Flask app — routes, prediction API, viz data API
├── dataset.py                    # Data cleaning + model training script
├── model.pkl                     # Trained Gradient Boosting model (cardiovascular)
├── requirements.txt
│
├── cardio_train.csv              # Primary cardio dataset (Kaggle, ~70k records)
├── shanxi_cardio.csv             # Secondary cardio dataset (Shanxi regional)
├── cardio_clean.csv              # Cleaned cardio dataset
├── shanxi_clean.csv              # Cleaned shanxi dataset
├── combined_clean.csv            # Merged cardio dataset used for model training
├── hypertension_dataset.csv      # Dedicated dataset for hypertension model
│
├── templates/
│   ├── Index.html                # Home page — quick prediction + hypertension form
│   ├── Risk.html                 # Guided step-by-step cardiovascular assessment
│   ├── Reduce.html               # How to reduce risk (both diseases)
│   ├── Visualize.html            # Dataset visualizations
│   └── Faq.html                  # FAQ
│
├── static/
│   ├── style.css
│   └── script.js
│
└── api/                          # Vercel serverless entry point
```

---

## Getting Started

```
git clone https://github.com/yakew7/Cardiovascular-disease-prediction.git
cd Cardiovascular-disease-prediction
pip install -r requirements.txt
```

**Train the model and clean the datasets:**

```
python3 dataset.py
```

**Start the Flask server:**

```
python3 App.py
```

**Open in browser:**

```
http://localhost:5000
```

---

## API Reference

### `POST /predict`

Predict cardiovascular risk from clinical inputs.

**Request body:**

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

**Response:**

```json
{
  "prediction": 1,
  "probability": 0.78,
  "confidence_pct": 78,
  "bmi": 26.0
}
```

`prediction: 1` = high risk, `prediction: 0` = low risk.

### `GET /api/vizdata?dataset=cardio`

Returns aggregated dataset statistics for all visualizations. Supports `dataset=cardio` or `dataset=shanxi`.

---

## Input Features

### Cardiovascular Model

| Feature | Description | Values |
| --- | --- | --- |
| `age` | Age in years | e.g. 45 |
| `gender` | Biological sex | 1 = female, 2 = male |
| `height` | Height in cm | e.g. 170 |
| `weight` | Weight in kg | e.g. 75 |
| `ap_hi` | Systolic blood pressure | e.g. 140 |
| `ap_lo` | Diastolic blood pressure | e.g. 90 |
| `cholesterol` | Cholesterol level | 1 = normal, 2 = above normal, 3 = well above |
| `gluc` | Glucose level | 1 = normal, 2 = above normal, 3 = well above |
| `smoke` | Smoking | 0 = no, 1 = yes |
| `alco` | Alcohol intake | 0 = no, 1 = yes |
| `active` | Physical activity | 0 = no, 1 = yes |

### Hypertension Model (Separate Dataset)

Trained on `hypertension_dataset.csv` — a dedicated dataset with features specific to hypertension risk, entirely separate from the cardio training data.

| Feature | Description | Values |
| --- | --- | --- |
| `family_hx` | Family history of hypertension | 0 = no, 1 = yes |
| `stress` | Average daily stress level | 1 (very low) – 9 (very high) |
| `salt_intake` | Daily salt consumption | low (<5 g/day), moderate (5–10 g/day), high (10–15 g/day) |

A family history of hypertension roughly doubles baseline risk. Chronic stress elevates cortisol and adrenaline, pushing blood pressure up over time. The WHO recommends staying under 5 g of salt per day — most processed food exceeds this. All three fields are optional and do not affect the main cardiovascular prediction.

---

## Visualizations

The `/visualize` page includes six charts across both datasets:

- Age distribution by disease status
- Gender-based disease comparison
- Cholesterol level risk analysis
- Smoking impact breakdown
- BMI vs systolic blood pressure scatter plot
- Physical activity comparison

---

## What's Next

- [ ] SHAP explainability — show which features drove each prediction
- [ ] Deep learning model comparison (Keras/PyTorch)
- [ ] User authentication + saved risk history
- [ ] Medical report PDF upload and parsing
- [ ] Advanced analytics dashboard
- [ ] Model bias audit across demographic groups

---

## Disclaimer

This project is for educational and research purposes only. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

*Built by [Yash Kewlani](https://github.com/yakew7)*
