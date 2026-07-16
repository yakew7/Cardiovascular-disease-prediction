# Project Scope Checklist

Tracks the deliverables required to consider this project submission-ready, and what's actually done today.

| # | Item | Status | Notes |
|---|------|:------:|-------|
| 1 | Final scope decision | ☐ | This document is the scope draft — needs sign-off |
| 2 | Dataset documentation | ☐ | Datasets are named in [README.md](README.md#project-structure) but not formally documented (source, size, feature dictionary, license) |
| 3 | Data cleaning notebook | ☐ | Cleaning logic exists in [dataset.py](dataset.py) as a script, not a notebook |
| 4 | EDA notebook | ☐ | Not present — `/visualize` page covers some charts, but no exploratory notebook |
| 5 | Model comparison | ☐ | Only one model per disease (Gradient Boosting) is documented; no comparison against alternatives |
| 6 | Accuracy, precision, recall, F1, ROC-AUC | ☐ | README reports accuracy (~73%) and AUC-ROC (~0.80) only; precision/recall/F1 missing |
| 7 | Confusion matrix | ☐ | Not present |
| 8 | False positive / false negative discussion | ☐ | Not present |
| 9 | Explainability / feature importance | ☐ | Listed under "What's Next" in README as future work (SHAP), not yet implemented |
| 10 | Bias and limitations section | ☐ | Not present — bias audit is listed as future work only |
| 11 | Medical disclaimer | ☑ | Present in [README.md](README.md#disclaimer) |
| 12 | Clean GitHub repo | ☑ | Present, though large raw/processed CSVs and `model.pkl` are committed directly rather than via Git LFS or external storage |
| 13 | Working website/demo | ☑ | Live at the [demo link](https://cardiovascular-disease-prediction-sandy.vercel.app) in README |
| 14 | 1500–2500 word technical report | ☐ | Not present |
| 15 | Resume/project description | ☐ | Not present |

**Legend:** ☑ done · ☐ outstanding
