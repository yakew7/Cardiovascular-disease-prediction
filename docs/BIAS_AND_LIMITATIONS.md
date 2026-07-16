# Bias and Limitations

Honest accounting of where this project's model and data fall short, so results aren't overstated. Numbers below
come from [`notebooks/03_model_comparison.ipynb`](../notebooks/03_model_comparison.ipynb) unless noted otherwise.

---

## 1. Data limitations

- **Self-reported intake data.** Smoking, alcohol use, and physical activity are single binary self-reports
  collected at one point in time, not measured or longitudinal. This likely explains why these fields show the
  weakest (and sometimes counter-intuitive) correlation with the disease target in EDA — e.g. patients who already
  have cardiovascular disease may have quit smoking *after* diagnosis, which would bias the raw correlation toward
  zero or even negative.
- **Single-visit clinical snapshot.** Blood pressure, cholesterol, and glucose are single readings, not averaged
  over multiple visits — clinically, a single elevated BP reading is not the same as diagnosed hypertension.
- **No ground-truth verification.** The `cardio` label's provenance (self-report vs. clinical diagnosis vs.
  screening test) is not documented by the original dataset publishers, so its reliability can't be independently
  verified from this repo alone.
- **Only two source populations.** Training data covers Russian and Shanxi (China) cohorts only. Aggregate summary
  statistics for the two cohorts are nearly identical (see below), which is convenient for pooling but does **not**
  establish that the model generalizes to other populations, healthcare systems, or measurement conventions.

## 2. Per-cohort performance check

Pooling two source cohorts risks the model implicitly overfitting to whichever cohort is easier, while looking fine
in aggregate. This was checked directly rather than assumed:

| Cohort | Mean age | Mean BMI | Mean systolic BP | Disease prevalence |
|---|---:|---:|---:|---:|
| Russia | 53.33 | 27.45 | 126.67 | 49% |
| China (Shanxi) | 53.35 | 27.43 | 126.68 | 50% |

The two cohorts are close enough in aggregate distribution that a single pooled model is a reasonable choice for
this dataset — but this is a property of *this specific pair* of datasets, not a general result. A new regional
dataset with a meaningfully different population (age structure, measurement units, clinical thresholds) should not
be assumed to work with the current model without re-validating per-cohort accuracy.

## 3. Model limitations

- **Accuracy ceiling ~73%, ROC-AUC ~0.80 across every model family tried** (Logistic Regression, KNN, Decision
  Tree, Random Forest, Gradient Boosting — see [model comparison results](model_comparison_results.csv)). Since
  substantially different model architectures all converge to a similar ceiling, the limitation is very likely the
  **information content of the 11 available features**, not the choice of algorithm. A more expressive model would
  not be expected to meaningfully beat this ceiling on this data.
- **False negative rate.** At the default 0.5 probability threshold, the deployed model produces **2,720 false
  negatives out of 8,733 true positive cases** in the held-out test set (recall ≈ 68.9%) — meaning roughly 3 in 10
  people who actually have cardiovascular disease are told they're low-risk. See the confusion matrix and FP/FN
  discussion in [`03_model_comparison.ipynb`](../notebooks/03_model_comparison.ipynb) for the full breakdown and why
  this matters more than the false-positive rate in a screening context.
- **No calibration check.** The model outputs a probability (`predict_proba`), and the app presents it directly as
  a "confidence %," but no calibration analysis (e.g. reliability diagram, Brier score) has been done to confirm
  that a reported "78% risk" actually corresponds to a ~78% empirical event rate. Treat the displayed percentage as
  a relative risk ranking, not a calibrated probability, until this is checked.
- **No demographic subgroup audit.** Model performance has not been broken out by `gender` or `age` bracket beyond
  the cohort-level check above. A subgroup fairness audit (e.g. accuracy/recall by age decile and by gender) is
  listed as future work in the README and has not been done here.

## 4. The hypertension module is not a trained model

The README and in-app FAQ describe a "hypertension risk model." In the current codebase, this is **not accurate** —
there is no trained hypertension model, no `hypertension_model.pkl`, and no hypertension inference path in
`app.py`. The hypertension score shown in the UI is computed **entirely client-side** by a hand-written point
threshold heuristic (`calcHypertensionRisk` in [`static/script.js`](../static/script.js)) using only 3 of the
175k-record hypertension dataset's 22 available predictor columns (family history, stress, salt intake), plus a
couple of the cardio form's own fields (age, BMI, blood pressure).

This means:
- The hypertension "risk" the app shows has **no empirical accuracy, precision, recall, or ROC-AUC** — it has never
  been validated against the dataset it claims to use, unlike the cardiovascular model in this report.
- The 175k-record hypertension dataset — with 22 features far richer than the 3 currently used — is only consumed
  today by the `/visualize` dataset charts, not by any predictive model.
- README's Hypertension Module table has been corrected to describe this accurately (see
  [`README.md`](../README.md#hypertension-module)) rather than implying parity with the validated cardiovascular
  model.

Training an actual model on the hypertension dataset (which has a real, richer feature set and a clear binary
target) is a natural next step, but is out of scope for this pass — it isn't listed in the original checklist,
and doing it properly deserves the same rigor (train/test split, model comparison, metrics) as the cardio model,
not a rushed addition.

## 5. Deployment and engineering limitations

- Large raw and cleaned CSVs (up to ~19 MB) and `model.pkl` are committed directly to the Git repository rather than
  tracked via Git LFS or pulled from external storage at build time — this bloats clone size and is not a scalable
  pattern if datasets grow.
- The Flask app has no authentication, rate limiting, or input-range validation on the `/predict` endpoint beyond
  what the frontend form enforces — a direct API call with out-of-range values (e.g. negative age) is not rejected
  server-side.

## 6. Ethical / responsible-use notes

This tool is a **screening aid for educational purposes**, not a diagnostic device, and has not undergone any
clinical validation, regulatory review (e.g. FDA/CE marking), or peer review. See the
[medical disclaimer](../README.md#disclaimer) in the README, which should be read before treating any output from
this app as clinically meaningful.
