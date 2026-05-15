# ♥ CardioAI — Cardiovascular & Hypertension Risk Predictor

> An AI-powered web application that predicts **cardiovascular disease risk** and **hypertension risk** using machine learning on real-world medical datasets.

**Live Demo:** [cardiovascular-disease-prediction-sandy.vercel.app](https://cardiovascular-disease-prediction-sandy.vercel.app)

---

## What It Does

CardioAI takes 11 standard health parameters (age, blood pressure, cholesterol, BMI, lifestyle factors) and instantly predicts:

- **Cardiovascular disease risk** — powered by a Gradient Boosting ML model trained on 88,000+ patient records (~73% accuracy, AUC ~0.80)
- **Hypertension risk** — a validated heuristic model using 3 additional inputs (family history, stress level, salt intake), based on a 175k-record dataset

Two input modes are available: a **quick form** on the home page and a **guided step-by-step chat** on the Risk page.

---

## Features

- Guided conversational risk assessment (Risk page)
- Quick prediction form with live BMI calculation (Home page)
- Optional hypertension risk add-on (family history, stress, salt intake)
- 8-chart data visualization dashboard across 3 datasets
- Risk reduction guide with evidence-based lifestyle tips
- Hypertension-specific reduction advice
- In-page AI chatbot for health questions
- FAQ page covering all parameters and both prediction models
- Fully deployable on Vercel (no pandas/sklearn required — heuristic fallback for serverless)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| ML / Data | scikit-learn, pandas, NumPy, joblib |
| Charts | Chart.js |
| Fonts | Google Fonts (Syne, DM Sans) |
| Deployment | Vercel (serverless via `api/index.py`) |

---

## Project Structure

```
Cardiovascular-disease-prediction/
│
├── app.py                  # Flask app for local dev (uses pandas + model.pkl)
├── dataset.py              # Cleans CSVs, trains and saves model.pkl
├── model.pkl               # Trained GradientBoosting model
│
├── api/
│   └── index.py            # Vercel serverless entry point (heuristic, no sklearn)
│
├── templates/
│   ├── Index.html          # Home page — quick prediction form + chatbot
│   ├── Risk.html           # Guided step-by-step chat assessment
│   ├── Reduce.html         # Lifestyle tips for heart & hypertension risk
│   ├── Visualize.html      # Dataset charts (Chart.js)
│   └── Faq.html            # Frequently asked questions
│
├── static/
│   ├── Script.js           # BMI calc, form submit, chatbot, hypertension heuristic
│   └── Style.css           # All styling
│
├── cardio_train.csv           # Raw: Russian cohort (~70k records)
├── shanxi_cardio.csv          # Raw: Chinese cohort (~19k records)
├── cardio_clean.csv           # Cleaned output from dataset.py
├── shanxi_clean.csv           # Cleaned output from dataset.py
├── hypertension_dataset.csv   # Raw: Hypertension Dataset (~175k records)
├── combined_clean.csv         # Merged dataset used for model training (~88k records)
│
├── vercel.json             # Vercel routing config
├── .vercelignore
└── requirements.txt
```

---

## Datasets

| Dataset | Records | Source | Target |
|---|---|---|---|
| Cardio Train | ~70,000 | Kaggle (Russian cohort) | `cardio` (0/1) |
| Shanxi Cardio | ~19,000 | Chinese medical records | `cardio` (0/1) |
| Combined (training) | ~88,000 | Both above, cleaned & merged | `cardio` (0/1) |
| Hypertension Dataset | ~175,000 | Kaggle (ankushpanday1) | `Hypertension` (High/Low) |

**Features used:** age, gender, height, weight, systolic BP, diastolic BP, cholesterol (1–3), glucose (1–3), smoking, alcohol, physical activity

**Hypertension extras:** family history, stress level (1–9), salt intake (g/day)

**Cleaning steps** (in `dataset.py`): removes records with impossible BP values (systolic < 70 or > 250), height < 100 cm or > 220 cm, weight < 30 kg or > 200 kg, BMI outside 10–60, and cases where diastolic ≥ systolic.

---

## ML Model

- **Algorithm:** `GradientBoostingClassifier` (scikit-learn)
- **Hyperparameters:** 200 estimators, max depth 4, learning rate 0.05, subsample 0.8
- **Pipeline:** `StandardScaler` → `GradientBoostingClassifier`
- **Train/test split:** 80/20, stratified
- **Performance:** ~73% accuracy, AUC ~0.80 on held-out test set
- **Fallback (Vercel):** rule-based heuristic in `api/index.py` — no sklearn dependency needed

---

## Installation (Local)

### 1. Clone the repo

```bash
git clone https://github.com/yakew7/Cardiovascular-disease-prediction.git
cd Cardiovascular-disease-prediction
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare datasets and train the model

```bash
python3 dataset.py
```

This cleans the raw CSVs, trains the ML model, and saves `model.pkl` and the cleaned CSVs.

### 4. Start the Flask server

```bash
python3 app.py
```

### 5. Open in browser

```
http://localhost:5000
```

---

## Deployment (Vercel)

The app is pre-configured for Vercel via `vercel.json`. The `api/index.py` file is the serverless entry point — it uses a heuristic fallback instead of the sklearn model (since Vercel's free tier doesn't support large binary dependencies like scikit-learn).

```bash
vercel deploy
```

Routes are configured so all Flask page routes (`/risk`, `/reduce`, etc.) are handled by the single serverless function.

---

## API

### `POST /predict`

Accepts JSON with health parameters, returns risk prediction.

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
  "bmi": 25.9
}
```

### `GET /api/vizdata?dataset=cardio`

Returns chart-ready statistics for the selected dataset. Options: `cardio`, `shanxi`, `hypertension`.

---

## Pages

| Route | Description |
|---|---|
| `/` | Home — quick prediction form, BMI calculator, chatbot |
| `/risk` | Guided step-by-step chat assessment with hypertension follow-up |
| `/reduce` | Evidence-based tips for reducing cardiovascular and hypertension risk |
| `/visualize` | 8 interactive charts across 3 datasets |
| `/faq` | Explanations for every input parameter and both models |

---

## Input Parameter Reference

| Parameter | How to Measure | Notes |
|---|---|---|
| Age | Date of birth | In years |
| Gender | Biological sex | 1 = Male, 2 = Female |
| Height | Measuring tape, standing | In centimetres |
| Weight | Flat weighing scale, morning | In kilograms |
| Systolic BP | Digital BP cuff | Upper number, e.g. 120 |
| Diastolic BP | Digital BP cuff | Lower number, e.g. 80 |
| Cholesterol | Lipid panel blood test | 1 = <200, 2 = 200–239, 3 = 240+ mg/dL |
| Glucose | Fasting blood sugar test | 1 = <100, 2 = 100–125, 3 = 126+ mg/dL |
| Smoking | Self-reported | 0 = No, 1 = Yes |
| Alcohol | Self-reported | 0 = No/rarely, 1 = Yes/regularly |
| Physical Activity | Self-reported | 1 = Active (30+ min/day), 0 = Sedentary |
| Family Hx HTN *(optional)* | Ask parents/siblings | Yes / No |
| Stress Level *(optional)* | Self-rated 1–9 | 1 = very calm, 9 = severely stressed |
| Salt Intake *(optional)* | Dietary estimate | Low <5g, Moderate 5–10g, High 10–15g/day |

---

## Disclaimer

CardioAI is for **educational and informational purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

## Author

**Yash Kewlani** — [github.com/yakew7](https://github.com/yakew7)
