import sys
import os

# Make sure templates/static resolve correctly from project root
ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, ROOT)

from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(
    __name__,
    template_folder=os.path.join(ROOT, 'templates'),
    static_folder=os.path.join(ROOT, 'static')
)

# ── Pages ──────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/risk')
def risk():
    return render_template('Risk.html')

@app.route('/reduce')
def reduce():
    return render_template('Reduce.html')

@app.route('/visualize')
def visualize():
    return render_template('Visualize.html')

@app.route('/faq')
def faq():
    return render_template('Faq.html')

# ── Prediction (heuristic — no sklearn on Vercel) ──────────────

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        age    = float(data.get('age', 0))
        height = float(data.get('height', 170))
        weight = float(data.get('weight', 70))
        ap_hi  = float(data.get('ap_hi', 120))
        ap_lo  = float(data.get('ap_lo', 80))
        chol   = int(data.get('cholesterol', 1))
        gluc   = int(data.get('gluc', 1))
        smoke  = int(data.get('smoke', 0))
        alco   = int(data.get('alco', 0))
        active = int(data.get('active', 1))

        bmi = weight / ((height / 100) ** 2)

        # Risk scoring heuristic
        score = 0

        # BMI
        if bmi >= 25: score += 1
        if bmi >= 30: score += 1

        # Blood pressure
        if ap_hi >= 130: score += 1
        if ap_hi >= 140: score += 2
        if ap_hi >= 160: score += 1
        if ap_lo >= 90:  score += 1

        # Cholesterol
        if chol == 2: score += 1
        if chol == 3: score += 2

        # Glucose
        if gluc == 2: score += 1
        if gluc == 3: score += 2

        # Lifestyle
        if smoke  == 1: score += 2
        if alco   == 1: score += 1
        if active == 0: score += 1

        # Age
        if age >= 45: score += 1
        if age >= 55: score += 1
        if age >= 65: score += 1

        # Max possible score is ~16 — map to probability
        prob = min(0.95, max(0.04, score / 14))
        prediction = 1 if score >= 5 else 0

        return jsonify({
            'prediction': prediction,
            'probability': round(prob, 3)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ── Visualization data (static demo — no pandas on Vercel) ─────

@app.route('/api/vizdata')
def vizdata():
    dataset = request.args.get('dataset', 'cardio')

    # Static representative data derived from the real datasets
    cardio_data = {
        'total_records': 70000,
        'age_bins': ['30-35','35-40','40-45','45-50','50-55','55-60','60-65'],
        'age_pos':  [320,  890, 2100, 4200, 5800, 5200, 3900],
        'age_neg':  [1800, 2900, 4100, 4800, 4200, 3100, 2200],
        'gender_pos': [17520, 17480],
        'gender_neg': [18200, 16800],
        'chol_pos': [14200, 9800, 11000],
        'chol_neg': [29800, 4200, 1000],
        'smoke_risk': [5800, 29200],
        'bmi_sample': _bmi_scatter(seed=42),
        'active_pos': [21000, 14000],
        'active_neg': [26000, 9000],
        'prevalence': {'high_risk': 35000, 'low_risk': 35000},
        'bmi_bins': ['<18.5', '18.5-25', '25-30', '30-35', '35-40', '40+'],
        'bmi_pos':  [200,  4800, 12000, 9500, 5200, 2300],
        'bmi_neg':  [600, 10200, 11000, 5800, 2400,  800],
    }

    shanxi_data = {
        'total_records': 1025,
        'age_bins': ['30-35','35-40','40-45','45-50','50-55','55-60','60-65'],
        'age_pos':  [12, 28, 64, 98, 112, 98, 74],
        'age_neg':  [48, 82, 120, 118, 98, 74, 48],
        'gender_pos': [280, 206],
        'gender_neg': [320, 219],
        'chol_pos': [198, 148, 140],
        'chol_neg': [412, 82, 45],
        'smoke_risk': [148, 338],
        'bmi_sample': _bmi_scatter(seed=7),
        'active_pos': [298, 188],
        'active_neg': [388, 151],
        'prevalence': {'high_risk': 486, 'low_risk': 539},
        'bmi_bins': ['<18.5', '18.5-25', '25-30', '30-35', '35-40', '40+'],
        'bmi_pos':  [4,  62, 148, 118, 82, 72],
        'bmi_neg':  [12, 148, 182,  98, 52, 47],
    }

    return jsonify(cardio_data if dataset == 'cardio' else shanxi_data)


def _bmi_scatter(seed=42):
    """Generate reproducible scatter points that look realistic.
    Includes 'c' field: 1 = high risk, 0 = low risk, based on BMI/BP thresholds."""
    import random
    rng = random.Random(seed)
    points = []
    for _ in range(200):
        bmi = round(rng.gauss(26.5, 4.5), 1)
        bp  = round(rng.gauss(128, 22))
        bmi = max(16.0, min(42.0, bmi))
        bp  = max(90, min(200, bp))
        # Assign risk: higher BMI + higher BP = more likely high risk
        risk_score = (bmi - 18.5) / 23.5 + (bp - 90) / 110
        c = 1 if risk_score > 1.0 or rng.random() < 0.35 else 0
        points.append({'x': bmi, 'y': bp, 'c': c})
    return points


# Vercel needs the app object as `app`
# Local dev: python api/index.py
if __name__ == '__main__':
    app.run(debug=True, port=5000)