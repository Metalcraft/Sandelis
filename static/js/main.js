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
  const fullUrl = method === 'GET'
    ? url + sep + 'token=' + token
    : url;
  const r = await fetch(fullUrl, {
    method,
    headers: {'Content-Type': 'application/json'},
    body: method === 'GET' ? undefined : JSON.stringify({...(data || {}), token})
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
    // Nustatyti šiandienos datą PDF filtrui
    const pdfDateEl = document.getElementById('pdfDate');
    if (pdfDateEl && !pdfDateEl.value) pdfDateEl.value = new Date().toISOString().slice(0,10);
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
  // Datos filtras
  const dateEl = document.getElementById('pdfDate');
  const selDate = dateEl ? dateEl.value : '';

  let surinkti = sortLk(lkOrders.filter(o => o.collected && !o.delivered));

  if (selDate) {
    surinkti = surinkti.filter(o => (o.collectedAt||'').slice(0,10) === selDate);
  }

  const now = new Date().toLocaleDateString('lt-LT') + ' ' + new Date().toTimeString().slice(0,5);
  const dateLabel = selDate
    ? new Date(selDate).toLocaleDateString('lt-LT', {weekday:'long', year:'numeric', month:'long', day:'numeric'})
    : 'Visi surinkti';

  function tableRows(arr) {
    if (!arr.length) return '<tr><td colspan="2" style="color:#aaa">Nėra įrašų</td></tr>';
    return arr.map((o,i) => '<tr style="background:'+(i%2===0?'#fff':'#f9f9f9')+'"><td style="padding:4px 10px;border-bottom:1px solid #eee;font-family:monospace;font-weight:700">' + o.kodas + '</td><td style="padding:4px 10px;color:#1a7f37">' + (o.collectedAt||'').slice(11,16) + '</td></tr>').join('');
  }

  var html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
    + 'body{font-family:Arial,sans-serif;margin:0;padding:12mm}'
    + 'h1{font-size:16pt;font-weight:900;margin-bottom:2mm}'
    + 'h2{font-size:11pt;font-weight:700;margin:6mm 0 2mm;padding:2mm 4mm;border-left:4px solid #1a7f37;color:#1a7f37}'
    + 'table{width:100%;border-collapse:collapse;margin-bottom:4mm}'
    + 'th{background:#1e3a5f;color:white;padding:2mm 4mm;text-align:left;font-size:9pt}'
    + 'td{padding:2mm 4mm;font-size:9pt}'
    + '.meta{font-size:9pt;color:#666;margin-bottom:4mm}'
    + '.sum{display:inline-block;background:#e6f4ea;border:1px solid #1a7f37;border-radius:6px;padding:3mm 6mm;margin-bottom:4mm}'
    + '.sum-n{font-size:20pt;font-weight:900;color:#1a7f37;font-family:monospace}'
    + '.sum-l{font-size:8pt;color:#666;text-transform:uppercase}'
    + '@page{margin:8mm;size:A4}'
    + '</style></head><body>'
    + '<h1>' + (curEtapas || 'Ataskaita') + '</h1>'
    + '<div class="meta">📅 ' + dateLabel + ' &nbsp;|&nbsp; Išspausdinta: ' + now + '</div>'
    + '<div class="sum"><div class="sum-n">' + surinkti.length + '</div><div class="sum-l">Surinktų paketų</div></div>'
    + '<h2>Surinkti paketai</h2>'
    + '<table><thead><tr><th>Kodas</th><th>Surinkimo laikas</th></tr></thead><tbody>' + tableRows(surinkti) + '</tbody></table>'
    + '</body></html>';

  var blob = new Blob([html], {type: 'text/html'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  const fn = 'surinkta_' + (curEtapas||'').replace(/\s/g,'_') + (selDate?'_'+selDate:'') + '.html';
  a.href = url; a.download = fn;
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
  if (r.success) { CM('recvModal'); await loadStock(); await loadHist(); toast(r.merged ? 'Atnaujinta: '+q+'vnt. x '+t+'mm — sujungta su esamu!' : 'Prideta: '+q+'vnt. x '+t+'mm ('+r.likoT+'t)'); }
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
  await loadLik();
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

// ════ PWA ════
let deferredPrompt = null;

window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  deferredPrompt = e;
  const btn = document.getElementById('installBtn');
  if (btn) btn.style.display = 'inline-flex';
});

window.addEventListener('appinstalled', () => {
  deferredPrompt = null;
  const btn = document.getElementById('installBtn');
  if (btn) btn.style.display = 'none';
  toast('Programa įdiegta! 🎉');
});

async function installApp() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  deferredPrompt = null;
  const btn = document.getElementById('installBtn');
  if (btn) btn.style.display = 'none';
}

// Registruoti service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });
}

