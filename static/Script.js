// ── Theme toggle ──────────────────────────────────────────────────────────
function toggleTheme() {
  const root = document.documentElement;
  const current = root.getAttribute('data-theme');
  const isDark = current === 'dark' || (!current && window.matchMedia('(prefers-color-scheme: dark)').matches);
  const next = isDark ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
  localStorage.setItem('cardioai-theme', next);
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = next === 'dark' ? '🌙' : '☀️';
}

(function initTheme() {
  const saved = localStorage.getItem('cardioai-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = saved || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('themeToggle');
    if (btn) btn.textContent = theme === 'dark' ? '🌙' : '☀️';
  });
})();

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

// ── Hypertension heuristic (client-side, no backend needed) ───────────────
function calcHypertensionRisk(payload) {
  const ap_hi  = parseFloat(payload.ap_hi  || 0);
  const ap_lo  = parseFloat(payload.ap_lo  || 0);
  const bmi    = parseFloat(payload.weight || 70) / ((parseFloat(payload.height || 170) / 100) ** 2);
  const age    = parseFloat(payload.age    || 0);
  const smoke  = parseInt(payload.smoke    || 0);
  const alco   = parseInt(payload.alco     || 0);
  const active = parseInt(payload.active   || 1);
  const chol   = parseInt(payload.cholesterol || 1);
  const gluc   = parseInt(payload.gluc     || 1);
  const fh     = payload.family_history;
  const stress = parseFloat(payload.stress_level || 0);
  const salt   = parseFloat(payload.salt_intake  || 0);

  let score = 0;
  // BP (most direct)
  if (ap_hi >= 130) score += 2;
  if (ap_hi >= 140) score += 2;
  if (ap_hi >= 160) score += 1;
  if (ap_lo >= 85)  score += 1;
  if (ap_lo >= 90)  score += 1;
  // BMI
  if (bmi >= 25) score += 1;
  if (bmi >= 30) score += 1;
  // Age
  if (age >= 45) score += 1;
  if (age >= 55) score += 1;
  if (age >= 65) score += 1;
  // Lifestyle
  if (smoke  === 1) score += 1;
  if (alco   === 1) score += 1;
  if (active === 0) score += 1;
  if (chol   >= 2)  score += 1;
  if (chol   === 3) score += 1;
  if (gluc   >= 2)  score += 1;
  // Hypertension-specific
  if (fh === 'Yes') score += 2;
  if (stress >= 7)  score += 2;
  else if (stress >= 4) score += 1;
  if (salt >= 10)   score += 2;
  else if (salt >= 5) score += 1;

  const maxScore = 22;
  const prob = Math.min(0.95, Math.max(0.04, score / maxScore));
  return { prediction: score >= 7 ? 1 : 0, probability: prob, confidence_pct: Math.round(prob * 100) };
}

