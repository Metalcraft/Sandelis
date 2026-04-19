// ════ SANDĖLIO SISTEMA ════
// TANKIS ir STORIAI apibrėžti index.html <script> bloke

let curEtapas = null;
let lkOrders = [];
let lkF = 'all';
let etapai = [];
let dxfOrders = [], dxfDets = [], curOrd = null, curArea = 0, curContour = '';
let stock = [], history = [], lkLC = null, lkLT = 0;
let settings = {defaultPrice: 0, lowAlert: 2, dxfKaina: 1.45};

// ════ API ════
async function api(method, url, data) {
  const r = await fetch(url, {
    method,
    headers: {'Content-Type': 'application/json'},
    body: data ? JSON.stringify(data) : undefined
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// ════ INIT ════
window.onload = async () => {
  const saved = localStorage.getItem('sandSettings');
  if (saved) try { settings = JSON.parse(saved); } catch(e) {}
  const lt = localStorage.getItem('lastThick');
  if (lt) {
    const s1 = document.getElementById('dThk'); if (s1) s1.value = lt;
    const s2 = document.getElementById('mThk'); if (s2) s2.value = lt;
  }
  await loadAll();
  setPeriod(30);
  setupDrop();
};

document.addEventListener('click', e => {
  const lkView = document.getElementById('view-lk');
  if (lkView && lkView.classList.contains('active') && !e.target.closest('input,button,select,a')) {
    focusScan();
  }
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.querySelectorAll('.mbg').forEach(m => m.style.display = 'none');
});

// ════ NAVIGACIJA ════
function SW(v) {
  document.querySelectorAll('.view').forEach(e => e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e => e.classList.remove('active'));
  document.getElementById('view-' + v).classList.add('active');
  const t = document.getElementById('tab-' + v); if (t) t.classList.add('active');
  if (v === 'lk') focusScan();
  if (v === 'dv') {
    const lt = localStorage.getItem('lastThick');
    if (lt) {
      const s1 = document.getElementById('dThk'); if (s1) s1.value = lt;
      const s2 = document.getElementById('mThk'); if (s2) s2.value = lt;
    }
  }
}
function CM(id) { document.getElementById(id).style.display = 'none'; }
function focusScan() { try { document.getElementById('scanInp').focus(); } catch(e) {} }
function toast(msg, warn=false, cls='') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast ' + (warn ? 'w' : cls) + ' show';
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('show'), 3000);
}

// ════ GARSAS ════
let actx = null;
function ga() { if (!actx) actx = new (window.AudioContext || window.webkitAudioContext)(); return actx; }
function beep(t) {
  try {
    const c = ga(); if (c.state === 'suspended') c.resume();
    const o = c.createOscillator(), g = c.createGain();
    o.connect(g); g.connect(c.destination);
    const n = c.currentTime;
    if (t === 'new') { o.frequency.value = 880; g.gain.setValueAtTime(.3,n); g.gain.exponentialRampToValueAtTime(.001,n+.2); o.start(n); o.stop(n+.2); }
    else if (t === 'col') { o.frequency.setValueAtTime(660,n); o.frequency.setValueAtTime(880,n+.12); g.gain.setValueAtTime(.3,n); g.gain.exponentialRampToValueAtTime(.001,n+.3); o.start(n); o.stop(n+.3); }
    else if (t === 'del') { o.frequency.setValueAtTime(440,n); o.frequency.setValueAtTime(660,n+.1); o.frequency.setValueAtTime(880,n+.2); g.gain.setValueAtTime(.3,n); g.gain.exponentialRampToValueAtTime(.001,n+.4); o.start(n); o.stop(n+.4); }
    else if (t === 'err') { o.type='sawtooth'; o.frequency.value=220; g.gain.setValueAtTime(.3,n); g.gain.exponentialRampToValueAtTime(.001,n+.4); o.start(n); o.stop(n+.4); }
  } catch(e) {}
}

// ════ ETAPAI ════
async function loadEtapai() {
  try {
    const r = await api('GET', '/api/etapai/aktyvus');
    etapai = r.etapai || [];
    rEtapai();
    document.getElementById('connDot').className = 'dot ok';
  } catch(e) {
    document.getElementById('connDot').className = 'dot err';
    toast('Klaida jungiantis', true);
  }
}

function rEtapai() {
  const sel = document.getElementById('etapasSelect');
  if (!sel) return;
  const curVal = sel.value;
  sel.innerHTML = '<option value="">-- Pasirink etapa --</option>';
  etapai.forEach(e => {
    const opt = document.createElement('option');
    opt.value = e.pavadinimas;
    opt.textContent = e.display + ' (' + e.surinkta + '/' + e.total + ')';
    if (e.pavadinimas === curVal) opt.selected = true;
    sel.appendChild(opt);
  });
  // Atnaujinti badge
  const bdg = document.getElementById('lkBdg');
  if (bdg) bdg.textContent = etapai.reduce((s,e) => s + (e.total - e.surinkta), 0) || etapai.reduce((s,e) => s + e.total, 0);
}

function onEtapasChange(val) {
  curEtapas = val || null;
  if (curEtapas) {
    const et = etapai.find(e => e.pavadinimas === curEtapas);
    const display = et ? et.display : curEtapas;
    document.getElementById('aktyvusLabel').textContent = display;
    document.getElementById('sbTitle').textContent = display;
    document.getElementById('scanHint').textContent = 'Skanuok i: ' + display;
    const ab = document.getElementById('archBtn'); if (ab) ab.style.display = 'inline-flex';
    const db = document.getElementById('delEtapBtn'); if (db) db.style.display = 'inline-flex';
    loadCurEtapas();
  } else {
    document.getElementById('aktyvusLabel').textContent = '';
    document.getElementById('sbTitle').textContent = 'Uzsakymai';
    document.getElementById('scanHint').textContent = 'Pasirink etapa virsuje...';
    const ab = document.getElementById('archBtn'); if (ab) ab.style.display = 'none';
    const db = document.getElementById('delEtapBtn'); if (db) db.style.display = 'none';
    lkOrders = []; lkStats(); rlkList();
  }
  focusScan();
}

async function loadCurEtapas() {
  if (!curEtapas) return;
  try {
    const r = await api('GET', '/api/etapai/lakstai/' + encodeURIComponent(curEtapas));
    lkOrders = r.orders || [];
    lkStats(); rlkList();
  } catch(e) {}
}

async function newEtapas() {
  const inp = document.getElementById('newEtapasInp');
  if (!inp) return;
  const name = inp.value.trim();
  if (!name) { toast('Ivesk pavadinima!', true); return; }
  inp.value = '';
  try {
    await api('POST', '/api/etapai/issaugoti', {pavadinimas: name});
    if (!etapai.find(e => e.pavadinimas === name)) {
      etapai.push({pavadinimas: name, display: name, total: 0, surinkta: 0, perduota: 0, laukia: 0});
    }
    rEtapai();
    const sel = document.getElementById('etapasSelect');
    if (sel) { sel.value = name; onEtapasChange(name); }
    toast('Etapas sukurtas: ' + name);
  } catch(e) { toast('Klaida: ' + e.message, true); }
}

async function delEtapas() {
  if (!curEtapas) { toast('Pasirink etapa!', true); return; }
  const et = etapai.find(e => e.pavadinimas === curEtapas);
  const total = et ? et.total : 0;
  const msg = total > 0
    ? 'Etape "' + curEtapas + '" yra ' + total + ' uzsakymu.\nAr tikrai istrinti visa etapa su visais uzsakymais?'
    : 'Istrinti etapa "' + curEtapas + '"?';
  if (!confirm(msg)) return;
  try {
    await api('DELETE', '/api/etapai/' + encodeURIComponent(curEtapas));
    toast('Etapas istrinta!');
    curEtapas = null;
    lkOrders = []; lkStats(); rlkList();
    document.getElementById('aktyvusLabel').textContent = '';
    document.getElementById('sbTitle').textContent = 'Uzsakymai';
    document.getElementById('scanHint').textContent = 'Pasirink etapa virsuje...';
    const ab = document.getElementById('archBtn'); if (ab) ab.style.display = 'none';
    const db = document.getElementById('delEtapBtn'); if (db) db.style.display = 'none';
    const sel = document.getElementById('etapasSelect'); if (sel) sel.value = '';
    await loadEtapai();
  } catch(e) { toast('Klaida trinant etapa: ' + e.message, true); }
}

async function archvuotiCur() {
  if (!curEtapas) { toast('Pasirink etapa!', true); return; }
  if (!confirm('Archyvuoti "' + curEtapas + '"?')) return;
  try {
    const r = await api('POST', '/api/etapai/archyvuoti', {etapas: curEtapas});
    if (r.success) {
      toast('Archyvuota!');
      curEtapas = null;
      lkOrders = []; lkStats(); rlkList();
      document.getElementById('aktyvusLabel').textContent = '';
      document.getElementById('sbTitle').textContent = 'Uzsakymai';
      document.getElementById('scanHint').textContent = 'Pasirink etapa virsuje...';
      const ab = document.getElementById('archBtn'); if (ab) ab.style.display = 'none';
      const sel = document.getElementById('etapasSelect'); if (sel) sel.value = '';
      etapai = etapai.filter(e => e.pavadinimas !== curEtapas);
      await loadEtapai();
    }
  } catch(e) { toast('Klaida', true); }
}

// ════ SKANAVIMAS ════
document.addEventListener('DOMContentLoaded', () => {
  const inp = document.getElementById('scanInp');
  if (!inp) return;
  inp.addEventListener('keydown', async e => {
    if (e.key === 'Enter') {
      const kodas = inp.value.trim();
      if (!kodas) return;
      inp.value = '';
      await handleScan(kodas);
    }
  });
});

async function handleScan(kodas) {
  if (!curEtapas) {
    lkRes('re', 'KLAIDA', kodas, 'Pasirink etapa virsuje!');
    beep('err'); toast('Pasirink etapa!', true); return;
  }
  const now = Date.now();
  if (kodas === lkLC && now - lkLT < 3000) {
    lkRes('rp', 'DUBLIKATAS', kodas, 'Tas pats kodas!');
    beep('err'); lkLC = null; return;
  }
  lkLC = kodas; lkLT = now;

  const local = lkOrders.find(o => o.kodas === kodas);
  if (local) {
    if (local.delivered) { lkRes('ra', 'JAU PERDUOTA', kodas, ''); beep('err'); return; }
    if (local.collected) {
      local.delivered = true; lkStats(); rlkList();
      lkRes('rd', 'PERDUOTA', kodas, '3x');  beep('del');
      api('POST', '/api/lakstai/next_v2', {kodas, etapas: curEtapas}).then(r => {
        if (!r.success) { local.delivered = false; lkStats(); rlkList(); beep('err'); toast('Klaida', true); }
        else { toast('Perduota: ' + kodas, false, 'b'); updateEtapasStats(); }
      });
    } else {
      local.collected = true; lkStats(); rlkList();
      lkRes('rc', 'SURINKTA', kodas, '2x'); beep('col');
      api('POST', '/api/lakstai/next_v2', {kodas, etapas: curEtapas}).then(r => {
        if (!r.success) { local.collected = false; lkStats(); rlkList(); beep('err'); toast('Klaida', true); }
        else { toast('Surinkta: ' + kodas); updateEtapasStats(); }
      });
    }
    return;
  }

  const newOrd = {kodas, registered: nowS(), collected: false, collectedAt: '', delivered: false, deliveredAt: '', etapas: curEtapas};
  lkOrders.push(newOrd); lkStats(); rlkList();
  lkRes('rn', 'NAUJAS', kodas, '1x'); beep('new');
  api('POST', '/api/lakstai/register_v2', {kodas, etapas: curEtapas}).then(r => {
    if (r.success) { toast('Uzregistruota: ' + kodas); updateEtapasStats(); }
    else if (r.alreadyExists) {
      lkOrders = lkOrders.filter(o => o.kodas !== kodas);
      lkOrders.push(r.order); lkStats(); rlkList();
      handleScan(kodas);
    } else {
      lkOrders = lkOrders.filter(o => o.kodas !== kodas);
      lkStats(); rlkList(); beep('err'); toast('Klaida', true);
    }
  });
}

function updateEtapasStats() {
  const et = etapai.find(e => e.pavadinimas === curEtapas);
  if (et) {
    et.total = lkOrders.length;
    et.surinkta = lkOrders.filter(o => o.collected).length;
    et.perduota = lkOrders.filter(o => o.delivered).length;
    rEtapai();
  }
}

function lkRes(cls, t, kodas, s) {
  const b = document.getElementById('lkRes');
  b.className = 'res ' + cls; b.style.display = 'block';
  document.getElementById('lkRt').textContent = t;
  document.getElementById('lkRc').textContent = kodas;
  document.getElementById('lkRs').textContent = s;
}

function lkStats() {
  const t = lkOrders.length, c = lkOrders.filter(o => o.collected).length;
  const d = lkOrders.filter(o => o.delivered).length, p = lkOrders.filter(o => !o.collected).length;
  const pc = t > 0 ? Math.round(c/t*100) : 0;
  document.getElementById('lkT').textContent = t;
  document.getElementById('lkC').textContent = c;
  document.getElementById('lkD').textContent = d;
  document.getElementById('lkP').textContent = p;
  document.getElementById('lkPct').textContent = pc + '%';
  document.getElementById('lkPfc').style.width = pc + '%';
  document.getElementById('lkPfd').style.width = (t > 0 ? Math.round(d/t*100) : 0) + '%';
}

function lkFlt(f, b) {
  lkF = f;
  document.querySelectorAll('.frow .fb').forEach(x => x.classList.remove('active'));
  b.classList.add('active'); rlkList();
}

function sortLk(l) {
  return [...l].sort((a,b) => {
    const na = parseInt((a.kodas.match(/[0-9]+/g)||[0]).join(''))||0;
    const nb = parseInt((b.kodas.match(/[0-9]+/g)||[0]).join(''))||0;
    return na - nb;
  });
}

function rlkList() {
  const el = document.getElementById('lkList');
  const q = (document.getElementById('lkSrch').value || '').toLowerCase();
  let l = sortLk(lkOrders);
  if (lkF === 'p') l = l.filter(o => !o.collected);
  if (lkF === 'c') l = l.filter(o => o.collected && !o.delivered);
  if (lkF === 'd') l = l.filter(o => o.delivered);
  if (q) l = l.filter(o => o.kodas.toLowerCase().includes(q));
  if (!l.length) { el.innerHTML = '<div class="empty-s">' + (lkOrders.length === 0 ? 'Pasirink etapa...' : 'Nerasta') + '</div>'; return; }
  el.innerHTML = l.map(o => {
    const sc = o.delivered ? 'sdd' : o.collected ? 'sc' : '';
    const sl = o.delivered ? 's2' : o.collected ? 's1' : 's0';
    const st = o.delivered ? 'Perduota' : o.collected ? 'Surinkta' : 'Registruota';
    const tm = (o.delivered ? o.deliveredAt : o.collected ? o.collectedAt : o.registered || '').slice(11,16);
    return '<div class="oi ' + sc + '"><div class="od"></div><div class="oc">' + o.kodas + '</div><span class="ost ' + sl + '">' + st + '</span><div class="otm">' + tm + '</div><button class="btn btn-d btn-sm" onclick="lkDel(\'' + o.kodas + '\')">x</button></div>';
  }).join('');
}

async function lkDel(k) {
  if (!confirm('Istrinti "' + k + '"?')) return;
  await api('DELETE', '/api/lakstai/' + k);
  lkOrders = lkOrders.filter(o => o.kodas !== k);
  lkStats(); rlkList(); toast('Istrinta');
}

function genPdfReport() {
  const surinkti = sortLk(lkOrders.filter(o => o.collected && !o.delivered));
  const perduoti = sortLk(lkOrders.filter(o => o.delivered));
  const laukia = sortLk(lkOrders.filter(o => !o.collected));
  const now = new Date().toLocaleDateString('lt-LT') + ' ' + new Date().toTimeString().slice(0,5);
  function tableRows(arr, color) {
    if (!arr.length) return '<tr><td colspan="2" style="color:#aaa">Tuscia</td></tr>';
    return arr.map(o => '<tr><td style="padding:4px 10px;border-bottom:1px solid #eee;font-family:monospace">' + o.kodas + '</td><td style="padding:4px 10px;color:' + color + '">' + (o.delivered ? o.deliveredAt : o.collected ? o.collectedAt : o.registered || '').slice(11,16) + '</td></tr>').join('');
  }
  var html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:Arial,sans-serif;margin:0;padding:12mm}h1{font-size:16pt;font-weight:900}h2{font-size:11pt;font-weight:700;margin:6mm 0 2mm;padding:2mm 4mm;border-left:4px solid #0969da}h2.g{border-left-color:#1a7f37}h2.b{border-left-color:#0969da}h2.y{border-left-color:#9a6700}table{width:100%;border-collapse:collapse;margin-bottom:4mm}th{background:#1e3a5f;color:white;padding:2mm 4mm;text-align:left;font-size:9pt}td{padding:2mm 4mm;font-size:9pt}.sum{display:flex;gap:8mm;margin:4mm 0;padding:3mm;background:#f5f5f5}.sum-n{font-size:18pt;font-weight:900;font-family:monospace}.sum-l{font-size:8pt;color:#666;text-transform:uppercase}@page{margin:8mm;size:A4}</style></head><body>'
    + '<h1>' + (curEtapas || 'Ataskaita') + '</h1><div style="font-size:9pt;color:#666;margin-bottom:4mm">' + now + '</div>'
    + '<div class="sum"><div><div class="sum-n" style="color:#1f2328">' + lkOrders.length + '</div><div class="sum-l">Is viso</div></div><div><div class="sum-n" style="color:#1a7f37">' + surinkti.length + '</div><div class="sum-l">Surinkta</div></div><div><div class="sum-n" style="color:#0969da">' + perduoti.length + '</div><div class="sum-l">Perduota</div></div><div><div class="sum-n" style="color:#9a6700">' + laukia.length + '</div><div class="sum-l">Laukia</div></div></div>'
    + '<h2 class="g">Surinkta (' + surinkti.length + ')</h2><table><tr><th>Kodas</th><th>Laikas</th></tr>' + tableRows(surinkti,'#1a7f37') + '</table>'
    + '<h2 class="b">Perduota (' + perduoti.length + ')</h2><table><tr><th>Kodas</th><th>Laikas</th></tr>' + tableRows(perduoti,'#0969da') + '</table>'
    + '<h2 class="y">Laukia (' + laukia.length + ')</h2><table><tr><th>Kodas</th><th>Laikas</th></tr>' + tableRows(laukia,'#9a6700') + '</table>'
    + '</body></html>';
  var blob = new Blob([html], {type: 'text/html'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url; a.download = 'ataskaita_' + (curEtapas||'').replace(/\s/g,'_') + '_' + new Date().toISOString().slice(0,10) + '.html';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ════ SANDĖLIS ════
async function loadStock() {
  try { const r = await api('GET', '/api/sandelis'); stock = r.stock || []; rStock(); document.getElementById('stkBdg').textContent = stock.length; } catch(e) {}
}
async function loadHist() {
  try { const r = await api('GET', '/api/sandelis/istorija'); history = r.history || []; rHist(); } catch(e) {}
}

function rStock() {
  const el = document.getElementById('stkTbl'), su = document.getElementById('stkSum');
  if (!stock.length) { el.innerHTML = '<div class="empty-s">Sandelis tuscias</div>'; su.innerHTML = ''; return; }
  const totVnt = stock.reduce((s,r) => s+r.likoVnt,0);
  const totKg = stock.reduce((s,r) => s+r.likoKg,0);
  const totT = Math.round(totKg/10)/100;
  const totVal = stock.reduce((s,r) => s+r.verte,0);
  su.innerHTML = '<div class="stk-s"><div class="stk-n">' + totVnt + '</div><div class="stk-l">Viso vnt.</div></div>'
    + '<div class="stk-s"><div class="stk-n">' + totKg.toFixed(1) + '</div><div class="stk-l">Viso kg</div></div>'
    + '<div class="stk-s"><div class="stk-n" style="color:var(--gn)">' + totT + '</div><div class="stk-l">Tonos</div></div>'
    + '<div class="stk-s"><div class="stk-n" style="color:var(--or)">' + totVal.toFixed(2) + '</div><div class="stk-l">Verte EUR</div></div>';
  const sorted = [...stock].sort((a,b) => a.storis - b.storis);
  el.innerHTML = sorted.map(r => {
    const nc = r.likoVnt===0?'empty':r.likoVnt<=settings.lowAlert?'warn':'ok';
    return '<div class="stk-row"><div><div class="stk-thick">' + r.storis + '<span>mm</span></div></div>'
      + '<div><div class="stk-dims">' + r.matmenys + 'mm</div><div class="stk-sub">' + (r.pastabos||'') + '</div></div>'
      + '<div><div class="stk-num ' + nc + '">' + r.likoVnt + '</div><div class="stk-sub">vnt.</div></div>'
      + '<div><div class="stk-num" style="font-size:13px;color:var(--tx2)">' + r.likoKg.toFixed(1) + '</div><div class="stk-sub">kg</div></div>'
      + '<div><div class="stk-num" style="font-size:12px;color:var(--tx2)">' + r.likoT.toFixed(3) + '</div><div class="stk-sub">t</div></div>'
      + '<div><div class="stk-val">' + r.verte.toFixed(2) + 'EUR</div><div class="stk-sub">' + (r.kainaKg>0?r.kainaKg+'EUR/t':'') + '</div></div>'
      + '<div class="stk-acts"><button class="btn btn-y btn-sm" onclick="showUse(\'' + r.id + '\',\'' + r.storis + 'mm ' + r.matmenys + '\',' + r.likoVnt + ')">-</button>'
      + '<button class="btn btn-d btn-sm" onclick="delStk(\'' + r.id + '\')">x</button></div></div>';
  }).join('') + '<div class="stk-tot"><div style="font-family:monospace;font-size:10px;font-weight:700">VISO</div><div></div>'
    + '<div><div class="stk-num" style="font-size:13px;color:var(--ac)">' + totVnt + '</div><div class="stk-sub">vnt.</div></div>'
    + '<div><div class="stk-num" style="font-size:12px;color:var(--tx2)">' + totKg.toFixed(1) + '</div><div class="stk-sub">kg</div></div>'
    + '<div><div class="stk-num" style="font-size:13px;color:var(--gn);font-weight:800">' + totT + '</div><div class="stk-sub">t</div></div>'
    + '<div><div class="stk-val" style="font-size:13px;font-weight:800">' + totVal.toFixed(2) + 'EUR</div></div><div></div></div>';
}

function rHist() {
  const el = document.getElementById('histTbl');
  if (!history.length) { el.innerHTML = '<div class="empty-s">Dar nera istorijos</div>'; return; }
  el.innerHTML = '<table><thead><tr><th>Data</th><th>Veiksmas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris kg</th></tr></thead><tbody>'
    + history.slice(0,50).map(h => '<tr><td class="mono" style="font-size:10px;color:var(--tx3)">' + h.data + '</td>'
      + '<td><span class="hist-act ' + h.veiksmas[0] + '">' + h.veiksmas + '</span></td>'
      + '<td class="mono">' + h.storis + 'mm</td><td class="mono" style="color:var(--tx2)">' + h.matmenys + '</td>'
      + '<td class="mono">' + h.kiekis + 'vnt.</td><td class="num">' + h.svorisIsViso.toFixed(2) + '</td></tr>').join('')
    + '</tbody></table>';
}

function showRecv() {
  if (settings.defaultPrice) document.getElementById('recP').value = settings.defaultPrice;
  document.getElementById('recvModal').style.display = 'flex';
}
function rcRecv() {
  const t=parseFloat(document.getElementById('recThk').value)||0;
  const w=parseFloat(document.getElementById('recW').value)||0;
  const l=parseFloat(document.getElementById('recL').value)||0;
  const q=parseInt(document.getElementById('recQ').value)||1;
  const p=parseFloat(document.getElementById('recP').value)||0;
  if (!w||!l) { document.getElementById('recPrev').textContent='Ivesk matmenis...'; return; }
  const we=Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  const tot=Math.round(we*q*100)/100;
  const totT=Math.round(tot/10)/100;
  const val=p>0?Math.round(totT*p*100)/100:0;
  document.getElementById('recPrev').innerHTML='1 lakstas: <strong style="color:var(--ac)">' + we + 'kg</strong> x ' + q + 'vnt. = <strong style="color:var(--gn)">' + tot + 'kg = ' + totT + 't</strong>' + (val>0?' = <strong style="color:var(--or)">' + val + 'EUR</strong>':'');
}
async function doRecv() {
  const t=document.getElementById('recThk').value, w=document.getElementById('recW').value;
  const l=document.getElementById('recL').value, q=document.getElementById('recQ').value;
  const p=document.getElementById('recP').value, n=document.getElementById('recN').value;
  if (!w||!l) { toast('Ivesk matmenis!',true); return; }
  const r = await api('POST','/api/sandelis/gauti',{storis:t,plotis:w,ilgis:l,kiekis:q,kaina:p,pastabos:n});
  if (r.success) { CM('recvModal'); await loadStock(); await loadHist(); toast('Prideta: '+q+'vnt. x '+t+'mm ('+r.likoT+'t)'); }
}
let curStockId = null;
function showUse(id,label,rem) {
  curStockId=id;
  document.getElementById('useInfo').innerHTML='<strong>'+label+'</strong><br>Liko: <strong style="color:var(--gn)">'+rem+'vnt.</strong>';
  document.getElementById('useQ').value=1; document.getElementById('useNote').value='';
  document.getElementById('useModal').style.display='flex';
}
async function doUse() {
  const q=parseInt(document.getElementById('useQ').value)||1, n=document.getElementById('useNote').value;
  const r=await api('POST','/api/sandelis/'+curStockId+'/naudoti',{kiekis:q,pastabos:n});
  if (r.success) { CM('useModal'); await loadStock(); await loadHist(); toast('Sunaudota: '+q+'vnt.'); }
}
async function delStk(id) {
  if(!confirm('Istrinti?')) return;
  await api('DELETE','/api/sandelis/'+id); await loadStock(); toast('Istrinta');
}
function showSett() {
  document.getElementById('settP').value=settings.defaultPrice||'';
  document.getElementById('settL').value=settings.lowAlert||2;
  document.getElementById('settDxf').value=settings.dxfKaina||1.45;
  document.getElementById('settModal').style.display='flex';
}
function saveSett() {
  settings.defaultPrice=parseFloat(document.getElementById('settP').value)||0;
  settings.lowAlert=parseInt(document.getElementById('settL').value)||2;
  settings.dxfKaina=parseFloat(document.getElementById('settDxf').value)||1.45;
  CM('settModal'); localStorage.setItem('sandSettings',JSON.stringify(settings)); toast('Issaugota');
}

// ════ DXF ════
async function loadDxfOrds() {
  try { const r=await api('GET','/api/uzsakymai'); dxfOrders=r.orders||[]; dxfSum(); rOrds(); document.getElementById('dxfBdg').textContent=dxfOrders.length; } catch(e) {}
}
function dxfSum() {
  const t=dxfOrders.length, n=dxfOrders.filter(o=>o.statusas==='Naujas').length;
  const a=dxfOrders.filter(o=>o.statusas==='Vykdomas').length, d=dxfOrders.filter(o=>o.statusas==='Baigtas').length;
  const w=dxfOrders.reduce((s,o)=>s+o.bendraSvoris,0);
  document.getElementById('dxfSum').innerHTML='<div class="smc"><div class="smn a">'+t+'</div><div class="sml">Is viso</div></div>'
    +'<div class="smc"><div class="smn" style="color:var(--yw)">'+n+'</div><div class="sml">Nauji</div></div>'
    +'<div class="smc"><div class="smn a">'+a+'</div><div class="sml">Vykdomi</div></div>'
    +'<div class="smc"><div class="smn" style="color:var(--gn)">'+d+'</div><div class="sml">Baigti</div></div>'
    +'<div class="smc"><div class="smn a">'+w.toFixed(2)+'</div><div class="sml">Svoris kg</div></div>';
}
let dxfF='all';
function dxfFlt(f,b) { dxfF=f; document.querySelectorAll('.fbar .fb').forEach(x=>x.classList.remove('active')); b.classList.add('active'); rOrds(); }
function rOrds() {
  const el=document.getElementById('ordsGrid'), q=(document.getElementById('dxfSrch').value||'').toLowerCase();
  let l=[...dxfOrders].sort((a,b)=>new Date(b.sukurta)-new Date(a.sukurta));
  if(dxfF!=='all') l=l.filter(o=>o.statusas===dxfF);
  if(q) l=l.filter(o=>o.klientas.toLowerCase().includes(q));
  if(!l.length) { el.innerHTML='<div class="empty-s">'+(dxfOrders.length===0?'Dar nera uzsakymu':'Nerasta')+'</div>'; return; }
  el.innerHTML=l.map(o=>'<div class="ocard" onclick="openOrd(\''+o.id+'\')">'
    +'<div class="oct"><div class="oid">'+o.id+'</div><div style="display:flex;gap:4px"><span class="stb '+o.statusas+'">'+o.statusas+'</span>'
    +'<button class="btn btn-d btn-sm" onclick="event.stopPropagation();quickDelOrd(\''+o.id+'\',\''+o.klientas.replace(/'/g,"\\'")+'\')" >x</button></div></div>'
    +'<div class="ocli">'+o.klientas+'</div><div class="ocdesc">'+(o.aprasymas||'')+'</div>'
    +'<div class="ocm"><div class="ocmi"><span class="v">'+o.bendraSvoris.toFixed(3)+'</span><span class="l"> kg</span></div>'
    +'<div class="ocmi"><span class="v">'+o.detaliuSk+'</span><span class="l"> det.</span></div>'
    +'<div class="ocmi"><span class="l">'+(o.sukurta||'').slice(0,10)+'</span></div></div></div>').join('');
}
async function quickDelOrd(id,klientas) {
  if(!confirm('Istrinti "'+klientas+'"?')) return;
  await api('DELETE','/api/uzsakymai/'+id); dxfOrders=dxfOrders.filter(o=>o.id!==id); dxfSum(); rOrds(); toast('Istrinta');
}
function showNewOrd() { document.getElementById('noModal').style.display='flex'; setTimeout(()=>document.getElementById('noC').focus(),100); }
async function createOrd() {
  const c=document.getElementById('noC').value.trim(); if(!c){toast('Ivesk klienta!',true);return;}
  const r=await api('POST','/api/uzsakymai',{klientas:c,aprasymas:document.getElementById('noD').value.trim(),pastabos:document.getElementById('noN').value.trim()});
  if(r.success){CM('noModal');document.getElementById('noC').value='';document.getElementById('noD').value='';document.getElementById('noN').value='';await loadDxfOrds();toast('Sukurta!');openOrd(r.id);}
}
async function openOrd(id) {
  const o=dxfOrders.find(x=>x.id===id); if(!o) return; curOrd=o;
  document.getElementById('dvId').textContent=o.id;
  document.getElementById('dvCli').textContent=o.klientas;
  document.getElementById('dvDsc').textContent=o.aprasymas||'';
  document.getElementById('dvWt').textContent=o.bendraSvoris.toFixed(3);
  document.getElementById('dvSt').value=o.statusas||'Naujas';
  document.getElementById('dvMeta').textContent=(o.sukurta||'').slice(0,16)+(o.pastabos?' - '+o.pastabos:'');
  SW('dv'); await loadDets();
}
function back2Ords() { SW('dxf'); loadDxfOrds(); curArea=0; curContour=''; document.getElementById('pForm').style.display='none'; document.getElementById('cvW').style.display='none'; document.getElementById('dxfFile').value=''; }
async function chSt() { if(!curOrd) return; await api('PUT','/api/uzsakymai/'+curOrd.id+'/statusas',{statusas:document.getElementById('dvSt').value}); toast('Atnaujinta'); }
async function delOrd() { if(!curOrd) return; if(!confirm('Istrinti "'+curOrd.klientas+'"?')) return; await api('DELETE','/api/uzsakymai/'+curOrd.id); toast('Istrinta'); back2Ords(); }
async function loadDets() {
  if(!curOrd) return;
  const r=await api('GET','/api/uzsakymai/'+curOrd.id+'/detales');
  dxfDets=r.details||[]; rDets();
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
  const _showSum = !curOrd || !(curOrd.klientas||'').toLowerCase().includes('metalika');
  const sumEl=document.getElementById('dvSum'); if(sumEl){sumEl.textContent=_showSum?dxfDets.reduce((s,d)=>s+(d.suma||0),0).toFixed(2)+'€':'';sumEl.style.display=_showSum?'':'none';const sumLbl=sumEl.nextElementSibling;if(sumLbl)sumLbl.style.display=_showSum?'':'';}
}
function rDets() {
  const w=document.getElementById('dtWrap');
  dxfDets.sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  if(!dxfDets.length){w.innerHTML='<div class="empty-s">Dar nera detaliu</div>';return;}
  const showKaina = !curOrd || !(curOrd.klientas||'').toLowerCase().includes('metalika');
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  const tq=dxfDets.reduce((s,d)=>s+d.kiekis,0);
  const ts=dxfDets.reduce((s,d)=>s+(d.suma||0),0);
  const groups={};
  dxfDets.forEach(d=>{
    const t=String(d.storis);
    if(!groups[t])groups[t]={t,dets:[],w:0,q:0,s:0};
    groups[t].dets.push(d);groups[t].w+=d.svoris;groups[t].q+=d.kiekis;groups[t].s+=(d.suma||0);
  });
  let rows=''; let idx=0;
  Object.values(groups).forEach(g=>{
    rows+='<tr style="background:var(--s2);border-top:2px solid var(--bd)">'
      +'<td colspan="2"></td>'
      +'<td colspan="2" style="font-weight:800;font-size:13px;color:var(--ac);font-family:monospace;padding:6px 12px">'+g.t+'mm</td>'
      +'<td style="font-size:11px;color:var(--tx2);font-family:monospace">'+g.dets.length+'det.</td>'
      +'<td style="font-size:11px;color:var(--tx2);font-family:monospace">'+g.q+'vnt.</td>'
      +'<td style="font-size:11px;color:var(--ac);font-weight:700;font-family:monospace">'+g.w.toFixed(3)+'kg</td>'
      +(showKaina?'<td></td><td style="font-size:11px;color:var(--gn);font-weight:700;font-family:monospace">'+g.s.toFixed(2)+'€</td>':'')
      +'<td></td></tr>';
    g.dets.forEach(d=>{
      idx++;
      rows+='<tr>'
        +'<td class="mono" style="color:var(--tx3);font-size:10px">'+idx+'</td>'
        +'<td style="font-weight:600">'+d.pavadinimas+'</td>'
        +'<td><select class="det-inp" onchange="updDet(\''+d.detId+'\',\'storis\',this.value)">'+STORIAI.map(t=>'<option value="'+t+'"'+(d.storis===t?' selected':'')+'>'+t+'mm</option>').join('')+'</select></td>'
        +'<td class="mono" style="font-size:11px;color:var(--tx2)">'+calcDims(d)+'</td>'
        +'<td><input type="number" class="det-inp" value="'+d.kiekis+'" min="1" style="width:50px" onchange="updDet(\''+d.detId+'\',\'kiekis\',this.value)"></td>'
        +'<td><input type="number" class="det-inp num" value="'+d.svoris.toFixed(3)+'" min="0" step="0.001" style="width:70px;color:var(--ac);font-weight:700" id="w-'+d.detId+'" onchange="updDetW(\''+d.detId+'\',this.value)"><span style="font-size:10px;color:var(--tx3)">kg</span></td>'
        +(showKaina
          ?'<td><input type="number" class="det-inp" value="'+(d.kainaKg||1.45).toFixed(2)+'" min="0" step="0.01" style="width:65px;color:var(--gn);font-weight:700" id="k-'+d.detId+'" onchange="updDetK(\''+d.detId+'\',this.value)"></td>'
           +'<td style="font-weight:700;color:var(--gn);font-family:monospace" id="s-'+d.detId+'">'+(d.suma||0).toFixed(2)+'€</td>'
          :'')
        +'<td><button class="btn btn-d btn-sm" onclick="delDet(\''+d.detId+'\')">x</button></td>'
        +'</tr>';
    });
  });
  const th='<table><thead><tr><th>#</th><th>Pavadinimas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris</th>'+(showKaina?'<th>EUR/kg</th><th>Suma EUR</th>':'')+'<th></th></tr></thead><tbody>';
  const tf='</tbody></table><div class="dttot"><span style="color:var(--tx3)">Viso: <strong style="color:var(--tx)">'+tq+'vnt.</strong></span><span>Svoris: <span class="tot">'+tw.toFixed(3)+'kg</span></span>'+(showKaina?'<span>Bendra suma: <span class="tot" style="color:var(--gn)">'+ts.toFixed(2)+'€</span></span>':'')+'</div>';
  w.innerHTML=th+rows+tf;
}
async function updDet(detId,field,value) {
  const d=dxfDets.find(x=>x.detId===detId); if(!d) return;
  if(field==='storis') d.storis=parseFloat(value);
  else if(field==='kiekis') d.kiekis=parseInt(value)||1;
  d.svoris=Math.round(d.plotas*(d.storis/10)*(TANKIS/1000)*d.kiekis/1000*1000)/1000;
  d.suma=Math.round(d.svoris*(d.kainaKg||1.45)*100)/100;
  const wEl=document.getElementById('w-'+detId); if(wEl) wEl.value=d.svoris.toFixed(3);
  const sEl=document.getElementById('s-'+detId); if(sEl) sEl.textContent=d.suma.toFixed(2)+'€';
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,plotas:d.plotas,kaina_kg:d.kainaKg||1.45});
}
async function updDetW(detId,value) {
  const d=dxfDets.find(x=>x.detId===detId); if(!d) return;
  d.svoris=Math.round(parseFloat(value)*1000)/1000;
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,svoris:d.svoris,plotas:d.plotas});
}
async function updDetK(detId,value) {
  const d=dxfDets.find(x=>x.detId===detId); if(!d) return;
  d.kainaKg=Math.round(parseFloat(value)*100)/100||1.45;
  d.suma=Math.round(d.svoris*d.kainaKg*100)/100;
  const sEl=document.getElementById('s-'+detId); if(sEl) sEl.textContent=d.suma.toFixed(2)+'€';
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,kaina_kg:d.kainaKg,plotas:d.plotas});
}
async function delDet(id) { if(!confirm('Istrinti?')) return; await api('DELETE','/api/detales/'+id); dxfDets=dxfDets.filter(d=>d.detId!==id); rDets(); document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3); toast('Istrinta'); }
function handleDxf(e) { if(e.target.files.length) handleMultiDxf(Array.from(e.target.files)); }
function handleFolder(e) {
  if(!e.target.files.length) return;
  const files=Array.from(e.target.files).filter(f=>f.name.toLowerCase().endsWith('.dxf'));
  if(!files.length){toast('Aplanke nerasta .dxf failu!',true);return;}
  const folderName=(files[0].webkitRelativePath||'').split('/')[0]||'';
  const ft=thickFromName(folderName);
  if(ft){document.getElementById('dThk').value=ft;document.getElementById('mThk').value=ft;localStorage.setItem('lastThick',String(ft));toast('Aplankas: '+folderName+' -> '+ft+'mm',false,'b');}
  handleMultiDxf(files);
}
async function handleMultiDxf(files) {
  if(!curOrd){toast('Pirma atidaryк uzsakyma!',true);return;}
  if(files.length===1){procDxf(files[0]);return;}
  const defThick=parseFloat(localStorage.getItem('lastThick')||document.getElementById('dThk').value)||3;
  const defQty=parseInt(document.getElementById('dQty').value)||1;
  let ok=0,fail=0;
  for(const file of files){
    await new Promise(resolve=>{
      const r=new FileReader();
      r.onload=async e2=>{
        try{
          const res=pDxf(e2.target.result);
          if(res.areaCm2<=0){fail++;resolve();return;}
          const at=thickFromName(file.name)||defThick;
          const aq=qtyFromName(file.name)||defQty;
          const ctour=serializeContour(res.entities,res.dimW,res.dimH);
          const resp=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:file.name.replace(/[.]dxf$/i,''),storis:at,plotas:res.areaCm2,kiekis:aq,konturas:ctour});
          if(resp.success)ok++;else fail++;
        }catch(ex){fail++;}
        resolve();
      };
      r.readAsText(file);
    });
  }
  document.getElementById('dxfFile').value='';
  await loadDets();
  toast(fail>0?'Ikelта: '+ok+', nepavyko: '+fail:'Sekmingai ikeltos '+ok+' detales!');
}
function procDxf(file) {
  const r=new FileReader();
  r.onload=e=>{
    try{
      const res=pDxf(e.target.result);
      curArea=res.areaCm2; curContour=serializeContour(res.entities,res.dimW,res.dimH);
      document.getElementById('dName').value=file.name.replace(/[.]dxf$/i,'');
      const at=thickFromName(file.name); const aq=qtyFromName(file.name);
      if(at){document.getElementById('dThk').value=at;localStorage.setItem('lastThick',String(at));}
      if(aq) document.getElementById('dQty').value=aq;
      drawPrev(res.entities);
      document.getElementById('pForm').style.display='block';
      rcW();
    }catch(ex){toast('Klaida: '+ex.message,true);}
  };
  r.readAsText(file);
}
function rcW(){const t=parseFloat(document.getElementById('dThk').value)||3,q=parseInt(document.getElementById('dQty').value)||1,w=curArea*(t/10)*(TANKIS/1000)*q/1000;document.getElementById('wPv').textContent=w.toFixed(3);document.getElementById('wAr').textContent='Plotas: '+curArea.toFixed(2)+'cm2 x '+t+'mm x '+q+'vnt.';}
function rcM(){const t=parseFloat(document.getElementById('mThk').value)||3,a=parseFloat(document.getElementById('mArea').value)||0,q=parseInt(document.getElementById('mQty').value)||1;document.getElementById('mWp').textContent=(a*(t/10)*(TANKIS/1000)*q/1000).toFixed(3)+' kg';}
async function addDet(){
  if(!curOrd) return; if(curArea<=0){toast('Plotas=0',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('dName').value.trim()||'Detale',storis:parseFloat(document.getElementById('dThk').value),plotas:curArea,kiekis:parseInt(document.getElementById('dQty').value)||1,konturas:curContour,kaina_kg:settings.dxfKaina||1.45});
  if(r.success){document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';curArea=0;curContour='';await loadDets();toast('Detale: '+r.svoris.toFixed(3)+'kg');}
}
async function addMDet(){
  if(!curOrd) return; const a=parseFloat(document.getElementById('mArea').value)||0; if(a<=0){toast('Ivesk plota!',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('mName').value.trim()||'Detale',storis:parseFloat(document.getElementById('mThk').value),plotas:a,kiekis:parseInt(document.getElementById('mQty').value)||1,konturas:'',kaina_kg:settings.dxfKaina||1.45});
  if(r.success){document.getElementById('mName').value='';document.getElementById('mArea').value='';document.getElementById('mQty').value='1';document.getElementById('mWp').textContent='0.000 kg';await loadDets();toast('Detale: '+r.svoris.toFixed(3)+'kg');}
}
function setupDrop() {
  const dz=document.getElementById('dropZ');
  if(!dz) return;
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length)handleMultiDxf(Array.from(e.dataTransfer.files));});
}

