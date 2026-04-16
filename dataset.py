import pandas as pd

# Load Russia dataset (semicolon-separated on Kaggle)
russia = pd.read_csv("cardio_train.csv", sep=";")

# Load China dataset (from the paper's supplementary data)
china = pd.read_csv("shanxi_cardio.csv")

# Dropped id column
russia = russia.drop(columns=["id"], errors="ignore")
china  = china.drop(columns=["id"], errors="ignore")

russia["source"] = "russia"
china["source"]  = "china"

# Step 3: Convert age from days to years (both datasets)
russia["age"] = (russia["age"] / 365).round().astype(int)
china["age"]  = (china["age"]  / 365).round().astype(int)

# Step 4: Add BMI column (optional but useful)
russia["bmi"] = russia["weight"] / ((russia["height"] / 100) ** 2)
china["bmi"]  = china["weight"]  / ((china["height"]  / 100) ** 2)

# Step 5: Make sure both have the same columns in the same order
cols = ["age","gender","height","weight","bmi",
        "ap_hi","ap_lo","cholesterol","gluc",
        "smoke","alco","active","cardio","source"]

russia = russia[cols]
china  = china[cols]

# Step 6: Combine
combined = pd.concat([russia, china], ignore_index=True)

print(combined.shape)       # should be ~85k rows
print(combined["source"].value_counts())
print(combined.isnull().sum())  # check for any nulls

def clean_cardio(df):
    df = df.copy()

    # Remove impossible blood pressure readings
    df = df[df["ap_hi"] >= 70]   # systolic below 70 is not survivable
    df = df[df["ap_hi"] <= 250]  # systolic above 250 is data entry error
    df = df[df["ap_lo"] >= 40]   # diastolic below 40 is not survivable
    df = df[df["ap_lo"] <= 150]  # diastolic above 150 is data entry error
    df = df[df["ap_hi"] > df["ap_lo"]]  # systolic must be > diastolic

    # Remove impossible heights and weights
    df = df[df["height"] >= 100]  # no adult under 100 cm
    df = df[df["height"] <= 220]  # no adult over 220 cm
    df = df[df["weight"] >= 30]   # no adult under 30 kg
    df = df[df["weight"] <= 200]  # no adult over 200 kg

    # Remove impossible BMI
    df = df[(df["bmi"] >= 10) & (df["bmi"] <= 60)]

    return df.reset_index(drop=True)

russia  = clean_cardio(russia)
china   = clean_cardio(china)
combined = clean_cardio(combined)  # if using option A