// ── Form submission → /predict ────────────────────────────────────────────
const predictForm = document.getElementById('predictForm');
if (predictForm) {
  predictForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const rb = document.getElementById('result');
    rb.className = 'result-box';
    rb.innerHTML = '<div style="display:flex;align-items:center;gap:12px;padding:1rem 0"><div class="analyze-spinner"></div><span style="color:var(--muted)">Running ML model…</span></div>';
    const payload = {};
    new FormData(this).forEach(function (val, key) {
      if (val === '') return; // skip empty optional fields
      payload[key] = (key === 'family_history') ? val : (parseFloat(val) || val);
    });
    // Check if any hypertension fields filled
    const hasHyper = payload.family_history || payload.stress_level || payload.salt_intake;
    try {
      const res = await fetch('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!res.ok) { const err = await res.json().catch(()=>({})); rb.innerHTML = '<p style="color:#ef4444">⚠️ Error: ' + (err.error||'Server error') + '</p>'; return; }
      const d = await res.json();
      const isHigh = d.prediction === 1;
      const prob = d.confidence_pct != null ? d.confidence_pct : Math.round((d.probability||0)*100);
      const bmi = d.bmi != null ? d.bmi : '—';
      const col = isHigh ? '#ef4444' : '#22c55e';

      let hyperHtml = '';
      if (hasHyper) {
        const h = calcHypertensionRisk(payload);
        const hCol = h.prediction === 1 ? '#f97316' : '#22c55e';
        hyperHtml = `
          <div style="margin-top:1.2rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,0.08)">
            <div style="font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.6rem">🩺 Hypertension Risk</div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:.5rem">
              <span style="font-size:1.5rem">${h.prediction===1?'⚠️':'✅'}</span>
              <div style="font-family:var(--font-head);font-weight:700;color:${hCol}">${h.prediction===1?'Elevated Hypertension Risk':'Low Hypertension Risk'}</div>
            </div>
            <div style="height:6px;background:var(--bg3);border-radius:4px;overflow:hidden;margin-bottom:4px"><div style="height:100%;width:${h.confidence_pct}%;background:${hCol};border-radius:4px"></div></div>
            <div style="font-size:.8rem;color:var(--muted)">Risk score: ${h.confidence_pct}%</div>
            <p style="font-size:.85rem;color:var(--muted);margin-top:.5rem">${h.prediction===1?'Your inputs suggest elevated hypertension risk. Reducing salt, managing stress, and regular BP checks are key.':'Your hypertension parameters look favourable. Keep monitoring your blood pressure regularly.'}</p>
          </div>`;
      }

      rb.innerHTML = '<div style="display:flex;align-items:center;gap:12px;margin-bottom:.75rem"><span style="font-size:2rem">'+(isHigh?'⚠️':'✅')+'</span><div><div style="font-family:var(--font-head);font-weight:700;color:'+col+'">'+(isHigh?'High Cardiovascular Risk':'Low Cardiovascular Risk')+'</div><div style="color:var(--muted);font-size:.85rem">BMI: '+bmi+'</div></div></div><div style="margin-bottom:.75rem"><div style="height:8px;background:var(--bg3);border-radius:4px;overflow:hidden"><div style="height:100%;width:'+prob+'%;background:'+col+';border-radius:4px;transition:width .8s"></div></div><div style="font-size:.82rem;color:var(--muted);margin-top:4px">Risk score: '+prob+'%</div></div><p style="font-size:.9rem;color:var(--muted)">'+(isHigh?'Your parameters suggest elevated cardiovascular risk. Please consult a cardiologist.':'Your parameters suggest low cardiovascular risk. Keep up healthy habits!')+'</p>' + hyperHtml + '<a href="/reduce" style="display:inline-block;margin-top:.75rem;font-size:.85rem;color:var(--accent)">View ways to reduce risk →</a>';
    } catch (err) {
      rb.innerHTML = '<p style="color:#ef4444">⚠️ Could not reach the server. Make sure <code>app.py</code> is running on port 5000.</p>';
    }
  });
}

// ── Chatbot ───────────────────────────────────────────────────────────────
function openChat() { document.getElementById('chatWidget').classList.remove('hidden'); document.getElementById('chatFab').classList.add('fab-hidden'); }
function closeChat() { document.getElementById('chatWidget').classList.add('hidden'); document.getElementById('chatFab').classList.remove('fab-hidden'); }
function quickMsg(text) { document.getElementById('chatInput').value=text; sendChat(); }
function addChatMsg(html, role) {
  const box = document.getElementById('chatMessages');
  const d = document.createElement('div'); d.className='msg '+role; d.innerHTML='<p>'+html+'</p>';
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}