// ════ ATASKAITA ════
function setPeriod(days) {
  const to=new Date(),from=new Date();
  if(days===0) from.setDate(1); else from.setDate(to.getDate()-days);
  document.getElementById('repFrom').value=from.toISOString().slice(0,10);
  document.getElementById('repTo').value=to.toISOString().slice(0,10);
}
async function genRep() {
  const from=document.getElementById('repFrom').value,to=document.getElementById('repTo').value;
  if(!from||!to){toast('Pasirink laikotarpi!',true);return;}
  const r=await api('GET','/api/ataskaita?nuo='+from+'&iki='+to);
  const el=document.getElementById('repOut'); el.style.display='block';
  el.innerHTML='<div class="card"><div class="rep-s"><div class="rep-st">Laikotarpis: '+from+' - '+to+'</div><div class="rep-sr">'
    +'<div class="rep-sc"><div class="n">'+r.lakstai.gauta+'</div><div class="l">Lakstu gauta</div></div>'
    +'<div class="rep-sc"><div class="n">'+r.lakstai.surinkta+'</div><div class="l">Surinkta</div></div>'
    +'<div class="rep-sc"><div class="n">'+r.lakstai.perduota+'</div><div class="l">Perduota</div></div>'
    +'<div class="rep-sc"><div class="n">'+r.dxf.sk+'</div><div class="l">DXF uzsakymu</div></div>'
    +'<div class="rep-sc"><div class="n">'+r.dxf.svoris.toFixed(1)+'</div><div class="l">DXF svoris kg</div></div></div></div>'
    +'<div class="rep-s"><div class="rep-st">Sandelio judesys</div><div class="rep-sr">'
    +'<div class="rep-sc"><div class="n" style="color:var(--gn)">'+r.sandelis.gautaKg.toFixed(1)+'</div><div class="l">Gauta kg</div></div>'
    +'<div class="rep-sc"><div class="n" style="color:var(--rd)">'+r.sandelis.sunaudotaKg.toFixed(1)+'</div><div class="l">Sunaudota kg</div></div>'
    +'<div class="rep-sc"><div class="n" style="color:var(--or)">'+r.sandelis.gautaVerte.toFixed(2)+'</div><div class="l">Gauta EUR</div></div></div></div></div>';
}

