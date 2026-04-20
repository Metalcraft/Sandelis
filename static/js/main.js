// ════ SANDĖLIO SISTEMA ════
// TANKIS ir STORIAI apibrėžti index.html <script> bloke

let curEtapas = null;
let lkOrders = [];
let lkF = 'all';
let etapai = [];
let dxfOrders = [], dxfDets = [], curOrd = null, curArea = 0, curContour = '';
let stock = [], history = [], lkLC = null, lkLT = 0;
let settings = {defaultPrice: 0, lowAlert: 2, dxfKaina: 1.45};

// ════ AUTH ════
function getToken() {
  const m = document.cookie.match(/stoken=([^;]+)/);
  return m ? m[1] : '';
}
function getRole() { return localStorage.getItem('srole') || ''; }
function getVardas() { return localStorage.getItem('svardas') || ''; }

async function checkAuth() {
  const token = getToken();
  if(!token) { window.location.href='/login'; return; }
  try {
    const r = await fetch('/api/auth/me?token='+token);
    if(!r.ok) { window.location.href='/login'; return; }
    const d = await r.json();
    localStorage.setItem('srole', d.role);
    localStorage.setItem('svardas', d.vardas);
    // Darbuotojas mato tik lakstus
    if(d.role === 'darbuotojas') {
      document.querySelectorAll('.tab').forEach(t => {
        if(!t.id || t.id === 'tab-lk') return;
        t.style.display = 'none';
      });
      SW('lk');
    }
    // Rodyti vartotoja
    const vEl = document.getElementById('vardasEl');
    if(vEl) vEl.textContent = d.vardas;
  } catch(e) { window.location.href='/login'; }
}

async function logout() {
  const token = getToken();
  await fetch('/api/auth/logout', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})});
  document.cookie = 'stoken=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
  localStorage.removeItem('srole');
  localStorage.removeItem('svardas');
  window.location.href='/login';
}

