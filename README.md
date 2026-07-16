# Cardiovascular Disease Prediction

> *A machine learning web app that predicts cardiovascular disease risk from clinical indicators — trained on 70,000+ real patient records, extended with a dedicated hypertension risk module.*

**by Yash Kewlani · [Live Demo →](https://cardiovascular-disease-prediction-sandy.vercel.app)**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-lightgrey?style=flat-square&logo=flask)
![scikit-learn](https://img.shields.io/badge/scikit--learn-GradientBoosting-orange?style=flat-square&logo=scikit-learn)
![Deployed](https://img.shields.io/badge/Deployed-Vercel-black?style=flat-square&logo=vercel)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What This Is

A full-stack AI web application that takes 11 clinical inputs — age, blood pressure, cholesterol, BMI, lifestyle factors — and predicts whether a patient is at high or low risk for cardiovascular disease.

The app covers **two diseases**. Alongside the main cardiovascular model, a separate **hypertension risk module** is trained on `hypertension_dataset.csv` — a dedicated dataset with its own features (family history, stress level, salt intake) not present in the cardio datasets. The two models run independently and show results side by side.

Built end-to-end: data cleaning, model training, REST API, and a full interactive frontend with risk visualizations.

---

## Model Performance

### Cardiovascular Disease Model

Five classifier families were trained and compared on an identical split before picking the deployed model — see
[`notebooks/03_model_comparison.ipynb`](notebooks/03_model_comparison.ipynb) for the full evaluation and
[`docs/model_comparison_results.csv`](docs/model_comparison_results.csv) for raw numbers.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|:--------:|:---------:|:------:|:--:|:-------:|
| **Gradient Boosting (deployed)** | **73.30%** | 75.12% | 68.85% | 71.85% | **0.8018** |
| Random Forest | 73.09% | 76.51% | 65.84% | 70.78% | 0.7999 |
| Decision Tree | 72.81% | 75.54% | 66.68% | 70.83% | 0.7930 |
| Logistic Regression | 72.63% | 75.26% | 66.62% | 70.68% | 0.7885 |
| K-Nearest Neighbors | 72.23% | 73.01% | 69.64% | 71.29% | 0.7878 |

| | |
|--------|:-----:|
| Training records | 88,202 (after cleaning) |
| Datasets | `cardio_train.csv` + `shanxi_cardio.csv` |

**Confusion matrix** (held-out test set, n=17,641):

| | Predicted: No disease | Predicted: Disease |
|---|:---:|:---:|
| **Actual: No disease** | 6,917 (TN) | 1,991 (FP) |
| **Actual: Disease** | 2,720 (FN) | 6,013 (TP) |

At the default 0.5 threshold, the model misses ~31% of true disease cases (false negatives) — a more important
number than raw accuracy in a screening context, since a false negative delays follow-up on a real condition while
a false positive just causes unnecessary concern. Full discussion in
[`docs/BIAS_AND_LIMITATIONS.md`](docs/BIAS_AND_LIMITATIONS.md).

**Explainability:** feature importance (both impurity-based and permutation importance) consistently ranks
systolic blood pressure, age, cholesterol, and BMI/weight as the dominant predictors, with smoking, alcohol, and
gender contributing very little marginal signal — consistent with the classic clinical cardiovascular risk triad.
This is a global, dataset-level explanation; per-prediction explainability (e.g. SHAP in the UI) is still future
work. See [Explainability](docs/TECHNICAL_REPORT.md#6-explainability) in the technical report.

### Hypertension Module

> ⚠ **Correction:** earlier versions of this README described a trained "Gradient Boosting Classifier" for
> hypertension. That was inaccurate. As documented in [`docs/DATASET.md`](docs/DATASET.md#important-how-this-dataset-is-actually-used-today)
> and [`docs/BIAS_AND_LIMITATIONS.md`](docs/BIAS_AND_LIMITATIONS.md#4-the-hypertension-module-is-not-a-trained-model),
> there is **no trained hypertension model** in this repo.

| | |
|--------|:-----:|
| Method | Client-side point-scoring heuristic (`calcHypertensionRisk` in [`static/script.js`](static/script.js)) |
| Dataset | `hypertension_dataset.csv` (174,982 records, 22 features) — currently used only for the `/visualize` charts, not for training |
| Features used by the heuristic | Family history, stress level, salt intake, age, BMI, blood pressure (3 of the dataset's 22 available features) |
| Validated accuracy/precision/recall/ROC-AUC | None — unlike the cardiovascular model above, this heuristic has never been evaluated against the dataset it's based on |

Training a properly evaluated model on the full 22-feature hypertension dataset is a reasonable next step, but is
out of scope for the current pass — see [`docs/BIAS_AND_LIMITATIONS.md`](docs/BIAS_AND_LIMITATIONS.md) for why.

The cardiovascular model also includes a **heuristic fallback** — if `model.pkl` isn't available, risk is calculated from clinical thresholds for BMI, blood pressure, cholesterol, glucose, and lifestyle factors.

---

## Features

- **Cardiovascular risk prediction** — input 11 clinical indicators, get a probability score and high/low risk classification
- **Hypertension risk module** — separate client-side scoring heuristic with its own dedicated inputs ([not yet a trained/validated model](#hypertension-module))
- **Interactive visualizations** — age distribution, gender comparison, cholesterol risk, BMI vs blood pressure scatter, physical activity analysis
- **Multi-dataset support** — Kaggle cardio dataset + Shanxi regional dataset
- **REST API** — `POST /predict` endpoint for programmatic access
- **Fallback heuristics** — works without the model file using clinical thresholds

---

## Tech Stack

| Layer | Details |
|-------|---------|
| Backend | Flask, Python, scikit-learn, pandas, NumPy, joblib |
| Frontend | HTML, CSS, JavaScript (Chart.js) |
| Deployment | Vercel |

---

## Project Structure

```
Cardiovascular-disease-prediction/
│
├── App.py                        # Flask app — routes, prediction API, viz data API
├── dataset.py                    # Data cleaning + model training script
├── model.pkl                     # Trained Gradient Boosting model (cardiovascular)
├── requirements.txt
├── CHANGELOG.md
│
├── cardio_train.csv              # Primary cardio dataset (Kaggle, ~70k records)
├── shanxi_cardio.csv             # Secondary cardio dataset (Shanxi regional)
├── cardio_clean.csv              # Cleaned cardio dataset
├── shanxi_clean.csv              # Cleaned Shanxi dataset
├── combined_clean.csv            # Merged dataset used for model training
├── hypertension_dataset.csv      # Hypertension dataset (currently viz-only, see docs/DATASET.md)
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb    # Cleaning pipeline walkthrough with before/after stats
│   ├── 02_eda.ipynb              # Exploratory data analysis and visualizations
│   └── 03_model_comparison.ipynb # 5-model comparison, metrics, confusion matrix, explainability
│
├── docs/
│   ├── DATASET.md                # Full dataset documentation and feature dictionary
│   ├── BIAS_AND_LIMITATIONS.md   # Bias, limitations, and known gaps
│   ├── TECHNICAL_REPORT.md       # Full technical report
│   ├── RESUME.md                 # Resume / project description blurbs
│   └── model_comparison_results.csv
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

```bash
git clone https://github.com/yakew7/Cardiovascular-disease-prediction.git
cd Cardiovascular-disease-prediction
pip install -r requirements.txt
```

Train the model and clean the datasets:

```bash
python3 dataset.py
```

Start the Flask server:

```bash
python3 App.py
```

Open `http://localhost:5000` in your browser.

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

`prediction: 1` = high risk · `prediction: 0` = low risk

### `GET /api/vizdata?dataset=cardio`

Returns aggregated dataset statistics for all visualizations. Supports `dataset=cardio` or `dataset=shanxi`.

---

## Input Features

### Cardiovascular Model

| Feature | Description | Values |
|---------|-------------|--------|
| `age` | Age in years | e.g. `45` |
| `gender` | Biological sex | `1` = female, `2` = male |
| `height` | Height in cm | e.g. `170` |
| `weight` | Weight in kg | e.g. `75` |
| `ap_hi` | Systolic blood pressure | e.g. `140` |
| `ap_lo` | Diastolic blood pressure | e.g. `90` |
| `cholesterol` | Cholesterol level | `1` = normal, `2` = above normal, `3` = well above |
| `gluc` | Glucose level | `1` = normal, `2` = above normal, `3` = well above |
| `smoke` | Smoking | `0` = no, `1` = yes |
| `alco` | Alcohol intake | `0` = no, `1` = yes |
| `active` | Physical activity | `0` = no, `1` = yes |

### Hypertension Model

Trained on `hypertension_dataset.csv` — entirely separate from the cardio training data. These fields are optional and do not affect the cardiovascular prediction.

| Feature | Description | Values |
|---------|-------------|--------|
| `family_hx` | Family history of hypertension | `0` = no, `1` = yes |
| `stress` | Average daily stress level | `1` (very low) – `9` (very high) |
| `salt_intake` | Daily salt consumption | `low` (<5 g/day), `moderate` (5–10 g/day), `high` (10–15 g/day) |

> A family history of hypertension roughly doubles baseline risk. Chronic stress elevates cortisol and pushes blood pressure up over time. The WHO recommends staying under 5 g of salt per day — most processed food exceeds this.

---

## Visualizations

Six charts across both datasets on the `/visualize` page:

- Age distribution by disease status
- Gender-based disease comparison
- Cholesterol level risk analysis
- Smoking impact breakdown
- BMI vs systolic blood pressure scatter
- Physical activity comparison

---

## What's Next

- [ ] Per-prediction SHAP explainability in the UI (global feature importance is done — see [Model Performance](#cardiovascular-disease-model))
- [ ] A properly trained, evaluated hypertension model (the module is currently a heuristic — see [Hypertension Module](#hypertension-module))
- [ ] Deep learning model comparison (Keras/PyTorch)
- [ ] User authentication + saved risk history
- [ ] Medical report PDF upload and parsing
- [ ] Advanced analytics dashboard
- [ ] Demographic subgroup fairness audit (cohort-level check is done — see [Bias and Limitations](docs/BIAS_AND_LIMITATIONS.md))
- [ ] Model calibration check (reliability diagram / Brier score) for the displayed risk percentage

---

## Documentation

| Doc | Covers |
|---|---|
| [`docs/DATASET.md`](docs/DATASET.md) | Full dataset documentation — sources, sizes, feature dictionaries, data lineage |
| [`notebooks/01_data_cleaning.ipynb`](notebooks/01_data_cleaning.ipynb) | Data cleaning pipeline with before/after statistics |
| [`notebooks/02_eda.ipynb`](notebooks/02_eda.ipynb) | Exploratory analysis and visualizations |
| [`notebooks/03_model_comparison.ipynb`](notebooks/03_model_comparison.ipynb) | 5-model comparison, full metrics, confusion matrix, FP/FN discussion, explainability |
| [`docs/BIAS_AND_LIMITATIONS.md`](docs/BIAS_AND_LIMITATIONS.md) | Data/model limitations, per-cohort check, and the hypertension-module correction |
| [`docs/TECHNICAL_REPORT.md`](docs/TECHNICAL_REPORT.md) | Full technical report (methodology, results, limitations) |
| [`docs/RESUME.md`](docs/RESUME.md) | Resume/portfolio project description blurbs |

---

## Disclaimer

This project is for educational and research purposes only. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider. See [Bias and Limitations](docs/BIAS_AND_LIMITATIONS.md) for a detailed accounting of what this project does not validate or guarantee.

---

*Built by [Yash Kewlani](https://github.com/yakew7)*
