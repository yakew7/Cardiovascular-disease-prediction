# Technical Report: Cardiovascular Disease Prediction

**Author:** Yash Kewlani
**Project:** Full-stack machine learning web application predicting cardiovascular disease risk from routine
clinical indicators, with a supplementary hypertension risk assessment.

---

## 1. Problem Statement

Cardiovascular disease (CVD) is one of the leading causes of death worldwide, and much of that risk is
detectable from a small set of routine clinical measurements — blood pressure, cholesterol, glucose, age, and
body composition — long before a cardiac event occurs. The goal of this project was to build an end-to-end system
that takes those measurements as input and returns a calibrated-looking risk score, packaged as a usable web
application rather than a notebook-only exercise. The scope covers the full pipeline: sourcing and cleaning real
patient data, training and comparing multiple classifiers, evaluating the chosen model rigorously (not just on
accuracy), and shipping a working demo with a REST API.

This report documents what was built, how it performs, where it falls short, and what a reader should and should
not conclude from it.

## 2. Data

Two public cardiovascular datasets were combined: a Russian cohort of 70,000 patients (`cardio_train.csv`) and a
Shanxi, China regional cohort of 19,999 patients (`shanxi_cardio.csv`), giving 89,999 raw records with an identical
schema — age, gender, height, weight, systolic/diastolic blood pressure, cholesterol category, glucose category,
smoking, alcohol use, physical activity, and a binary `cardio` target. Full field-level documentation, including
units and value encodings, lives in [`docs/DATASET.md`](DATASET.md).

Age was recorded in days in both raw files and converted to years. BMI was derived from height and weight. Rows
with physiologically implausible values — blood pressure outside 40–250 mmHg, systolic not exceeding diastolic,
height outside 100–220 cm, weight outside 30–200 kg, or BMI outside 10–60 — were dropped rather than clipped, since
self-reported intake data is prone to unit-entry errors (e.g. a missing decimal turning 160 into 1600) that clipping
would silently mask. This removed 2.00% of Russian records and 1.98% of Chinese records, leaving 88,202 combined
records. The full cleaning pipeline, with before/after counts at every step, is in
[`notebooks/01_data_cleaning.ipynb`](../notebooks/01_data_cleaning.ipynb).

A separate, larger dataset (174,982 records, 22 features, from a Kaggle hypertension risk collection spanning ~175
countries) was also incorporated into the project for visualization purposes. It is documented in full in
`docs/DATASET.md`, including an important caveat discussed in Section 6.

Exploratory analysis (`notebooks/02_eda.ipynb`) confirmed the target class is close to balanced — 50.5% no-disease
versus 49.5% disease — which means accuracy is a meaningful headline metric here and no class-imbalance correction
(SMOTE, class weighting) was necessary. Univariate analysis showed the clearest separation between disease and
no-disease groups on systolic blood pressure, age, cholesterol category, and BMI, while binary lifestyle self-reports
(smoking, alcohol, activity) showed weak and in some cases counter-intuitive relationships with the target — most
plausibly because patients already diagnosed with CVD may have changed those behaviors (e.g. quit smoking) after
diagnosis, which would bias a simple correlation toward zero. The two source cohorts were checked for aggregate
distributional differences and found to be very similar (mean age 53.33 vs. 53.35, mean systolic BP 126.67 vs.
126.68), which supported pooling them into a single training set.

## 3. Methodology

Five classifier families were trained on an identical 80/20 train/test split (`random_state=42`, stratified on the
target) so that differences in results are attributable to the model, not to a different sample: Logistic
Regression (linear baseline), K-Nearest Neighbors, a single Decision Tree, Random Forest, and Gradient Boosting.
Each was wrapped in a `StandardScaler → classifier` pipeline. This comparison is the core deliverable of
[`notebooks/03_model_comparison.ipynb`](../notebooks/03_model_comparison.ipynb) and exists specifically so the
deployed model choice (Gradient Boosting) is a documented decision, not an assumption.

Every model was scored on five metrics: accuracy, precision, recall, F1, and ROC-AUC — not accuracy alone, since
accuracy on a roughly-balanced binary target can still hide an imbalance between the two error types that matters a
great deal in a medical screening context (discussed in Section 5).

## 4. Results — Model Comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| **Gradient Boosting (deployed)** | **0.7330** | 0.7512 | 0.6885 | 0.7185 | **0.8018** |
| Random Forest | 0.7309 | **0.7651** | 0.6584 | 0.7078 | 0.7999 |
| Decision Tree | 0.7281 | 0.7554 | 0.6668 | 0.7083 | 0.7930 |
| Logistic Regression | 0.7263 | 0.7526 | 0.6662 | 0.7068 | 0.7885 |
| K-Nearest Neighbors | 0.7223 | 0.7301 | **0.6964** | 0.7129 | 0.7878 |

Full CSV: [`docs/model_comparison_results.csv`](model_comparison_results.csv).

