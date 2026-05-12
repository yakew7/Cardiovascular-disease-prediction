// ── BMI live preview ──────────────────────────────────────────────────────
const heightEl = document.querySelector('[name="height"]');
const weightEl = document.querySelector('[name="weight"]');
const bmiEl    = document.getElementById('bmiDisplay');

function updateBmi() {
  const h = parseFloat(heightEl && heightEl.value);
  const w = parseFloat(weightEl && weightEl.value);
  if (h > 0 && w > 0) {
    const bmi = (w / ((h / 100) ** 2)).toFixed(1);
    const cat = bmi < 18.5 ? '(Underweight)' : bmi < 25 ? '(Normal)' : bmi < 30 ? '(Overweight)' : '(Obese)';
    if (bmiEl) bmiEl.textContent = bmi + ' ' + cat;
  } else {
    if (bmiEl) bmiEl.textContent = '—';
  }
}
if (heightEl) heightEl.addEventListener('input', updateBmi);
if (weightEl) weightEl.addEventListener('input', updateBmi);

// ── Form submission → /predict ────────────────────────────────────────────
const predictForm = document.getElementById('predictForm');
if (predictForm) {
  predictForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const rb = document.getElementById('result');
    rb.className = 'result-box';
    rb.innerHTML = '<div style="display:flex;align-items:center;gap:12px;padding:1rem 0"><div class="analyze-spinner"></div><span style="color:var(--muted)">Running ML model…</span></div>';
    const payload = {};
    new FormData(this).forEach(function (val, key) { payload[key] = parseFloat(val) || val; });
    try {
      const res = await fetch('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!res.ok) { const err = await res.json().catch(()=>({})); rb.innerHTML = '<p style="color:#ef4444">⚠️ Error: ' + (err.error||'Server error') + '</p>'; return; }
      const d = await res.json();
      const isHigh = d.prediction === 1;
      const prob = d.confidence_pct != null ? d.confidence_pct : Math.round((d.probability||0)*100);
      const bmi = d.bmi != null ? d.bmi : '—';
      const col = isHigh ? '#ef4444' : '#22c55e';
      rb.innerHTML = '<div style="display:flex;align-items:center;gap:12px;margin-bottom:.75rem"><span style="font-size:2rem">'+(isHigh?'⚠️':'✅')+'</span><div><div style="font-family:var(--font-head);font-weight:700;color:'+col+'">'+(isHigh?'High Cardiovascular Risk':'Low Cardiovascular Risk')+'</div><div style="color:var(--muted);font-size:.85rem">BMI: '+bmi+'</div></div></div><div style="margin-bottom:.75rem"><div style="height:8px;background:var(--bg3);border-radius:4px;overflow:hidden"><div style="height:100%;width:'+prob+'%;background:'+col+';border-radius:4px;transition:width .8s"></div></div><div style="font-size:.82rem;color:var(--muted);margin-top:4px">Risk score: '+prob+'%</div></div><p style="font-size:.9rem;color:var(--muted)">'+(isHigh?'Your parameters suggest elevated cardiovascular risk. Please consult a cardiologist.':'Your parameters suggest low cardiovascular risk. Keep up healthy habits!')+'</p><a href="/reduce" style="display:inline-block;margin-top:.75rem;font-size:.85rem;color:var(--accent)">View ways to reduce risk →</a>';
    } catch (err) {
      rb.innerHTML = '<p style="color:#ef4444">⚠️ Could not reach the server. Make sure <code>app.py</code> is running on port 5000.</p>';
    }
  });
}

// ── Chatbot ───────────────────────────────────────────────────────────────
function openChat() { document.getElementById('chatWidget').classList.remove('hidden'); document.getElementById('chatFab').style.display='none'; }
function closeChat() { document.getElementById('chatWidget').classList.add('hidden'); document.getElementById('chatFab').style.display='flex'; }
function quickMsg(text) { document.getElementById('chatInput').value=text; sendChat(); }
function addChatMsg(html, role) {
  const box = document.getElementById('chatMessages');
  const d = document.createElement('div'); d.className='msg '+role; d.innerHTML='<p>'+html+'</p>';
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}