// ════ SPAUSDINIMAS ════
function printOrd() {
  if(!curOrd) return;
  const sorted=[...dxfDets].sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  const groups=new Map();
  sorted.forEach(d=>{if(!groups.has(d.storis))groups.set(d.storis,[]);groups.get(d.storis).push(d);});
  const totW=sorted.reduce((s,d)=>s+d.svoris,0),totQ=sorted.reduce((s,d)=>s+d.kiekis,0);
  const now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  const sumRows=[...groups.entries()].map(([t,dets])=>{const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);return'<tr><td style="font-weight:700;color:#1e3a5f">'+t+'mm</td><td style="text-align:center">'+dets.length+'</td><td style="text-align:center">'+gq+'</td><td style="text-align:right;font-weight:700">'+gw.toFixed(3)+'</td></tr>';}).join('');
  let html='<div class="pph"><div><div class="pptitle">'+curOrd.klientas+'</div><div class="ppid">'+curOrd.id+'</div></div><div style="text-align:right"><div class="ppbc"><svg id="pbc"></svg></div></div></div>'
    +'<div class="ppinfo"><div><div class="ppi-l">Bendras svoris</div><div class="ppi-v">'+totW.toFixed(3)+' kg</div></div><div><div class="ppi-l">Viso detaliu</div><div class="ppi-v">'+totQ+' vnt.</div></div><div><div class="ppi-l">Storiu sk.</div><div class="ppi-v">'+groups.size+'</div></div></div>'
    +'<table class="pptable" style="margin-bottom:4mm"><thead><tr><th>Storis</th><th style="text-align:center">Poz.</th><th style="text-align:center">Vnt.</th><th style="text-align:right">Svoris kg</th></tr></thead><tbody>'+sumRows+'<tr style="background:#f0f0f0;font-weight:700"><td>VISO</td><td style="text-align:center">'+sorted.length+'</td><td style="text-align:center">'+totQ+'</td><td style="text-align:right">'+totW.toFixed(3)+'</td></tr></tbody></table>'
    +'<div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Prieme</div><div class="pss">Data</div></div>'
    +'<div class="ppfoot"><span>Isspausta: '+now+'</span><span>'+curOrd.id+'</span></div>';
  groups.forEach((dets,thick)=>{
    const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);
    const rows=dets.map((d,i)=>'<tr><td>'+(i+1)+'</td><td><strong>'+d.pavadinimas+'</strong></td><td style="text-align:center">'+calcDims(d)+'</td><td style="text-align:center">'+d.kiekis+'</td><td style="text-align:right"><strong>'+d.svoris.toFixed(3)+'</strong></td><td style="text-align:center;vertical-align:middle">'+drawContourSvg(d.konturas,12)+'</td></tr>').join('');
    html+='<div style="page-break-before:always"><div class="pph"><div><div class="pptitle">'+curOrd.klientas+'</div><div class="ppid">'+curOrd.id+'</div></div><div style="text-align:right;font-size:22pt;font-weight:900;color:#1e3a5f;border:3px solid #1e3a5f;padding:2mm 4mm;display:inline-block">'+thick+'mm</div></div>'
      +'<div class="ppinfo"><div><div class="ppi-l">Svoris ('+thick+'mm)</div><div class="ppi-v">'+gw.toFixed(3)+' kg</div></div><div><div class="ppi-l">Kiekis</div><div class="ppi-v">'+gq+'vnt. ('+dets.length+'poz.)</div></div><div><div class="ppi-l">Data</div><div class="ppi-v">'+now+'</div></div></div>'
      +'<table class="pptable"><thead><tr><th>#</th><th>Pavadinimas</th><th style="text-align:center">Matmenys</th><th style="text-align:center">Kiekis</th><th style="text-align:right">Svoris kg</th><th style="text-align:center;width:25mm">Vaizdas</th></tr></thead><tbody>'+rows
      +'<tr style="background:#f0f0f0;font-weight:700"><td colspan="3" style="text-align:right">VISO:</td><td style="text-align:center">'+gq+'vnt.</td><td style="text-align:right">'+gw.toFixed(3)+'kg</td><td></td></tr></tbody></table>'
      +'<div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Prieme</div><div class="pss">Data</div></div>'
      +'<div class="ppfoot"><span>'+thick+'mm x '+dets.length+'poz. x '+gq+'vnt. x '+gw.toFixed(3)+'kg</span><span>'+curOrd.id+'</span></div></div>';
  });
  document.getElementById('printArea').innerHTML=html;
  setTimeout(()=>{try{JsBarcode('#pbc',curOrd.id,{format:'CODE128',width:2,height:45,displayValue:false,margin:0});}catch(e){}},100);
  document.getElementById('printMod').style.display='flex';
}
function dlPdf(){
  const c=document.getElementById('printArea').innerHTML;
  const w=window.open('','_blank');
  if(!w){alert('Leiskite popup langus!');return;}
  w.document.open();
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pptable{width:100%;border-collapse:collapse;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:2mm}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style></head><body>'+c+'</body></html>');
  w.document.close();
  setTimeout(()=>w.print(),600);
}
function nowS(){return new Date().toISOString().replace('T',' ').slice(0,19);}


