import warnings
warnings.filterwarnings("ignore")

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os, joblib

app = Flask(__name__)

BASE = os.path.dirname(__file__)

# ── Load cleaned datasets ────────────────────────────────────────────────────
def load_df(filename):
    path = os.path.join(BASE, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"[CardioAI] Loaded {filename} — {len(df)} rows")
        return df
    print(f"[CardioAI] {filename} not found — run dataset.py first")
    return None

cardio_df  = load_df("cardio_clean.csv")
shanxi_df  = load_df("shanxi_clean.csv")

# ── Load model ───────────────────────────────────────────────────────────────
model = None
try:
    model = joblib.load(os.path.join(BASE, "model.pkl"))
    print("[CardioAI] ML model loaded (GradientBoosting, acc≈73%, AUC≈0.80)")
except Exception as e:
    print(f"[CardioAI] model.pkl not found — run dataset.py first: {e}")

FEATURES = ["age","gender","height","weight","ap_hi","ap_lo",
            "cholesterol","gluc","smoke","alco","active"]

# ── Pages ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():      return render_template('Index.html')

@app.route('/risk')
def risk():       return render_template('Risk.html')

@app.route('/reduce')
def reduce():     return render_template('Reduce.html')

@app.route('/visualize')
def visualize():  return render_template('Visualize.html')

@app.route('/faq')
def faq():        return render_template('Faq.html')

# ── Predict API ──────────────────────────────────────────────────────────────
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
            X = np.array([[age, gender, height, weight, ap_hi, ap_lo,
                           chol, gluc, smoke, alco, active]])
            pred = int(model.predict(X)[0])
            prob = float(model.predict_proba(X)[0][1])
        else:
            # Heuristic fallback
            rs = 0
            if bmi > 25: rs += 1
            if bmi > 30: rs += 1
            if ap_hi > 140: rs += 2
            if ap_hi > 160: rs += 1
            if ap_lo > 90:  rs += 1
            if chol > 1: rs += 1
            if chol > 2: rs += 1
            if gluc > 1: rs += 1
            if smoke:    rs += 1
            if alco:     rs += 1
            if not active: rs += 1
            if age > 50: rs += 1
            if age > 60: rs += 1
            pred = 1 if rs >= 4 else 0
            prob = min(0.95, max(0.05, rs / 10))

        return jsonify({
            'prediction':      pred,
            'probability':     round(prob, 3),
            'confidence_pct':  round(prob * 100),
            'bmi':             round(bmi, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ── Visualization Data API ───────────────────────────────────────────────────
@app.route('/api/vizdata')
def vizdata():
    dataset = request.args.get('dataset', 'cardio')
    df = cardio_df if dataset == 'cardio' else shanxi_df

    if df is None:
        return jsonify({'error': 'Dataset not loaded — run dataset.py first',
                        'total_records': 0}), 404

    result = {'total_records': int(len(df))}
    target_col = 'cardio'

    try:
        # ── Age distribution ────────────────────────────────────────────────
        age_col = 'age'
        bins   = list(range(30, 75, 5))
        labels = [f'{b}-{b+5}' for b in bins[:-1]]
        df = df.copy()
        df['age_bin'] = pd.cut(df[age_col], bins=bins, labels=labels)
        age_grp = df.groupby(['age_bin', target_col], observed=False).size().unstack(fill_value=0)
        result['age_bins'] = [str(l) for l in labels]
        result['age_pos']  = [int(x) for x in (age_grp[1].tolist() if 1 in age_grp else [])]
        result['age_neg']  = [int(x) for x in (age_grp[0].tolist() if 0 in age_grp else [])]

        # ── Gender ──────────────────────────────────────────────────────────
        if 'gender' in df.columns:
            g = df.groupby(['gender', target_col]).size().unstack(fill_value=0)
            result['gender_pos'] = [int(g.loc[v, 1]) if v in g.index and 1 in g.columns else 0 for v in [1, 2]]
            result['gender_neg'] = [int(g.loc[v, 0]) if v in g.index and 0 in g.columns else 0 for v in [1, 2]]

        # ── Cholesterol ─────────────────────────────────────────────────────
        if 'cholesterol' in df.columns:
            c = df.groupby(['cholesterol', target_col]).size().unstack(fill_value=0)
            result['chol_pos'] = [int(c.loc[v, 1]) if v in c.index and 1 in c.columns else 0 for v in [1, 2, 3]]
            result['chol_neg'] = [int(c.loc[v, 0]) if v in c.index and 0 in c.columns else 0 for v in [1, 2, 3]]

        # ── Smoker ──────────────────────────────────────────────────────────
        if 'smoke' in df.columns:
            hr = df[df[target_col] == 1]
            sc = hr['smoke'].value_counts()
            result['smoke_risk'] = [int(sc.get(1, 0)), int(sc.get(0, 0))]

        # ── BMI scatter (200 pts) ────────────────────────────────────────────
        if 'bmi' in df.columns and 'ap_hi' in df.columns:
            sample = df[['bmi', 'ap_hi', target_col]].dropna().sample(
                min(200, len(df)), random_state=42)
            result['bmi_sample'] = [
                {'x': round(float(r['bmi']), 1),
                 'y': int(r['ap_hi']),
                 'c': int(r[target_col])}
                for _, r in sample.iterrows()
            ]

        # ── Physical activity ────────────────────────────────────────────────
        if 'active' in df.columns:
            a = df.groupby(['active', target_col]).size().unstack(fill_value=0)
            result['active_pos'] = [int(a.loc[v, 1]) if v in a.index and 1 in a.columns else 0 for v in [1, 0]]
            result['active_neg'] = [int(a.loc[v, 0]) if v in a.index and 0 in a.columns else 0 for v in [1, 0]]

        # ── BMI distribution (histogram) ─────────────────────────────────────
        if 'bmi' in df.columns:
            bmi_bins  = [10, 18.5, 25, 30, 35, 40, 60]
            bmi_lbls  = ['<18.5','18.5–25','25–30','30–35','35–40','40+']
            df['bmi_bin'] = pd.cut(df['bmi'], bins=bmi_bins, labels=bmi_lbls)
            bmi_grp = df.groupby(['bmi_bin', target_col], observed=False).size().unstack(fill_value=0)
            result['bmi_bins'] = bmi_lbls
            result['bmi_pos']  = [int(x) for x in (bmi_grp[1].tolist() if 1 in bmi_grp else [])]
            result['bmi_neg']  = [int(x) for x in (bmi_grp[0].tolist() if 0 in bmi_grp else [])]

        # ── Overall prevalence ───────────────────────────────────────────────
        vc = df[target_col].value_counts()
        result['prevalence'] = {
            'high_risk': int(vc.get(1, 0)),
            'low_risk':  int(vc.get(0, 0))
        }

    except Exception as e:
        result['warning'] = str(e)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