// ════ LIKUČIAI ════
let likuciai = [], likF = 'visi';

async function loadLik() {
  try {
    const r = await api('GET', '/api/likuciai');
    likuciai = r.likuciai || [];
    rLik();
    rLikSum();
  } catch(e) { toast('Klaida', true); }
}

function rLikSum() {
  const el = document.getElementById('likSum');
  if (!el) return;
  const liko = likuciai.filter(l => !l.sunaudota);
  const totKg = liko.reduce((s,l) => s+l.svoris, 0);
  const totT = Math.round(totKg/10)/100;
  el.innerHTML = '<div class="stk-s"><div class="stk-n">'+liko.length+'</div><div class="stk-l">Liko vnt.</div></div>'
    +'<div class="stk-s"><div class="stk-n">'+totKg.toFixed(1)+'</div><div class="stk-l">Liko kg</div></div>'
    +'<div class="stk-s"><div class="stk-n" style="color:var(--gn)">'+totT+'</div><div class="stk-l">Tonos</div></div>'
    +'<div class="stk-s"><div class="stk-n" style="color:var(--tx2)">'+likuciai.filter(l=>l.sunaudota).length+'</div><div class="stk-l">Sunaudota</div></div>';
}

function likFlt(f, b) {
  likF = f;
  document.querySelectorAll('#view-lik .fb').forEach(x => x.classList.remove('active'));
  if(b) b.classList.add('active');
  rLik();
}

function rLik() {
  const el = document.getElementById('likTbl');
  const q = (document.getElementById('likSrch').value || '').toLowerCase();
  let l = [...likuciai];
  if (likF === 'liko') l = l.filter(x => !x.sunaudota);
  if (likF === 'sunaudota') l = l.filter(x => x.sunaudota);
  if (q) l = l.filter(x => x.barcode.toLowerCase().includes(q) || x.matmenys.toLowerCase().includes(q));
  if (!l.length) { el.innerHTML = '<div class="empty-s">Nerasta</div>'; return; }
  const groups = {};
  l.forEach(x => {
    const k = x.storis+'mm';
    if(!groups[k]) groups[k] = [];
    groups[k].push(x);
  });
  let html = '<table><thead><tr><th>Barkodas</th><th>Storis</th><th>Matmenys</th><th>Svoris</th><th>Būsena</th><th></th></tr></thead><tbody>';
  Object.entries(groups).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0])).forEach(([thick, items]) => {
    const liko = items.filter(x=>!x.sunaudota);
    html += '<tr style="background:var(--s2);border-top:2px solid var(--bd)"><td colspan="3" style="font-weight:800;font-size:13px;color:var(--ac);font-family:monospace;padding:6px 12px">'+thick+'</td><td style="font-size:11px;color:var(--tx2)">'+liko.length+' liko / '+items.length+' viso</td><td colspan="2"></td></tr>';
    items.forEach(x => {
      const sc = x.sunaudota ? 'sdd' : 'sc';
      const st = x.sunaudota ? '<span class="ost s2">Sunaudota</span>' : '<span class="ost s1">Liko</span>';
      html += '<tr class="'+sc+'"><td class="mono" style="font-size:11px">'+x.barcode+'</td>'
        +'<td class="mono">'+x.storis+'mm</td>'
        +'<td class="mono">'+x.matmenys+'mm</td>'
        +'<td class="mono" style="font-size:11px">'+x.svoris.toFixed(2)+'kg</td>'
        +'<td>'+st+'</td>'
        +'<td style="display:flex;gap:4px">'
        +(!x.sunaudota?'<button class="btn btn-y btn-sm" onclick="likSunaudoti(\''+x.barcode+'\')">✓</button>':'')
        +'<button class="btn btn-s btn-sm" onclick="likEtiketė(\''+x.barcode+'\','+x.storis+',\''+x.matmenys+'\')">🏷</button>'
        +'<button class="btn btn-d btn-sm" onclick="likDel(\''+x.barcode+'\')">x</button>'
        +'</td></tr>';
    });
  });
  html += '</tbody></table>';
  el.innerHTML = html;
}