// ════ ARCHYVAI ════
async function loadStages() {
  try {
    const r = await api('GET', '/api/etapai/archyvai');
    const stages = r.stages || [];
    document.getElementById('archBdg').textContent = stages.length;
    const el = document.getElementById('stageCards');
    if (!stages.length) { el.innerHTML = '<div class="empty-s">Dar nera archivu</div>'; return; }
    el.innerHTML = stages.map(s => '<div class="sc-card" onclick="openArch(\'' + s.name.replace(/\\/g,'\\\\').replace(/'/g,"\\'") + '\')">'
      + '<div class="sc-name">' + s.name.replace('ARCH_','') + '</div>'
      + '<div class="sc-stats">Viso: ' + s.total + ' | Surinkta: ' + s.collected + ' | Perduota: ' + s.delivered + '</div>'
      + '</div>').join('');
  } catch(e) {}
}

async function openArch(name) {
  try {
    const r = await api('GET', '/api/etapai/lakstai/' + encodeURIComponent(name));
    const items = r.orders || [];
    const el = document.getElementById('adList');
    document.getElementById('adTitle').textContent = name.replace('ARCH_','');
    document.getElementById('adBox').style.display = 'block';
    if (!items.length) { el.innerHTML = '<div class="empty-s">Tuscias</div>'; return; }
    const surinkti = items.filter(o => o.collected);
    const laukia = items.filter(o => !o.collected);
    el.innerHTML = '<div style="padding:8px;font-size:12px;color:var(--tx2)">Surinkta: <strong>' + surinkti.length + '</strong> | Laukia: <strong>' + laukia.length + '</strong></div>'
      + items.sort((a,b) => a.kodas.localeCompare(b.kodas)).map(o =>
        '<div class="oi ' + (o.delivered?'sdd':o.collected?'sc':'') + '">'
        + '<div class="oc">' + o.kodas + '</div>'
        + '<span class="ost ' + (o.delivered?'s2':o.collected?'s1':'s0') + '">' + (o.delivered?'Perduota':o.collected?'Surinkta':'Laukia') + '</span>'
        + '</div>').join('');
  } catch(e) {}
}

function closeAd() { document.getElementById('adBox').style.display = 'none'; }

// calcDims, drawContourSvg, drawPrev, serializeContour — apibrėžtos dxf.js

// Papildomos archyvu funkcijos
async function loadAll() {
  await loadEtapai();
  await loadDxfOrds();
  await loadStock();
  await loadHist();
  await loadStages();
}