Gradient Boosting is the best or tied-best model on every metric except raw precision (where Random Forest edges it
out at the cost of recall), which is why it is the model shipped in production (`model.pkl`). Notably, every model
family — from a linear baseline to two different tree ensembles — converges to a similar ceiling of roughly 72–73%
accuracy and 0.79–0.80 ROC-AUC. When architecturally very different models all plateau at the same point, that is
evidence the limiting factor is the **information content of the 11 available features** (single-visit,
self-reported clinical intake) rather than model capacity. This is an important, and somewhat humbling, finding:
a more complex model (e.g. a deep neural network) would not be expected to meaningfully outperform Gradient Boosting
on this specific dataset.

## 5. Confusion Matrix and the False Positive / False Negative Trade-off

On the 17,641-record held-out test set, the deployed Gradient Boosting model produced:

| | Predicted: No disease | Predicted: Disease |
|---|---:|---:|
| **Actual: No disease** | 6,917 (TN) | 1,991 (FP) |
| **Actual: Disease** | 2,720 (FN) | 6,013 (TP) |

In a screening context, these two error types are not equally costly. A **false negative** — telling a patient with
real cardiovascular disease that they are low-risk — is the more dangerous failure mode, since it can delay
follow-up testing for a genuine condition. A **false positive** causes unnecessary concern and possibly an
unneeded follow-up visit, but carries far lower downstream risk. By that logic, recall (sensitivity) — the fraction
of true disease cases actually caught, 68.85% here — arguably matters more for this use case than the overall
73.30% accuracy figure. At the model's default 0.5 probability threshold, roughly 3 in 10 people who truly have
cardiovascular disease are classified as low-risk. Because the app already exposes a continuous probability rather
than only a binary label, a product decision to lower the classification threshold could trade some precision for
meaningfully higher recall — that threshold choice is intentionally left as a deployment/product decision rather
than hardcoded into the model.

## 6. Explainability

Two independent feature-importance measures were computed for the deployed model: the Gradient Boosting model's
built-in impurity-based importance, and permutation importance (the drop in held-out ROC-AUC when a feature is
shuffled), which is more robust to bias from high-cardinality or continuous features. Both agree on the ranking:
systolic blood pressure (`ap_hi`) dominates by a wide margin, followed by age, cholesterol category, and
weight/BMI, while smoking, alcohol, and gender contribute very little marginal signal once the clinical measurements
are already present. This ranking matches the classic cardiovascular risk triad (blood pressure, age, cholesterol)
from established clinical literature, which is a useful sanity check that the model learned a physiologically
sensible pattern rather than an artifact of how the data was collected. This is currently a **global**,
dataset-level explanation rather than a per-prediction one (e.g. SHAP values surfaced in the UI for each user's
specific inputs) — per-prediction explainability remains a documented item for future work.

## 7. Bias, Limitations, and an Important Correction

A full accounting is maintained in [`docs/BIAS_AND_LIMITATIONS.md`](BIAS_AND_LIMITATIONS.md); the most significant
finding is worth stating here directly. While preparing this report, it became clear that the project's
"hypertension model" — described in the README and in-app FAQ — is **not actually a trained model**. There is no
`hypertension_model.pkl` and no server-side hypertension inference code; the hypertension risk shown in the UI is
computed entirely client-side by a hand-written point-scoring heuristic in `static/script.js`, using only 3 of the
175k-record hypertension dataset's 22 available features. That heuristic has never been evaluated against the
dataset it is described as using — it has no measured accuracy, precision, recall, or ROC-AUC, unlike the
cardiovascular model documented above. The README has been corrected to describe this accurately rather than imply
parity with the validated cardiovascular model. Training a properly evaluated hypertension model on the richer
22-feature dataset is a natural next step but was treated as out of scope for this pass, since doing it with the
same rigor as the cardio model (train/test split, multi-model comparison, full metric suite) is itself a
project-sized piece of work, not a quick addition.

Other limitations worth flagging: no calibration check exists to confirm the displayed "risk %" corresponds to a
true empirical event rate (it should be read as a relative ranking, not a calibrated probability); no demographic
subgroup fairness audit has been performed beyond the cohort-level check; and large raw/cleaned CSVs and the model
file are committed directly to the Git repository rather than tracked externally, which is a maintainability concern
as datasets grow.

## 8. Conclusion

This project delivers a working, end-to-end cardiovascular risk screening tool: cleaned and documented data, a
five-model comparison justifying the deployed Gradient Boosting classifier, a full evaluation beyond accuracy
(precision/recall/F1/ROC-AUC, confusion matrix, and an explicit discussion of which error type matters more in a
screening context), and global feature-importance explainability consistent with known clinical risk factors. The
project's honest ceiling — roughly 73% accuracy and 0.80 ROC-AUC, consistent across very different model
architectures — is presented as a property of the available features rather than a solvable engineering problem,
and the report deliberately surfaces a real documentation/implementation gap in the hypertension module rather than
letting an inflated claim stand. As stated throughout, and in the app's own disclaimer, this remains an educational
screening aid, not a diagnostic or clinically validated medical device.