async function likScan() {
  const inp = document.getElementById('likScanInp');
  const barcode = inp.value.trim();
  if (!barcode) return;
  inp.value = '';
  const res = document.getElementById('likScanRes');
  res.style.display = 'block';
  try {
    const r = await api('POST', '/api/likuciai/scan', {barcode});
    if (r.notFound) {
      res.innerHTML = '<div class="res re"><div class="rt">NERASTAS</div><div class="rc">'+barcode+'</div></div>';
      beep('err');
    } else if (r.sunaudota && !r.action) {
      res.innerHTML = '<div class="res ra"><div class="rt">JAU SUNAUDOTAS</div><div class="rc">'+barcode+'</div><div class="rs">'+r.storis+'mm '+r.matmenys+'</div></div>';
      beep('err');
    } else {
      res.innerHTML = '<div class="res rd"><div class="rt">SUNAUDOTA ✓</div><div class="rc">'+barcode+'</div><div class="rs">'+r.storis+'mm '+r.matmenys+' — '+r.svoris.toFixed(2)+'kg</div></div>';
      beep('del');
      toast('Sunaudota: '+r.storis+'mm '+r.matmenys);
      await loadLik();
    }
  } catch(e) { res.innerHTML = '<div class="res re"><div class="rt">KLAIDA</div></div>'; beep('err'); }
}

function showNewLik() {
  document.getElementById('likModal').style.display = 'flex';
  document.getElementById('likPrev').textContent = 'Įvesk matmenis...';
}

function rcLik() {
  const t = parseFloat(document.getElementById('likThk').value)||0;
  const w = parseFloat(document.getElementById('likW').value)||0;
  const l = parseFloat(document.getElementById('likL').value)||0;
  if(!w||!l) { document.getElementById('likPrev').textContent='Įvesk matmenis...'; return; }
  const sv = Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  document.getElementById('likPrev').innerHTML = '<strong>'+t+'mm '+Math.round(w)+'×'+Math.round(l)+'mm</strong> — '+sv+' kg';
}

async function doAddLik() {
  const storis = parseFloat(document.getElementById('likThk').value);
  const plotis = parseFloat(document.getElementById('likW').value)||0;
  const ilgis = parseFloat(document.getElementById('likL').value)||0;
  const note = document.getElementById('likNote').value;
  if(!plotis||!ilgis) { toast('Įvesk matmenis!',true); return; }
  const barcode = 'LIK-'+storis+'mm-'+Math.round(plotis)+'x'+Math.round(ilgis)+'-'+Date.now().toString(36).toUpperCase();
  const r = await api('POST', '/api/likuciai', {storis, plotis, ilgis, barcode, pastabos:note});
  if(r.success) {
    CM('likModal');
    document.getElementById('likW').value='';
    document.getElementById('likL').value='';
    document.getElementById('likNote').value='';
    await loadLik();
    toast('Likutis pridėtas!');
    // Spausdinti etiketę
    likEtiketė(barcode, storis, Math.round(plotis)+'x'+Math.round(ilgis));
  }
}

