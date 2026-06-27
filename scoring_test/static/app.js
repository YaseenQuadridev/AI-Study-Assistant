const API = '';
async function get(url){ const r=await fetch(API+url); return r.json(); }
async function post(url, body){ const r=await fetch(API+url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); return r.json(); }

function el(id){ return document.getElementById(id); }
function setStatus(id, msg, ok=true){ const s=el(id); s.textContent=msg; s.className='status '+(ok?'ok':'err'); }

async function loadMetrics(){
  const m = await get('/metrics');
  if(!m.ok) return;
  const d=m.data;
  el('m-readiness').textContent = d.readiness.label + ' ('+d.readiness.value+')';
  const topics = await get('/topics');
  el('m-topics').textContent = topics.data ? topics.data.length : 0;
  const state = await get('/topics');
  const plan = await get('/plan');
  el('m-day').textContent = plan.ok && plan.data.plan.length ? 'Day' : '—';
}

async function populateTopics(){
  const r = await get('/topics');
  const sel = el('sel-topic'); sel.innerHTML='<option value="">Select topic</option>';
  if(r.ok && r.data){
    r.data.forEach(t=>{ const o=document.createElement('option'); o.value=t.name; o.textContent=t.name; sel.appendChild(o); });
  }
}

async function addTopic(){
  const body = {
    subject: el('in-subject').value,
    name: el('in-name').value,
    D: parseFloat(el('in-d').value),
    P: parseFloat(el('in-p').value),
    U: parseFloat(el('in-u').value)
  };
  const r = await post('/add-topic', body);
  setStatus('s-add', r.ok ? 'Added: '+r.data.name : (r.error||'Failed'), r.ok);
  if(r.ok){ el('in-name').value=''; populateTopics(); refreshState(); }
}

async function logSession(){
  const name = el('sel-topic').value;
  if(!name){ setStatus('s-log','Select a topic',false); return; }
  const r = await post('/log', {topic_name:name, studied_today:el('chk-studied').checked, made_mistake:el('chk-mistake').checked});
  setStatus('s-log', r.ok ? 'Logged.' : (r.error||'Failed'), r.ok);
  if(r.ok){ refreshState(); }
}

async function generatePlan(){
  const r = await get('/plan');
  const out = el('plan-out');
  if(!r.ok){ out.innerHTML='<div class="status err">'+r.error+'</div>'; return; }
  const d = r.data;
  if(!d.plan.length){ out.innerHTML='<p>No plan available yet.</p>'; return; }
  let html = '';
  d.plan.forEach((item, idx)=>{
    const t=item.topic;
    html += '<div class="plan-item '+(idx===0?'focus':'')+'">';
    html += '<div class="name">'+(idx+1)+'. '+t.name+' <span class="pill '+t.priority+'">'+t.priority+'</span></div>';
    html += '<div class="meta">Score '+t.score+' | Memory '+t.memory_strength+' | '+item.estimated_minutes+' min | '+t.reasons.join(', ')+'</div>';
    html += '</div>';
  });
  html += '<div style="margin-top:8px;font-size:13px;color:#94a3b8">Total: '+d.total_minutes+' min'+ (d.overflow_count?' | Overflow: '+d.overflow_count+' topics':'') +'</div>';
  out.innerHTML = html;
  setStatus('s-plan','Plan generated.');
}

async function advanceDay(){
  const r = await post('/advance',{});
  setStatus('s-plan', r.ok ? 'Advanced to day '+r.data.current_day : (r.error||'Failed'), r.ok);
  if(r.ok){ refreshState(); generatePlan(); }
}

async function refreshState(){
  const r = await get('/topics');
  el('state-pre').textContent = JSON.stringify(r.data||[], null, 2);
}

window.addEventListener('DOMContentLoaded', ()=>{ populateTopics(); refreshState(); loadMetrics(); });
