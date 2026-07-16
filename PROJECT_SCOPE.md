# Project Scope Checklist

Tracks the deliverables required to consider this project submission-ready, and what's actually done today.

| # | Item | Status | Notes |
|---|------|:------:|-------|
| 1 | Final scope decision | ☑ | This checklist itself, now fully closed out — final scope reflected below |
| 2 | Dataset documentation | ☑ | [`docs/DATASET.md`](docs/DATASET.md) — sources, sizes, full feature dictionaries, license notes, data lineage for all 3 datasets |
| 3 | Data cleaning notebook | ☑ | [`notebooks/01_data_cleaning.ipynb`](notebooks/01_data_cleaning.ipynb) — executed, with before/after stats at each step |
| 4 | EDA notebook | ☑ | [`notebooks/02_eda.ipynb`](notebooks/02_eda.ipynb) — executed, class balance, distributions, correlations, cohort comparison |
| 5 | Model comparison | ☑ | [`notebooks/03_model_comparison.ipynb`](notebooks/03_model_comparison.ipynb) — 5 model families compared on an identical split; results in [`docs/model_comparison_results.csv`](docs/model_comparison_results.csv) |
| 6 | Accuracy, precision, recall, F1, ROC-AUC | ☑ | Computed for all 5 models; README + technical report updated with the full table |
| 7 | Confusion matrix | ☑ | Computed and visualized for the deployed model in notebook 3; reproduced in README and technical report |
| 8 | False positive / false negative discussion | ☑ | Written up in notebook 3, [`docs/TECHNICAL_REPORT.md`](docs/TECHNICAL_REPORT.md) §5, and README |
| 9 | Explainability / feature importance | ☑ | Impurity-based + permutation importance computed in notebook 3; global ranking documented (per-prediction SHAP remains future work) |
| 10 | Bias and limitations section | ☑ | [`docs/BIAS_AND_LIMITATIONS.md`](docs/BIAS_AND_LIMITATIONS.md) — data/model limitations, per-cohort check, and a correction of a prior inaccurate claim about the hypertension module |
| 11 | Medical disclaimer | ☑ | Present in [README.md](README.md#disclaimer), now cross-linked to the limitations doc |
| 12 | Clean GitHub repo | ☑ | Present, though large raw/processed CSVs and `model.pkl` are still committed directly rather than via Git LFS or external storage (noted as a limitation, not fixed — would change repo history) |
| 13 | Working website/demo | ☑ | Live at the [demo link](https://cardiovascular-disease-prediction-sandy.vercel.app) in README |
| 14 | 1500–2500 word technical report | ☑ | [`docs/TECHNICAL_REPORT.md`](docs/TECHNICAL_REPORT.md) — ~1,500 words, built from the real notebook results, not placeholder numbers |
| 15 | Resume/project description | ☑ | [`docs/RESUME.md`](docs/RESUME.md) — one-liner, bullet points, and short/long portfolio blurbs |

**Legend:** ☑ done · ☐ outstanding

## Known trade-off carried forward from item 12

Large CSVs and `model.pkl` remain committed directly rather than moved to Git LFS/external storage — doing that
now would rewrite repo history or require a storage migration, which is a separate decision from closing out this
checklist. Flagged here and in [`docs/BIAS_AND_LIMITATIONS.md`](docs/BIAS_AND_LIMITATIONS.md#5-deployment-and-engineering-limitations)
rather than silently left off the list.
