from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# ── Load datasets ──────────────────────────────────────────────
BASE = os.path.dirname(__file__)
cardio_df = None
shanxi_df = None

try:
    cardio_df = pd.read_csv(os.path.join(BASE, 'cardio_train.csv'), sep=';')
    # Age in cardio_train is in days — convert to years
    cardio_df['age_years'] = (cardio_df['age'] / 365).astype(int)
    print(f"[CardioAI] Loaded cardio_train.csv — {len(cardio_df)} rows")
except Exception as e:
    print(f"[CardioAI] cardio_train.csv not found: {e}")

try:
    shanxi_df = pd.read_csv(os.path.join(BASE, 'shanxi_cardio.csv'))
    print(f"[CardioAI] Loaded shanxi_cardio.csv — {len(shanxi_df)} rows")
except Exception as e:
    print(f"[CardioAI] shanxi_cardio.csv not found: {e}")

# ── Optional: load ML model ────────────────────────────────────
model = None
try:
    import joblib
    model = joblib.load(os.path.join(BASE, 'model.pkl'))
    print("[CardioAI] ML model loaded")
except:
    print("[CardioAI] No model.pkl found — using fallback logic")

# ── Pages ──────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/risk')
def risk():
    return render_template('risk.html')

@app.route('/reduce')
def reduce():
    return render_template('reduce.html')

@app.route('/visualize')
def visualize():
    return render_template('visualize.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

# ── Prediction API ─────────────────────────────────────────────

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    try:
        age    = float(data['age'])
        gender = int(data['gender'])
        height = float(data['height'])
        weight = float(data['weight'])
        ap_hi  = float(data['ap_hi'])
        ap_lo  = float(data['ap_lo'])
        chol   = int(data.get('cholesterol', 1))
        gluc   = int(data.get('gluc', 1))
        smoke  = int(data.get('smoke', 0))
        alco   = int(data.get('alco', 0))
        active = int(data.get('active', 1))

        bmi = weight / ((height / 100) ** 2)

        if model:
            # Use trained model — adjust feature order to match your training
            features = np.array([[age, gender, height, weight, ap_hi, ap_lo, chol, gluc, smoke, alco, active]])
            pred = int(model.predict(features)[0])
            try:
                prob = float(model.predict_proba(features)[0][1])
            except:
                prob = 0.5
        else:
            # Fallback heuristic
            risk_score = 0
            if bmi > 25:      risk_score += 1
            if bmi > 30:      risk_score += 1
            if ap_hi > 140:   risk_score += 2
            if ap_hi > 160:   risk_score += 1
            if ap_lo > 90:    risk_score += 1
            if chol > 1:      risk_score += 1
            if chol > 2:      risk_score += 1
            if gluc > 1:      risk_score += 1
            if smoke == 1:    risk_score += 1
            if alco == 1:     risk_score += 1
            if active == 0:   risk_score += 1
            if age > 50:      risk_score += 1
            if age > 60:      risk_score += 1

            pred = 1 if risk_score >= 4 else 0
            prob = min(0.95, max(0.05, risk_score / 10))

        return jsonify({'prediction': pred, 'probability': round(prob, 3)})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ── Visualization Data API ─────────────────────────────────────

@app.route('/api/vizdata')
def vizdata():
    dataset = request.args.get('dataset', 'cardio')
    df = cardio_df if dataset == 'cardio' else shanxi_df

    if df is None:
        return jsonify({'error': 'Dataset not loaded', 'total_records': 0}), 404

    result = {'total_records': len(df)}

    try:
        # Determine target column
        target_col = 'cardio' if 'cardio' in df.columns else df.columns[-1]

        # Age distribution (bins)
        age_col = 'age_years' if 'age_years' in df.columns else 'age'
        bins = list(range(30, 75, 5))
        labels = [f'{b}-{b+5}' for b in bins[:-1]]
        df['age_bin'] = pd.cut(df[age_col], bins=bins, labels=labels)
        age_grp = df.groupby(['age_bin', target_col]).size().unstack(fill_value=0)
        result['age_bins'] = [str(l) for l in labels]
        result['age_pos'] = age_grp[1].tolist() if 1 in age_grp else []
        result['age_neg'] = age_grp[0].tolist() if 0 in age_grp else []

        # Gender
        if 'gender' in df.columns:
            g = df.groupby(['gender', target_col]).size().unstack(fill_value=0)
            result['gender_pos'] = [int(g.loc[v, 1]) if v in g.index and 1 in g.columns else 0 for v in [1, 2]]
            result['gender_neg'] = [int(g.loc[v, 0]) if v in g.index and 0 in g.columns else 0 for v in [1, 2]]

        # Cholesterol
        if 'cholesterol' in df.columns:
            c = df.groupby(['cholesterol', target_col]).size().unstack(fill_value=0)
            result['chol_pos'] = [int(c.loc[v, 1]) if v in c.index and 1 in c.columns else 0 for v in [1, 2, 3]]
            result['chol_neg'] = [int(c.loc[v, 0]) if v in c.index and 0 in c.columns else 0 for v in [1, 2, 3]]

        # Smoker
        if 'smoke' in df.columns:
            high_risk = df[df[target_col] == 1]
            smoke_count = high_risk['smoke'].value_counts()
            result['smoke_risk'] = [int(smoke_count.get(1, 0)), int(smoke_count.get(0, 0))]

        # BMI scatter (sample 200)
        if 'height' in df.columns and 'weight' in df.columns and 'ap_hi' in df.columns:
            sample = df[['height', 'weight', 'ap_hi']].dropna().sample(min(200, len(df)))
            sample['bmi'] = sample['weight'] / ((sample['height'] / 100) ** 2)
            result['bmi_sample'] = [{'x': round(r['bmi'], 1), 'y': int(r['ap_hi'])}
                                    for _, r in sample.iterrows()]

        # Active
        if 'active' in df.columns:
            a = df.groupby(['active', target_col]).size().unstack(fill_value=0)
            result['active_pos'] = [int(a.loc[v, 1]) if v in a.index and 1 in a.columns else 0 for v in [1, 0]]
            result['active_neg'] = [int(a.loc[v, 0]) if v in a.index and 0 in a.columns else 0 for v in [1, 0]]

    except Exception as e:
        result['warning'] = str(e)

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)