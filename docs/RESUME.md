# Resume / Project Description

Ready-to-use blurbs for a resume, portfolio site, or LinkedIn project section, in a few lengths.

---

## One-line (resume bullet)

> Built and deployed a full-stack ML web app predicting cardiovascular disease risk (Gradient Boosting, 88K+
> patient records, 0.80 ROC-AUC) with a 5-model comparison, full evaluation suite, and live Flask/Vercel demo.

## Resume bullet points (3–4 lines, for an "Experience" or "Projects" section)

> **Cardiovascular Disease Prediction** — *Personal project* | [Live demo](https://cardiovascular-disease-prediction-sandy.vercel.app)
> - Built an end-to-end ML pipeline on 88,202 cleaned patient records from two public cardiovascular datasets,
>   comparing 5 classifier families (Logistic Regression, KNN, Decision Tree, Random Forest, Gradient Boosting) and
>   selecting the best on a full metric suite (accuracy, precision, recall, F1, ROC-AUC), not accuracy alone.
> - Achieved 73.3% accuracy / 0.80 ROC-AUC with Gradient Boosting; documented confusion-matrix trade-offs and
>   feature importance (permutation + impurity-based) to explain predictions in clinically meaningful terms.
> - Shipped a Flask REST API and interactive frontend (Chart.js visualizations, guided risk assessment) deployed to
>   Vercel, with a written technical report covering methodology, limitations, and responsible-use disclaimers.

## Short project description (~100 words, for a portfolio/README-style listing)

> A full-stack machine learning web application that predicts cardiovascular disease risk from 11 routine clinical
> indicators (age, blood pressure, cholesterol, BMI, lifestyle factors). Trained and compared five classifier
> families on 88,202 cleaned patient records from two public datasets, selecting a Gradient Boosting model
> (73.3% accuracy, 0.80 ROC-AUC) after evaluating precision, recall, F1, and confusion-matrix trade-offs relevant to
> medical screening. Includes global feature-importance explainability, a documented bias/limitations analysis, and
> a deployed Flask + Vercel demo with a REST API. Built end-to-end: data cleaning, EDA, model comparison, evaluation,
> and a live interactive frontend.

## Longer project description (~200 words, for a portfolio page or cover letter)

> I built a full-stack machine learning application that predicts cardiovascular disease risk from routine clinical
> measurements — blood pressure, cholesterol, glucose, age, BMI, and lifestyle factors — and packaged it as a live
> web app rather than a one-off notebook. The pipeline covers the full lifecycle: sourcing and cleaning two public
> patient datasets (Russian and Chinese cohorts, 88,202 records after removing physiologically implausible values),
> exploratory analysis to understand which features actually separate disease from non-disease cases, and a
> five-model comparison (Logistic Regression, KNN, Decision Tree, Random Forest, Gradient Boosting) trained on an
> identical split so the final model choice — Gradient Boosting, 73.3% accuracy and 0.80 ROC-AUC — is a documented
> decision rather than a default.
>
> Rather than stopping at accuracy, I evaluated the model on precision, recall, F1, and a full confusion matrix, and
> wrote up why false negatives matter more than false positives in a screening context. I also computed feature
> importance two independent ways to confirm the model learned a clinically sensible signal (blood pressure, age,
> and cholesterol dominate, matching established risk factors), and wrote an honest bias/limitations section —
> including catching and correcting an inaccurate claim in my own documentation about a secondary hypertension
> feature. The result is deployed live with a Flask REST API and an interactive frontend.

---

*Tailor the length/tense to the target (resume bullets stay in past tense, portfolio blurbs can be first-person).
Update the accuracy/ROC-AUC figures here if the model is retrained — they are pulled from
[`docs/model_comparison_results.csv`](model_comparison_results.csv) as of this writing.*
