import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as sc
import sklearn as sk
import seaborn as sns

# Load Russia dataset
russia = pd.read_csv("cardio_train.csv", sep=";")

# Load China dataset
china = pd.read_csv("shanxi_cardio.csv")

# Dropped id column
russia = russia.drop(columns=["id"], errors="ignore")
china  = china.drop(columns=["id"], errors="ignore")

russia["source"] = "russia"
china["source"]  = "china"

#Converted age from days to years (both datasets)
russia["age"] = (russia["age"] / 365).round().astype(int)
china["age"]  = (china["age"]  / 365).round().astype(int)

#Added BMI
russia["bmi"] = russia["weight"] / ((russia["height"] / 100) ** 2)
china["bmi"]  = china["weight"]  / ((china["height"]  / 100) ** 2)

# Columns
cols = ["age","gender","height","weight","bmi","ap_hi","ap_lo","cholesterol","gluc","smoke","alco","active","cardio","source"]

russia = russia[cols]
china  = china[cols]
combined = pd.concat([russia, china], ignore_index=True)

print(combined.shape)
print(combined["source"].value_counts())
print(combined.isnull().sum())

def clean_cardio(df):
    df = df.copy()

    # Removed impossible blood pressure readings
    df = df[df["ap_hi"] >= 70]   
    df = df[df["ap_hi"] <= 250]  
    df = df[df["ap_lo"] >= 40]   
    df = df[df["ap_lo"] <= 150]  
    df = df[df["ap_hi"] > df["ap_lo"]]

    # Removed impossible heights and weights
    df = df[df["height"] >= 100]  
    df = df[df["height"] <= 220]
    df = df[df["weight"] >= 30]
    df = df[df["weight"] <= 200]

    # Removed impossible BMI
    df = df[(df["bmi"] >= 10) & (df["bmi"] <= 60)]

    return df.reset_index(drop=True)

russia  = clean_cardio(russia)
china   = clean_cardio(china)
combined = clean_cardio(combined)

CHOLESTEROL_MAP = {1: 180, 2: 220, 3: 270}   # mg/dL
GLUCOSE_MAP     = {1:  90, 2: 115, 3: 180}   # mg/dL

for df in [russia, china, combined]:
    df["cholesterol_mgdl"] = df["cholesterol"].map(CHOLESTEROL_MAP)
    df["gluc_mgdl"]        = df["gluc"].map(GLUCOSE_MAP)

    #readable label columns
    chol_labels = {1: "Normal (<200)", 2: "Above Normal (200–239)", 3: "Well Above Normal (≥240)"}
    gluc_labels = {1: "Normal (<100)", 2: "Above Normal (100–125)", 3: "Well Above Normal (≥126)"}
    df["cholesterol_label"] = df["cholesterol"].map(chol_labels)
    df["gluc_label"]        = df["gluc"].map(gluc_labels)

print("\nCholesterol value mapping (mg/dL):")
print(combined[["cholesterol", "cholesterol_mgdl", "cholesterol_label"]].drop_duplicates().sort_values("cholesterol"))

print("\nGlucose value mapping (mg/dL):")
print(combined[["gluc", "gluc_mgdl", "gluc_label"]].drop_duplicates().sort_values("gluc"))