// ════ API ════
async function api(method, url, data) {
  const token = getToken();
  const sep = url.includes('?') ? '&' : '?';
  const fullUrl = method === 'GET' ? url + sep + 'token=' + token : url;
  const r = await fetch(fullUrl, {
    method,
    headers: {'Content-Type': 'application/json'},
    body: data ? JSON.stringify({...( data || {}), token}) : JSON.stringify({token})
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// ════ INIT ════
window.onload = async () => {
  await checkAuth();
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
    if (!e.message.includes('401')) {
      document.getElementById('connDot').className = 'dot err';
      toast('Klaida jungiantis', true);
    }
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
  const now = new Date().toLocaleDateString('lt-LT') + ' ' + new Date().toTimeString().slice(0,5);
  function tableRows(arr) {
    if (!arr.length) return '<tr><td colspan="2" style="color:#aaa">Tuscia</td></tr>';
    return arr.map((o,i) => '<tr style="background:'+(i%2===0?'#fff':'#f9f9f9')+'"><td style="padding:4px 10px;border-bottom:1px solid #eee;font-family:monospace;font-weight:700">' + o.kodas + '</td><td style="padding:4px 10px;color:#1a7f37">' + (o.collectedAt||'').slice(11,16) + '</td></tr>').join('');
  }
  var html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:Arial,sans-serif;margin:0;padding:12mm}h1{font-size:16pt;font-weight:900}h2{font-size:11pt;font-weight:700;margin:6mm 0 2mm;padding:2mm 4mm;border-left:4px solid #1a7f37;color:#1a7f37}table{width:100%;border-collapse:collapse;margin-bottom:4mm}th{background:#1e3a5f;color:white;padding:2mm 4mm;text-align:left;font-size:9pt}td{padding:2mm 4mm;font-size:9pt}.sum{display:flex;gap:8mm;margin:4mm 0;padding:3mm;background:#f5f5f5}.sum-n{font-size:18pt;font-weight:900;font-family:monospace}.sum-l{font-size:8pt;color:#666;text-transform:uppercase}@page{margin:8mm;size:A4}</style></head><body>'
    + '<h1>' + (curEtapas || 'Ataskaita') + '</h1><div style="font-size:9pt;color:#666;margin-bottom:4mm">' + now + '</div>'
    + '<div class="sum"><div><div class="sum-n" style="color:#1a7f37">' + surinkti.length + '</div><div class="sum-l">Surinkta</div></div></div>'
    + '<h2>Surinkti paketai (' + surinkti.length + ')</h2><table><tr><th>Kodas</th><th>Surinkta</th></tr>' + tableRows(surinkti) + '</table>'
    + '</body></html>';
  var blob = new Blob([html], {type: 'text/html'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url; a.download = 'ataskaita_' + (curEtapas||'').replace(/\s/g,'_') + '_' + new Date().toISOString().slice(0,10) + '.html';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ════ SANDĖLIS ════
function showLabel(storis, matmenys) {
  const modal = document.getElementById('labelModal');
  document.getElementById('lblStoris').textContent = storis + 'mm';
  document.getElementById('lblMatmenys').textContent = matmenys + 'mm';
  document.getElementById('lblStoVal').value = storis;
  document.getElementById('lblMatVal').value = matmenys;
  document.getElementById('lblQty').value = 1;
  modal.style.display = 'flex';
}

function printLabels() {
  const storis = document.getElementById('lblStoVal').value;
  const matmenys = document.getElementById('lblMatVal').value;
  const qty = parseInt(document.getElementById('lblQty').value) || 1;
  const barcodeVal = storis + 'mm-' + matmenys;
  let labelsHtml = '';
  for (let i = 0; i < qty; i++) {
    labelsHtml += `
      <div class="lbl">
        <div class="lbl-top">${storis}mm</div>
        <div class="lbl-mid">${matmenys}mm</div>
        <svg class="lbl-bc" id="lbc${i}"></svg>
      </div>`;
  }
  const w = window.open('','_blank');
  if(!w){alert('Leiskite popup langus!');return;}
  w.document.open();
  w.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"><\/script>
  <style>
    body{margin:0;padding:4mm;font-family:Arial,sans-serif}
    .lbl{display:inline-block;width:80mm;border:1px solid #000;padding:3mm;margin:2mm;vertical-align:top;page-break-inside:avoid}
    .lbl-top{font-size:28pt;font-weight:900;text-align:center;letter-spacing:2px}
    .lbl-mid{font-size:14pt;font-weight:700;text-align:center;color:#333;margin:1mm 0}
    .lbl-bot{font-size:11pt;text-align:center;color:#555;margin-bottom:2mm}
    .lbl-bc{display:block;margin:0 auto;width:100%}
    @media print{@page{margin:4mm}}
  </style></head><body>
  ${labelsHtml}
  <script>
    document.querySelectorAll('[id^="lbc"]').forEach(function(el){
      try{JsBarcode(el,'${barcodeVal}',{format:'CODE128',width:2,height:40,displayValue:true,fontSize:10,margin:2});}catch(e){}
    });
    setTimeout(function(){window.print();},500);
  <\/script></body></html>`);
  w.document.close();
  CM('labelModal');
}

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
      + '<button class="btn btn-s btn-sm" onclick="showLabel(\'' + r.storis + '\',\'' + r.matmenys + '\')">&#x1F3F7;</button>'
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
  CM('settModal'); localStorage.setItem('sandSettings',JSON.stringify(settings)); toast('Išsaugota');
}

async function saveSecurity() {
  const newPass = document.getElementById('settNewPass').value;
  const newPin = document.getElementById('settNewPin').value;
  const token = getToken();
  if(newPass) {
    if(newPass.length < 4) { toast('Per trumpas slaptažodis!', true); return; }
    await api('PUT', '/api/auth/slaptazodis', {token, slaptazodis: newPass});
    document.getElementById('settNewPass').value = '';
    toast('Slaptažodis pakeistas!');
  }
  if(newPin) {
    if(newPin.length !== 4 || isNaN(newPin)) { toast('PIN turi būti 4 skaitmenys!', true); return; }
    await api('PUT', '/api/auth/pin', {token, pin: newPin});
    document.getElementById('settNewPin').value = '';
    toast('PIN pakeistas!');
  }
}

function showSett() {
  document.getElementById('settP').value=settings.defaultPrice||'';
  document.getElementById('settL').value=settings.lowAlert||2;
  document.getElementById('settDxf').value=settings.dxfKaina||1.45;
  // Slėpti admin nustatymus darbuotojui
  const adminSett = document.getElementById('adminSett');
  if(adminSett) adminSett.style.display = getRole()==='admin' ? '' : 'none';
  document.getElementById('settModal').style.display='flex';
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

// ════ ETIKETĖS ════
function etkPreview() {
  const storis = document.getElementById('etkStoris').value.trim();
  const matmenys = document.getElementById('etkMatmenys').value.trim();
  const kiekis = parseInt(document.getElementById('etkKiekis').value) || 1;
  if (!storis || !matmenys) { toast('Ivesk stori ir matmenis!', true); return; }
  document.getElementById('etkPrevStoris').textContent = storis + 'mm';
  document.getElementById('etkPrevMatmenys').textContent = matmenys + 'mm';
  document.getElementById('etkKiekisLbl').textContent = kiekis + ' vnt.';
  document.getElementById('etkPrev').style.display = 'block';
  try {
    JsBarcode('#etkBc', storis + 'mm-' + matmenys, {
      format: 'CODE128', width: 2, height: 45,
      displayValue: true, fontSize: 11, margin: 4
    });
  } catch(e) {}
}

function etkPrint() {
  const storis = document.getElementById('etkStoris').value.trim();
  const matmenys = document.getElementById('etkMatmenys').value.trim();
  const kiekis = parseInt(document.getElementById('etkKiekis').value) || 1;
  if (!storis || !matmenys) { toast('Ivesk stori ir matmenis!', true); return; }
  const barcodeVal = storis + 'mm-' + matmenys;
  const logoSrc = 'data:image/png;base64,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L3kriIh/+Zd/ecvN3yuK1jnnnPNHN3xq48bgvDtnvfdpykpagaRHmJk5/Fu/9ds/+tE9zrr3vOc9R1uwCIjwRWCULHIl9DjADa9//etXr17z6KM7f7z9nuuv/+gf/dEfTU5OAsDGjS9zzmmdpRfovTvmmGMnJib4v9PTM9dd99Ef/ehHZ5756s2bX3722WcvkvnG8a3SIQ9jQRylD37wgwBw8ODB66+//o477rj22ms/85nPrFu37td/7deeePyp7373e+ImO2ezLPv4xz++adMmAJienr7mmuvuuOOON77xjX/wB59ct25dbBsxhnHyIjrvCgiRRhsOLTVTyC/WrFnz+7//++eff8G2bfdcc811+/btO+bYlf/X737slaefUpYBW9cKf+c/fOztb/slRDxw4OC111535513XnjhhX/4h59at26dhDRH2bWl2PxrrHEsicrHQHWtW7fu05++4YILLti6det11310//79k5PrP/e5G1/5ylfyB66++uorr7wcAPbs2fubv/nv77jjh294wxs+/ekb1qxZ/aI8FOMpWN55a6333lk7BoLFmmb16tX/6T99/s1vfvOPf/zja6+9dv/+/Zs3b7744ov5AyeeeKJS+unduz/ykX93//33X3zxxTfeeOPq1ateBHka45ROluuVKzrtdvvYVSs5ufaCrNnZ2bvv3vrII48opZTSFPtLojQ4RWmfFjqzSW+t2FoNxbdNSXlDzUuHqQo8EAARvKeiyDdt2rRixcr77vvJb/7mNZ/5zKcnJ9cJrLV799PXXvPRhx/6+9Wr15500iv+6q/+u7WOG24lSFj8xVgZQEmww+AFBaMZzsQTz1MBRJ7GE5poWmte8YqTLr74YhGjUGcQWdHjJlje+6uuuvKyy97L2yVR0vNZjz/xxHe+s2XLli07d+2KrRAxdi0jFfvgUUKhDEKDg77ZA7cJEQikmZsQizE21EtLu6Tcmb/LFThaZ/fcc89v/MZv3HjjH2/YsAERH31050c+8u8effTRdnvi8OzhP/viF42tIo4aCKV+0N0JKUiYikempJmHqsm9CDqflkKlter3u29+y5ve8Y53PIt3OFaCxeWasen081rGmG3btn3rW9/8wR13HTgwtXbt2l9669tOOOF4nQyGAAAd2VE+ls2oiIOzrhLBCqXJCYNK5Ca0CY1yVlXVMcesXLFi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';
  let labelsHtml = '';
  for (let i = 0; i < kiekis; i++) {
    labelsHtml += `<div class="lbl">
      <div class="lbl-header">
        <img src="${logoSrc}" class="lbl-logo">
        <div class="lbl-company">METALCRAFT</div>
      </div>
      <div class="lbl-top">${storis}mm</div>
      <div class="lbl-mid">${matmenys}mm</div>
      <div class="lbl-codes">
        <svg class="lbl-bc" id="lbc${i}"></svg>
        <canvas class="lbl-qr" id="lqr${i}"></canvas>
      </div>
    </div>`;
  }
  const w = window.open('', '_blank');
  if (!w) { alert('Leiskite popup langus!'); return; }
  w.document.open();
  w.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"><\/script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"><\/script>
  <style>
    body{margin:0;padding:4mm;font-family:Arial,sans-serif;background:#fff}
    .lbl{display:inline-block;width:85mm;border:2px solid #222;border-radius:4px;padding:3mm;margin:2mm;vertical-align:top;page-break-inside:avoid;text-align:center;box-sizing:border-box}
    .lbl-header{display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2mm;border-bottom:1px solid #ddd;padding-bottom:2mm}
    .lbl-logo{height:18px;width:auto}
    .lbl-company{font-size:9pt;font-weight:900;letter-spacing:1px;color:#222}
    .lbl-top{font-size:30pt;font-weight:900;letter-spacing:2px;line-height:1;margin:1mm 0}
    .lbl-mid{font-size:13pt;font-weight:700;color:#333;margin:1mm 0 2mm}
    .lbl-codes{display:flex;align-items:center;justify-content:center;gap:4px}
    .lbl-bc{flex:1;max-width:55mm}
    .lbl-qr canvas{width:22mm!important;height:22mm!important}
    @media print{@page{margin:4mm;size:A4}}
  </style></head><body>
  ${labelsHtml}
  <script>
    window.onload = function() {
      document.querySelectorAll('[id^="lbc"]').forEach(function(el) {
        try { JsBarcode(el, '${barcodeVal}', {format:'CODE128',width:1.8,height:40,displayValue:true,fontSize:10,margin:2}); } catch(e) {}
      });
      document.querySelectorAll('[id^="lqr"]').forEach(function(el) {
        try { new QRCode(el, {text:'${barcodeVal}',width:80,height:80,colorDark:'#000',colorLight:'#fff'}); } catch(e) {}
      });
      setTimeout(function(){ window.print(); }, 800);
    };
  <\/script></body></html>`);
  w.document.close();
}