function likEtiketė(barcode, storis, matmenys) {
  const logo = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAASABIAAD/4QCMRXhpZgAATU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAABACgAwAEAAAAAQAABAAAAAAA/8AAEQgEAAQAAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/bAEMAAwMDAwMDBAMDBAYEBAQGCAYGBgYICggICAgICg0KCgoKCgoNDQ0NDQ0NDQ8PDw8PDxISEhISFBQUFBQUFBQUFP/bAEMBAwMDBQUFCQUFCRUODA4VFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFf/dAAQAQP/aAAwDAQACEQMRAD8A/VKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9D9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/0f1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//S/VKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9P9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/1P1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//V/VKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9b9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/1/1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//Q/VKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9H9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/0v1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK+W/wBob9oS8+Bdz4at7Xwt/wAJO/iQXzY+3fYvJFl5HfyZt27zv9n7tfUlfnJ+3p/yGvhr/wBe+uf+h6fQBX/4b18Tf9El/wDK/D/8i0v/AA3r4i/6JL/5X4f/AJFr4fpu4VfKQfcn/DeniP8A6JL/AOXBD/8AItO/4by8R/8ARJf/AC4If/kWvhum7hVco7n3H/w3p4l/6JKv/hRQ/wDyLR/w3l4n/wCiSr/4UUP/AMi18ObhUu6jlC59vf8ADeniT/ok3/lfh/8AkSkb9vfxF/0SX/yvw/8AyLXw5vpdwqeULn3Cv7evif8A6JKn/hRQ/wDyHT/+G8vE3/RJf/Lgh/8AkWvhvcKl3U+ULn27/wAN6eJP+iSj/wAKCH/5Eo/4b08Sf9ElH/hQQ/8AyJXxFuqLcKXKFz7j/wCG9PEn/RJv/K/D/wDIlL/w3p4j/wCiS/8AlwQ//ItfDe4UbhVcoXPub/hvLxH/ANEl/wDLgh/+Rajb9vfxF/0SX/yvw/8AyLXw7uFG4VPKFz7f/wCG+fE//RJE/wDChh/+RKX/AIb41/8A6JQn/g/j/wDkSviHdTN9PlC59v8A/De3iH/ok/8A5X4//kSvtH4OfEU/Ff4b6L4//s3+yBq6zkWgm8/y/JmeH/WbE3fc/uV+KC9K/XH9kf8A5N58E/8AXG6/9LZ6mRR9J0UUVIBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/0/1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK/OP9vL/kNf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InLNUFjJpooInnndURF3MzfdC1+VH7TX7QsXxLuZvh34Duf+KOtps6jqMLf8hSeJv9TD/wBO0b/ff/ls/wBz5PnaX9pP9pa4+I0tz8PPhteeT4Sy0WpanE2H1P8A5ZyQw/8ATp/ff/lp/uff+c/BPg3xF488R2fgfwPZ/atRuvv/APPta2y/u5Li4b/lnFH/AN9u/wAq/O9WBynlWyfwKkdfT37Hn2f/AIXxYeVt/wCQBqP3f+ultX3V8PP2afhT4G8M2+j3nh3TvE2pA+dd6lq1nDcXFxO33m/eI/lR/wByJPlT/abc7enaD8N/h34Tvf7T8MeEtG0W+KeV9osLC2t5fLP8O+FEbbS5gO+oooqQCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAPmH9sb/k3Xxh/v6V/wCnW1r8pO3/AHzX6t/tj/8AJufi/wD67aV/6dbWvyhrSJLPZP2b/wDk4b4b/wDXxq//AKariv2Yr8Z/2dP+Thvhv/18ar/6ariv2YrMoKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9f9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD50/aw/5N58c/9ekH/pVDX5EV+u/7WH/JvPjn/r0g/wDSqGvyGXpWiEzovCC/8XB8Af8AY16N/wClaV+8Vfg94V/5KD4A/wCxq0b/ANK0r94amQwoooqQCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigArifGvg3w58QvDV/wCE/FNmmoaXfoVljb7w/uyK38Lr95GrtqKAPxI+Mvwa134K+IUsb5zqfhnUzjStVIxu/wCne4/gS4RP+ASp8y/xoj/gt8add+CevS3EEU2oeEdQmU6tpI+9G33fttl/BHLGn30+5Knyt/A6fsB4v8G+HPiB4ev/AAp4ssl1DS9QTy5onH/fDK38LofmVl+6a/Hf4v8Awg8R/BbxF/Y+qf6boeobv7K1X/nuv/PGb+7Ov8f9/wC8v+xYH7G+FfE+g+LtB03xL4c1OLU9M1OETW9xByJF9x95WX7rK2GVvlb5q4L4zfB/w18Z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UUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/0P1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAPm79rj/k3Xx3/16W//AKVxV+OP/COaL/z5r/31J/8AF1+xv7XP/Juvjn/r3t//AErhr8kq0QGn8PNI06w+J3gD7PZon/FT6QibPM/iu0r97K/B/wAF/wDJSfh1/wBjbov/AKVpX7wVMgCiiipAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAPmf9sFd/wCzr4zH/YO/9ONtX5K1+tv7Xv8Aybx4y/7h3/pxt6/JJa0iB7V+zZ/ycL8Ov+vjVv8A01XFfsxX4y/s4/8AJw3w6/6+NT/9NVxX7NVnUAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//R/VKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA+bf2u/+TdfHP/Xvb/8ApXDX5KJX63/tbf8AJu3jr/r3t/8A0rhr8ka0iSzc8GJ/xcr4e/8AY1aN/wClaV+8Ffg/4OT/AIuL8Pf+xq0b/wBL4a/eCpkUFFFFSAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAfMn7YP/JunjP/ALh3/pxt6/Juv1o/a+/5N48Yf72mf+nK2r8mq0RLR7F+zf8A8nD/AA6/6+NV/wDTVc1+zVfjP+zj/wAnDfDr/r41P/01XFfsxWZQUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/0v1SooooAKKKKACiiigAoooo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vqv6FqKOYD+er+3tF/6CVt/31Sf23ov/AEErf/vqv6FqKOYD+en+29F/6CVv/wB9U3+3NF/6CVn/AN91/QxRRzAfz0f25ov/AEErf/vuk/tzRf8AoJWf/fdf0MUUcwH89H9uaL/0Erf/AL7o/tzRf+glb/8Afdf0L0UcwH89P9uaL/0ErP8A76o/tzQf+glZ/wDfVf0LUUcwH89H9uaB/wBBG3/76pf7c0X/AKCVn/31X9C1FHMB/PT/AG3ov/QSt/8Avqm/2zoP/QSt/wDvqv6GKKOYD+en+3NB/wCgnb/99U3+3NF/6CVn/wB91/QxRRzAfz0f25oH/QRt/wDvql/tvRf+glb/APfVf0LUUcwH89P9t6L/ANBK3/76o/tzRf8AoJWf/fVf0LUUcwH88/8Abmg/9BKz/wC+6X+3NF/6CVv/AN91/QvRRzAfz0/23ov/AEErf/vqj+3NF/6CVn/31X9C1FHMB/PT/bmg/wDQTt/++qP7c0H/AKCdv/31X9C1FHMB/PT/AG5oP/QTt/8Avqj+29F/6CVv/wB9V/QtRRzAfz0/23ov/QSt/wDvqj+3NF/6CVn/AN9V/QtRRzAfz1f29oP/AEErf/vuj+3tB/6CVv8A991/QrRRzAfz0/23ov8A0Erf/vql/t7Qf+glb/8Afdf0K0UcwH89X9vaD/0Erf8A77pP7e0H/oJWf/fVf0LUUcwH89X9vaD/ANBK3/77o/t7Qf8AoJW//fdf0K0UcwH89P8Abei/9BK3/wC+qP7c0H/oJ2//AH1X9C1FHMB/PV/b2g/9BK3/AO+6P7e0H/oJW/8A33X9CtFHMB/PT/bei/8AQSt/++qP7b0X/oJW/wD31X9C1FHMB+LP7NF9p95+0T8PfsV5Ddf6Rqu/Z/2Criv2mooqQCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA/9T9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/1f1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//W/VKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9f9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/0P1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//R/VKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9L9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/0/1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//U/VKiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9X9UqKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/1v1SooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//Z';
  const w = window.open('','_blank');
  if(!w){alert('Leiskite popup langus!');return;}
  w.document.open();
  w.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jsbarcode/3.11.6/JsBarcode.all.min.js"><\/script>
  <style>
    body{margin:0;padding:4mm;font-family:Arial,sans-serif}
    .lbl{display:inline-block;width:80mm;border:1px solid #000;padding:3mm;text-align:center;page-break-inside:avoid}
    .lbl-logo{width:50px;display:block;margin:0 auto 3mm}
    .lbl-top{font-size:26pt;font-weight:900;letter-spacing:2px}
    .lbl-mid{font-size:13pt;font-weight:700;color:#333;margin:2mm 0}
    .lbl-bc{display:block;margin:0 auto;width:100%}
    @media print{@page{margin:4mm}}
  </style></head><body>
  <div class="lbl">
    <img src="${logo}" class="lbl-logo">
    <div class="lbl-top">${storis}mm</div>
    <div class="lbl-mid">${matmenys}mm</div>
    <svg class="lbl-bc" id="lbc"></svg>
  </div>
  <script>
    window.onload=function(){
      try{JsBarcode('#lbc','${barcode}',{format:'CODE128',width:2,height:45,displayValue:true,fontSize:10,margin:3});}catch(e){}
      setTimeout(function(){window.print();},500);
    };
  <\/script></body></html>`);
  w.document.close();
}

async function likSunaudoti(barcode) {
  if(!confirm('Pažymėti kaip sunaudotą?')) return;
  const r = await api('POST', '/api/likuciai/scan', {barcode});
  if(r.success) { toast('Sunaudota: '+r.matmenys); await loadLik(); }
}

async function likDel(barcode) {
  if(!confirm('Ištrinti?')) return;
  await api('DELETE', '/api/likuciai/'+barcode);
  likuciai = likuciai.filter(l=>l.barcode!==barcode);
  rLik(); rLikSum(); toast('Ištrinta');
}
