import pandas as pd
import numpy as np
import os

BASE = os.path.dirname(__file__)

# ── Load ────────────────────────────────────────────────────────────────────
russia = pd.read_csv(os.path.join(BASE, "cardio_train.csv"), sep=";")
china  = pd.read_csv(os.path.join(BASE, "shanxi_cardio.csv"))

# Drop id
russia = russia.drop(columns=["id"], errors="ignore")
china  = china.drop(columns=["id"], errors="ignore")

russia["source"] = "russia"
china["source"]  = "china"

# Age days → years
russia["age"] = (russia["age"] / 365).round().astype(int)
china["age"]  = (china["age"]  / 365).round().astype(int)

# BMI
russia["bmi"] = russia["weight"] / ((russia["height"] / 100) ** 2)
china["bmi"]  = china["weight"]  / ((china["height"]  / 100) ** 2)

# Align columns
cols = ["age","gender","height","weight","bmi","ap_hi","ap_lo",
        "cholesterol","gluc","smoke","alco","active","cardio","source"]
russia = russia[cols]
china  = china[cols]

combined = pd.concat([russia, china], ignore_index=True)

# ── Clean ───────────────────────────────────────────────────────────────────
def clean_cardio(df):
    df = df.copy()
    df = df[df["ap_hi"]  >= 70]
    df = df[df["ap_hi"]  <= 250]
    df = df[df["ap_lo"]  >= 40]
    df = df[df["ap_lo"]  <= 150]
    df = df[df["ap_hi"]  >  df["ap_lo"]]
    df = df[df["height"] >= 100]
    df = df[df["height"] <= 220]
    df = df[df["weight"] >= 30]
    df = df[df["weight"] <= 200]
    df = df[(df["bmi"] >= 10) & (df["bmi"] <= 60)]
    return df.reset_index(drop=True)

russia   = clean_cardio(russia)
china    = clean_cardio(china)
combined = clean_cardio(combined)

# ── Mappings ─────────────────────────────────────────────────────────────────
CHOLESTEROL_MAP = {1: 180, 2: 220, 3: 270}
GLUCOSE_MAP     = {1:  90, 2: 115, 3: 180}

for df in [russia, china, combined]:
    df["cholesterol_mgdl"] = df["cholesterol"].map(CHOLESTEROL_MAP)
    df["gluc_mgdl"]        = df["gluc"].map(GLUCOSE_MAP)
    chol_labels = {1: "Normal (<200)", 2: "Above Normal (200–239)", 3: "Well Above Normal (≥240)"}
    gluc_labels = {1: "Normal (<100)", 2: "Above Normal (100–125)", 3: "Well Above Normal (≥126)"}
    df["cholesterol_label"] = df["cholesterol"].map(chol_labels)
    df["gluc_label"]        = df["gluc"].map(gluc_labels)

# ── Train & save ML model ────────────────────────────────────────────────────
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, roc_auc_score
import joblib

FEATURES = ["age","gender","height","weight","ap_hi","ap_lo",
            "cholesterol","gluc","smoke","alco","active"]

df_model = combined.dropna(subset=FEATURES + ["cardio"])
X = df_model[FEATURES].values
y = df_model["cardio"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", GradientBoostingClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        subsample=0.8, random_state=42))
])

print("Training model…")
pipe.fit(X_train, y_train)

acc = accuracy_score(y_test, pipe.predict(X_test))
auc = roc_auc_score(y_test, pipe.predict_proba(X_test)[:, 1])
print(f"  Accuracy : {acc:.4f}")
print(f"  ROC-AUC  : {auc:.4f}")

model_path = os.path.join(BASE, "model.pkl")
joblib.dump(pipe, model_path)
print(f"Model saved → {model_path}")

# ── Export cleaned CSVs for the viz API ──────────────────────────────────────
russia.to_csv(os.path.join(BASE, "cardio_clean.csv"),  index=False)
china.to_csv( os.path.join(BASE, "shanxi_clean.csv"),  index=False)
combined.to_csv(os.path.join(BASE, "combined_clean.csv"), index=False)
print("Cleaned CSVs saved.")

if __name__ == "__main__":
    print("\nDataset shapes after cleaning:")
    print(f"  Russia   : {russia.shape}")
    print(f"  China    : {china.shape}")
    print(f"  Combined : {combined.shape}")
