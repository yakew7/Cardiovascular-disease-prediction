// ── BMI live preview ─────────────────────────────────────────────────────────
const heightEl = document.querySelector('[name="height"]');
const weightEl = document.querySelector('[name="weight"]');
const bmiEl    = document.getElementById('bmiDisplay');

function updateBmi() {
const h = parseFloat(heightEl.value);
const w = parseFloat(weightEl.value);
if (h > 0 && w > 0) {
    const bmi = (w / ((h / 100) ** 2)).toFixed(1);
    const cat = bmi < 18.5 ? '(Underweight)'
            : bmi < 25   ? '(Normal)'
            : bmi < 30   ? '(Overweight)'
            :               '(Obese)';
    bmiEl.textContent = bmi + ' ' + cat;
} else {
    bmiEl.textContent = '—';
}
}

if (heightEl) heightEl.addEventListener('input', updateBmi);
if (weightEl) weightEl.addEventListener('input', updateBmi);

// ── Form submission → backend /predict only ───────────────────────────────────
const predictForm = document.getElementById('predictForm');
if (predictForm) {
predictForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const rb = document.getElementById('result');
    rb.className = 'result-box';
    rb.innerHTML =
    '<div style="display:flex;align-items:center;gap:12px;padding:1rem 0">' +
    '<div class="analyze-spinner"></div>' +
    '<span style="color:var(--muted)">Running ML model…</span></div>';

    const payload = {};
    new FormData(this).forEach(function (val, key) {
    payload[key] = parseFloat(val) || val;
    });

    try {
        const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        rb.innerHTML =
            '<p style="color:#ef4444">⚠️ Error: ' + (err.error || 'Server error') + '</p>';
        return;
    }

    const d      = await res.json();
    const isHigh = d.prediction === 1;
    const prob   = d.confidence_pct != null ? d.confidence_pct : Math.round((d.probability || 0) * 100);
    const bmi    = d.bmi != null ? d.bmi : '—';
    const col    = isHigh ? '#ef4444' : '#22c55e';

    rb.innerHTML =
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:.75rem">' +
        '<span style="font-size:2rem">' + (isHigh ? '⚠️' : '✅') + '</span>' +
        '<div>' +
            '<div style="font-family:var(--font-head);font-weight:700;color:' + col + '">' +
            (isHigh ? 'High Cardiovascular Risk' : 'Low Cardiovascular Risk') +
            '</div>' +
            '<div style="color:var(--muted);font-size:.85rem">BMI: ' + bmi + '</div>' +
        '</div>' +
        '</div>' +
        '<div style="margin-bottom:.75rem">' +
        '<div style="height:8px;background:var(--bg3);border-radius:4px;overflow:hidden">' +
            '<div style="height:100%;width:' + prob + '%;background:' + col + ';border-radius:4px;transition:width .8s"></div>' +
        '</div>' +
        '<div style="font-size:.82rem;color:var(--muted);margin-top:4px">Risk score: ' + prob + '%</div>' +
        '</div>' +
        '<p style="font-size:.9rem;color:var(--muted)">' +
        (isHigh
            ? 'Your parameters suggest elevated cardiovascular risk. Please consult a cardiologist.'
            : 'Your parameters suggest low cardiovascular risk. Keep up healthy habits!') +
        '</p>' +
        '<a href="/reduce" style="display:inline-block;margin-top:.75rem;font-size:.85rem;color:var(--accent)">' +
        'View ways to reduce risk →' +
        '</a>';

    } catch (err) {
        rb.innerHTML =
        '<p style="color:#ef4444">⚠️ Could not reach the server. ' +
        'Make sure <code>app.py</code> is running on port 5000.</p>';
    }
});
}

// ── Chatbot ───────────────────────────────────────────────────────────────────
function openChat() {
    document.getElementById('chatWidget').classList.remove('hidden');
    document.getElementById('chatFab').style.display = 'none';
}

function closeChat() {
    document.getElementById('chatWidget').classList.add('hidden');
    document.getElementById('chatFab').style.display = 'flex';
}

function quickMsg(text) {
    document.getElementById('chatInput').value = text;
    sendChat();
}

function addChatMsg(html, role) {
    const box = document.getElementById('chatMessages');
    const d   = document.createElement('div');
    d.className = 'msg ' + role;
    d.innerHTML = '<p>' + html + '</p>';
    box.appendChild(d);
    box.scrollTop = box.scrollHeight;
}

function sendChat() {
    const input = document.getElementById('chatInput');
    const msg   = input.value.trim();
    if (!msg) return;
    input.value = '';
    addChatMsg(msg, 'user');
    addChatMsg(
    "Please use the form above for a prediction, or visit " +
    "<a href='/risk'>Know My Risk</a> for a guided step-by-step assessment.",
    'bot'
);
}