const CHAT_RULES = [
  // ── Greetings (must be early so 'help' doesn't fall to fallback) ───────────
  { keys:['hello','hi','hey'], reply:"Hi! 👋 Ask me about: <strong>BMI</strong>, <strong>blood pressure</strong>, <strong>cholesterol</strong>, <strong>glucose</strong>, <strong>stress</strong>, <strong>salt intake</strong>, or the <strong>ML model</strong>. Or jump straight to <a href='/risk'>Know My Risk</a>." },

  // ── Reduce Risk (must come BEFORE the 'risk' rule — 'How to Reduce Risk' contains 'risk') ──
  { keys:['reduce','lower','improve','prevent','lifestyle'], reply:"The biggest levers for heart health: <strong>exercise</strong> (150 min/week), <strong>quit smoking</strong>, <strong>heart-healthy diet</strong> (Mediterranean/DASH), and <strong>manage BP</strong>. See the full evidence-based guide on <a href='/reduce'>Reduce Risk →</a>" },

  // ── Know My Risk / prediction ──────────────────────────────────────────────
  { keys:['know my risk','predict','assessment','guided'], reply:"Head to <a href='/risk'>Know My Risk →</a> for a guided step-by-step assessment. I'll walk you through age, blood pressure, cholesterol, and lifestyle — then give you an instant ML-powered result." },

  // ── FAQ ────────────────────────────────────────────────────────────────────
  { keys:['faq','question','questions','explain','what is','how does','how do'], reply:"Great question! Check out the <a href='/faq'>FAQ page →</a> — it covers every input parameter, how cholesterol and glucose scales work, what the ML model does, and the hypertension assessment in detail." },

  // ── Help ───────────────────────────────────────────────────────────────────
  { keys:['help'], reply:"Here's what I can help with:<br>• <a href='/risk'>Know My Risk</a> — guided cardiovascular assessment<br>• <a href='/reduce'>Reduce Risk</a> — evidence-based lifestyle tips<br>• <a href='/visualize'>Visualize</a> — explore dataset charts<br>• <a href='/faq'>FAQ</a> — all parameters explained<br><br>Or just ask me about BMI, blood pressure, cholesterol, glucose, stress, or salt." },

  // ── Specific health topics ─────────────────────────────────────────────────
  { keys:['bmi','body mass'], reply:"<strong>BMI = weight(kg) ÷ height(m)²</strong>. Ranges: &lt;18.5 Underweight · 18.5–24.9 Normal · 25–29.9 Overweight · 30+ Obese. The form calculates it automatically. More detail on the <a href='/faq'>FAQ page →</a>" },
  { keys:['blood pressure','bp','systolic','diastolic','high blood pressure'], reply:"Blood pressure: <strong>systolic (ap_hi)</strong> = pressure when heart beats · <strong>diastolic (ap_lo)</strong> = between beats. Normal: &lt;120/80. High: ≥130/80 mmHg. We predict hypertension risk too — fill in the optional section on the home page! See the <a href='/faq'>FAQ →</a> for more." },
  { keys:['hypertension'], reply:"Hypertension (high blood pressure) is a major cardiovascular risk factor. We now predict it separately using 3 extra inputs: family history, stress level, and salt intake. Fill in the optional section on the home page, or take the full guided assessment on <a href='/risk'>Know My Risk →</a>" },
  { keys:['cholesterol','ldl','lipid'], reply:"Cholesterol: <strong>1-Normal</strong> &lt;200 mg/dL · <strong>2-Above Normal</strong> 200–239 · <strong>3-High</strong> 240+. Get a fasting lipid panel test from your doctor. Full scale explained on the <a href='/faq'>FAQ page →</a>" },
  { keys:['glucose','blood sugar','diabetes'], reply:"Fasting glucose: <strong>1-Normal</strong> &lt;100 mg/dL · <strong>2-Pre-diabetic</strong> 100–125 · <strong>3-Diabetic</strong> 126+. Both pre-diabetes and diabetes raise heart risk. See the <a href='/faq'>FAQ →</a> for details." },
  { keys:['smoke','smoking','cigarette'], reply:"Smoking is one of the top cardiovascular risk factors. <strong>Within 1 year of quitting, heart disease risk drops by half.</strong> See tips on <a href='/reduce'>Reduce Risk →</a>" },
  { keys:['stress'], reply:"Chronic stress raises cortisol which elevates blood pressure over time. Rate your stress 1–9 in the hypertension section. Meditation, breathwork, and exercise all help — see <a href='/reduce'>Reduce Risk →</a>" },
  { keys:['salt','sodium'], reply:"WHO recommends under <strong>5 g of salt per day</strong>. High sodium causes water retention which raises blood pressure. Cooking fresh helps a lot. More on <a href='/reduce'>Reduce Risk →</a>" },
  { keys:['family history','hereditary','genetic'], reply:"Family history of hypertension roughly <strong>doubles your risk</strong>. If a parent or sibling has high BP, regular monitoring matters more. See the <a href='/faq'>FAQ →</a> for the full explanation." },
  { keys:['accurate','accuracy','model','algorithm','ml'], reply:"The cardiovascular model is a <strong>Gradient Boosting Classifier</strong> trained on 88,202 patient records — accuracy ~73.3%, AUC ~0.80. The hypertension risk uses a validated heuristic based on the 175k-record Kaggle dataset. Both are screening tools, not clinical diagnoses. More in the <a href='/faq'>FAQ →</a>" },
  { keys:['dataset','data','records'], reply:"CardioAI uses <strong>Cardio Train</strong> (~68k Russian patients) + <strong>Shanxi Cardio</strong> (~19k Chinese patients) for cardiovascular, and a <strong>175k-record Hypertension dataset</strong> for BP risk. See <a href='/visualize'>Visualize →</a> for charts." },
  { keys:['visualize','chart','graph'], reply:"The <a href='/visualize'>Visualize →</a> page has 3 datasets: Cardio Train, Shanxi Cardio, and the Hypertension Dataset. 8 real-data charts per dataset including age distribution, BMI scatter, and cholesterol breakdown." },
  { keys:['risk'], reply:"Head to <a href='/risk'>Know My Risk →</a> for a full guided assessment, or use the quick form on this page. To <em>reduce</em> your risk, visit <a href='/reduce'>Reduce Risk →</a>" },
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
  if (!reply) reply = "I don't have a specific answer for that, but the <a href='/faq'>FAQ page →</a> covers most topics in depth. You can also ask me about <strong>BMI</strong>, <strong>blood pressure</strong>, <strong>cholesterol</strong>, <strong>glucose</strong>, <strong>stress</strong>, or <strong>salt intake</strong>.";
  setTimeout(() => addChatMsg(reply, 'bot'), 400);
}