const SUPABASE_URL = 'https://blowpaeftobvczysekrr.supabase.co';
const SUPABASE_KEY = 'sb_publishable_ZhJf8u6YjuDewlJp1tTfJw_p7eu8NpH';

const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

function el(id) { return document.getElementById(id); }
function setStatus(id, msg, ok = true) { const s = el(id); s.textContent = msg; s.className = 'status ' + (ok ? 'ok' : 'err'); }
function clearChildren(node) { while (node.firstChild) { node.removeChild(node.firstChild); } }
function makeEl(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

// Auth
async function initAuth() {
  const { data: { session } } = await supabase.auth.getSession();
  if (session) {
    showMain(session.user);
  } else {
    showAuth();
  }

  supabase.auth.onAuthStateChange((event, session) => {
    if (event === 'SIGNED_IN' && session) {
      showMain(session.user);
    } else if (event === 'SIGNED_OUT') {
      showAuth();
    }
  });
}

function showAuth() {
  el('auth-section').style.display = 'block';
  el('main-section').style.display = 'none';
}

function showMain(user) {
  el('auth-section').style.display = 'none';
  el('main-section').style.display = 'block';
  el('user-email').textContent = user.email || 'Logged in';
  populateTopics();
  refreshState();
  loadMetrics();
}

async function signIn() {
  const email = el('auth-email').value.trim();
  const password = el('auth-password').value;
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  setStatus('s-auth', error ? error.message : 'Signed in!', !error);
}

async function signUp() {
  const email = el('auth-email').value.trim();
  const password = el('auth-password').value;
  const { data, error } = await supabase.auth.signUp({ email, password });
  setStatus('s-auth', error ? error.message : 'Check your email for confirmation!', !error);
}

async function signOut() {
  await supabase.auth.signOut();
  showAuth();
}

// Data operations (Supabase)
async function loadMetrics() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;

  const { data: topics } = await supabase.from('topics').select('*').eq('user_id', user.id);
  const { data: appState } = await supabase.from('app_state').select('*').eq('user_id', user.id).eq('key', 'current_day').single();

  el('m-topics').textContent = topics ? topics.length : 0;
  el('m-day').textContent = appState ? (appState.value || 1) : 1;
}

async function populateTopics() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;
  const { data: topics } = await supabase.from('topics').select('*').eq('user_id', user.id);
  const sel = el('sel-topic');
  clearChildren(sel);
  sel.appendChild(makeEl('option', '', 'Select topic')).value = '';
  if (topics) {
    topics.forEach(t => {
      const o = makeEl('option', '', t.name);
      o.value = t.name;
      sel.appendChild(o);
    });
  }
}

async function addTopic() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) { setStatus('s-add', 'Not authenticated', false); return; }

  const body = {
    user_id: user.id,
    subject: el('in-subject').value,
    name: el('in-name').value,
    D: parseFloat(el('in-d').value),
    P: parseFloat(el('in-p').value),
    U: parseFloat(el('in-u').value)
  };
  if (!body.name) { setStatus('s-add', 'Name required', false); return; }

  const { data, error } = await supabase.from('topics').insert(body).select();
  setStatus('s-add', error ? error.message : 'Added: ' + (data && data[0] ? data[0].name : ''), !error);
  if (!error) { el('in-name').value = ''; populateTopics(); refreshState(); }
}

async function logSession() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) { setStatus('s-log', 'Not authenticated', false); return; }
  const name = el('sel-topic').value;
  if (!name) { setStatus('s-log', 'Select a topic', false); return; }

  const studied = el('chk-studied').checked;
  const mistake = el('chk-mistake').checked;

  const { data: topics } = await supabase.from('topics').select('*').eq('user_id', user.id).eq('name', name);
  if (!topics || topics.length === 0) { setStatus('s-log', 'Topic not found', false); return; }

  const topic = topics[0];
  const updates = {};
  if (studied) {
    const { data: appState } = await supabase.from('app_state').select('*').eq('user_id', user.id).eq('key', 'current_day').single();
    const currentDay = appState ? (appState.value || 1) : 1;
    updates.last_studied = currentDay;
    updates.s = Math.min(1.0, (topic.s || 0) + 0.03);
  }
  if (mistake) {
    updates.mistakes = (topic.mistakes || 0) + 1;
  }

  const { error } = await supabase.from('topics').update(updates).eq('id', topic.id).eq('user_id', user.id);
  setStatus('s-log', error ? error.message : 'Logged.', !error);
  if (!error) { refreshState(); }
}