const CHAT_RULES = [
  { keys:['know','risk','predict','assessment'], reply:"Head to <a href='/risk'>Know My Risk</a> for a guided step-by-step assessment. I'll ask about your age, blood pressure, cholesterol, and lifestyle — then give you an instant ML-powered result." },
  { keys:['reduce','lower','improve','prevent'], reply:"The biggest levers for heart health: <strong>exercise</strong> (150 min/week), <strong>quit smoking</strong>, <strong>heart-healthy diet</strong> (Mediterranean/DASH), and <strong>manage BP</strong>. See the full guide on <a href='/reduce'>Reduce Risk</a>." },
  { keys:['bmi','body mass'], reply:"<strong>BMI = weight(kg) ÷ height(m)²</strong>. Ranges: &lt;18.5 Underweight · 18.5–24.9 Normal · 25–29.9 Overweight · 30+ Obese. The form calculates it automatically." },
  { keys:['blood pressure','bp','systolic','diastolic','hypertension'], reply:"Blood pressure: <strong>systolic (ap_hi)</strong> = pressure when heart beats · <strong>diastolic (ap_lo)</strong> = pressure between beats. Normal: &lt;120/80. High: ≥130/80 mmHg." },
  { keys:['cholesterol','ldl','lipid'], reply:"Cholesterol: <strong>1-Normal</strong> &lt;200 mg/dL · <strong>2-Above Normal</strong> 200–239 · <strong>3-High</strong> 240+. Get a fasting lipid panel test from your doctor." },
  { keys:['glucose','blood sugar','diabetes'], reply:"Fasting glucose: <strong>1-Normal</strong> &lt;100 mg/dL · <strong>2-Pre-diabetic</strong> 100–125 · <strong>3-Diabetic</strong> 126+. Both pre-diabetes and diabetes raise heart risk significantly." },
  { keys:['smoke','smoking','cigarette'], reply:"Smoking is one of the top cardiovascular risk factors. <strong>Within 1 year of quitting, heart disease risk drops by half.</strong>" },
  { keys:['accurate','accuracy','model','algorithm','ml'], reply:"The model is a <strong>Gradient Boosting Classifier</strong> trained on 88,202 patient records. It achieves ~73.3% accuracy and AUC ~0.80. It's a screening tool — not a clinical diagnosis." },
  { keys:['dataset','data','records'], reply:"CardioAI uses <strong>Cardio Train</strong> (~68k Russian patients) + <strong>Shanxi Cardio</strong> (~19k Chinese patients), cleaned to 88,202 records. See <a href='/visualize'>Visualize</a> for charts." },
  { keys:['visualize','chart','graph'], reply:"The <a href='/visualize'>Visualize</a> page shows 8 real-data charts: age distribution, gender, BMI vs BP scatter, cholesterol, smoking, activity levels, and more." },
  { keys:['hello','hi','hey','help'], reply:"Hi! 👋 Ask me about: <strong>BMI</strong>, <strong>blood pressure</strong>, <strong>cholesterol</strong>, <strong>glucose</strong>, <strong>reducing risk</strong>, or the <strong>ML model</strong>. Or go to <a href='/risk'>Know My Risk</a>." },
];

function sendChat() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  addChatMsg(msg, 'user');
  const lower = msg.toLowerCase();
  let reply = null;
  for (const rule of CHAT_RULES) { if (rule.keys.some(k=>lower.includes(k))) { reply=rule.reply; break; } }
  if (!reply) reply = "I'm not sure about that. Try asking about <strong>BMI</strong>, <strong>blood pressure</strong>, <strong>cholesterol</strong>, or the <strong>ML model</strong>. Or visit <a href='/risk'>Know My Risk</a>.";
  setTimeout(() => addChatMsg(reply, 'bot'), 400);
}
