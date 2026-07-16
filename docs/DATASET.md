# Dataset Documentation

This project draws on three public datasets. This document records their source, size, license status, and full
feature dictionary so the data lineage is auditable independent of the code.

---

## 1. Cardiovascular Disease datasets (primary model)

### 1a. `cardio_train.csv` — Russian cohort

| | |
|---|---|
| Source | "Cardiovascular Disease dataset" — Kaggle, uploaded by Svetlana Ulianova (per project FAQ / commit history; search Kaggle for the exact listing rather than relying on a hardcoded link here) |
| Records | 70,000 |
| Population | Adult patients, Russia |
| License | Kaggle dataset — see the dataset page for the uploader's stated terms; no explicit open license file is bundled with the raw CSV in this repo |
| Format | `;`-separated CSV |

### 1b. `shanxi_cardio.csv` — Chinese regional cohort

| | |
|---|---|
| Source | Shanxi regional cardiovascular dataset (comma-separated, same schema as the Russian cohort) |
| Records | 19,999 |
| Population | Adult patients, Shanxi province, China |
| License | As bundled in this repo; treat as research/educational use only pending confirmation of upstream terms |
| Format | `,`-separated CSV |

### Combined feature dictionary (both cohorts, pre-cleaning)

| Field | Type | Description | Values / Units |
|---|---|---|---|
| `id` | int | Row identifier | Dropped before modeling — no predictive signal |
| `age` | int | Age | Stored in **days** in the raw files; converted to years during cleaning |
| `gender` | int | Biological sex | `1` = female, `2` = male |
| `height` | int | Height | cm |
| `weight` | float | Weight | kg |
| `ap_hi` | int | Systolic blood pressure | mmHg |
| `ap_lo` | int | Diastolic blood pressure | mmHg |
| `cholesterol` | int | Cholesterol category | `1` normal, `2` above normal, `3` well above normal |
| `gluc` | int | Glucose category | `1` normal, `2` above normal, `3` well above normal |
| `smoke` | int | Smoker | `0` no, `1` yes |
| `alco` | int | Alcohol intake | `0` no, `1` yes |
| `active` | int | Physically active | `0` no, `1` yes |
| `cardio` | int | **Target** — presence of cardiovascular disease | `0` no, `1` yes |

Derived fields added during cleaning (see [`notebooks/01_data_cleaning.ipynb`](../notebooks/01_data_cleaning.ipynb)):
`bmi`, `cholesterol_mgdl`, `gluc_mgdl`, `cholesterol_label`, `gluc_label`, `source`.

### Cleaned outputs

| File | Rows | Notes |
|---|---:|---|
| `cardio_clean.csv` | 68,598 | Russian cohort after outlier filtering (2.00% dropped) |
| `shanxi_clean.csv` | 19,604 | Shanxi cohort after outlier filtering (1.98% dropped) |
| `combined_clean.csv` | 88,202 | Both cohorts pooled, used to train `model.pkl` |

Target class balance in `combined_clean.csv`: **50.5% / 49.5%** (no-disease / disease) — effectively balanced, so no
resampling (SMOTE, class weights) is applied or needed.

---

## 2. Hypertension Risk Prediction dataset

| | |
|---|---|
| Source | "Hypertension Risk Prediction Dataset" — Kaggle, uploaded by ankushpanday1 (per project FAQ; search Kaggle for the exact listing rather than relying on a hardcoded link here) |
| Records | 174,982 |
| Population | ~175 countries |
| License | Kaggle dataset — treat as research/educational use pending confirmation of upstream terms |
| Format | Comma-separated CSV, 23 columns |

### Full feature dictionary

| Field | Type | Description |
|---|---|---|
| `Country` | str | Patient's country |
| `Age` | int | Age in years |
| `BMI` | float | Body mass index |
| `Cholesterol` | int | Cholesterol, mg/dL |
| `Systolic_BP` | int | Systolic blood pressure, mmHg |
| `Diastolic_BP` | int | Diastolic blood pressure, mmHg |
| `Smoking_Status` | str | Never / Former / Current |
| `Alcohol_Intake` | float | Alcohol units |
| `Physical_Activity_Level` | str | Low / Moderate / High |
| `Family_History` | str | Yes / No — family history of hypertension |
| `Diabetes` | str | Yes / No |
| `Stress_Level` | int | Self-rated stress, 1–9 |
| `Salt_Intake` | float | Daily salt intake, g/day |
| `Sleep_Duration` | float | Hours/night |
| `Heart_Rate` | int | Resting heart rate, bpm |
| `LDL` | int | LDL cholesterol, mg/dL |
| `HDL` | int | HDL cholesterol, mg/dL |
| `Triglycerides` | int | mg/dL |
| `Glucose` | int | mg/dL |
| `Gender` | str | Male / Female |
| `Education_Level` | str | Highest education level |
| `Employment_Status` | str | Employment status |
| `Hypertension` | str | **Target** — `High` (125,781 rows, 71.9%) / `Low` (49,201 rows, 28.1%) |

No missing values in any column.

### Important: how this dataset is actually used today

The README and in-app FAQ describe a "hypertension model," but as of this writing **no model is trained on this
dataset**. There is no `hypertension_model.pkl`, no training code for it in `dataset.py`, and no server-side
inference for it in `app.py`. The hypertension risk score shown in the UI is computed **entirely client-side** by a
hand-written point-scoring heuristic in [`static/script.js`](../static/script.js) (`calcHypertensionRisk`), using
only 3 of this dataset's 22 predictor columns (family history, stress level, salt intake) plus a couple of the
cardio-model's own inputs (age, BMI, blood pressure).

This is flagged in detail in [`BIAS_AND_LIMITATIONS.md`](BIAS_AND_LIMITATIONS.md#4-the-hypertension-module-is-not-a-trained-model)
and corrected in the README's model table — the 175k-record dataset is currently only used for the `/visualize`
dataset charts, not for training.

---

## Data lineage summary

```
cardio_train.csv (raw, Russia) ─┐
                                 ├─► clean_cardio() ─► combined_clean.csv ─► dataset.py training ─► model.pkl
shanxi_cardio.csv (raw, China) ─┘

hypertension_dataset.csv (raw) ─► used for /visualize charts only — not currently used to train any model
```