async function generatePlan() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) { setStatus('s-plan', 'Not authenticated', false); return; }

  const { data: topics } = await supabase.from('topics').select('*').eq('user_id', user.id);
  const { data: appState } = await supabase.from('app_state').select('*').eq('user_id', user.id).eq('key', 'current_day').single();
  const currentDay = appState ? (appState.value || 1) : 1;

  const out = el('plan-out');
  clearChildren(out);
  if (!topics || topics.length === 0) {
    out.appendChild(makeEl('p', '', 'No topics. Add some first.'));
    return;
  }

  // Enrich and sort
  const enriched = topics.map(t => {
    const D = t.d || 0.5, P = t.p || 0.5, U = t.u || 0.5, S = t.s || 0;
    const score = 0.35 * S + 0.20 * Math.min(P, 0.9) + 0.35 * D + 0.10 * Math.max(U, 0.2);
    const priority = score >= 0.70 ? 'High' : score >= 0.40 ? 'Medium' : 'Low';
    const last = t.last_studied;
    const gap = last ? Math.max(0, currentDay - last) : 999;
    const memory = last ? Math.max(0.1, Math.round(0.85 ** gap * 10000) / 10000) : 0.1;
    const reasons = [];
    if (t.mistakes > 0) reasons.push('recent mistakes');
    if (memory < 0.5) reasons.push('low retention');
    if (score > 0.7) reasons.push('high score');
    if (reasons.length === 0) reasons.push('needs review');
    return { ...t, score, priority, memory, reasons: reasons.slice(0, 2) };
  });

  enriched.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    if (a.memory !== b.memory) return a.memory - b.memory;
    return (b.mistakes || 0) - (a.mistakes || 0);
  });

  let total = 0;
  const TIME_CAP = 180;
  for (let i = 0; i < enriched.length; i++) {
    const t = enriched[i];
    const est = Math.max(15, Math.floor(30 + t.d * 60));
    if (total + est > TIME_CAP && i > 0) break;

    const wrap = makeEl('div', 'plan-item' + (i === 0 ? ' focus' : ''));
    const name = makeEl('div', 'name');
    name.textContent = (i + 1) + '. ' + t.name + ' ';
    const pill = makeEl('span', 'pill ' + t.priority, t.priority);
    name.appendChild(pill);
    wrap.appendChild(name);
    const meta = makeEl('div', 'meta');
    meta.textContent = 'Score ' + t.score.toFixed(4) + ' | Memory ' + t.memory + ' | ' + est + ' min | ' + t.reasons.join(', ');
    wrap.appendChild(meta);
    out.appendChild(wrap);
    total += est;
  }

  const overflow = enriched.length - out.childElementCount;
  const totalEl = makeEl('div', '');
  totalEl.style.cssText = 'margin-top:8px;font-size:13px;color:#94a3b8';
  totalEl.textContent = 'Total: ' + total + ' min' + (overflow > 0 ? ' | Overflow: ' + overflow + ' topics' : '');
  out.appendChild(totalEl);
  setStatus('s-plan', 'Plan generated.');
}

async function advanceDay() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) { setStatus('s-plan', 'Not authenticated', false); return; }

  const { data: appState } = await supabase.from('app_state').select('*').eq('user_id', user.id).eq('key', 'current_day').single();
  const currentDay = appState ? (appState.value || 1) : 1;
  const nextDay = currentDay + 1;

  const { error } = await supabase.from('app_state').upsert({ user_id: user.id, key: 'current_day', value: nextDay });
  setStatus('s-plan', error ? error.message : 'Advanced to day ' + nextDay, !error);
  if (!error) { refreshState(); generatePlan(); }
}

async function refreshState() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) { el('state-pre').textContent = 'Not authenticated'; return; }
  const { data: topics } = await supabase.from('topics').select('*').eq('user_id', user.id);
  el('state-pre').textContent = JSON.stringify(topics || [], null, 2);
}

window.addEventListener('DOMContentLoaded', () => { initAuth(); });