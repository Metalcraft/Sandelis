// SANDĖLIO SISTEMA – main.js

let lkOrders=[],lkF='all',lkLC=null,lkLT=0;
let dxfOrders=[],dxfF='all',dxfDets=[],curOrd=null,curArea=0,curContour='';
let stock=[],history=[],stages=[],archOpen=null;
let pendingSt='',curStockId=null;
let settings={defaultPrice:0,lowAlert:2};

// GARSAS
let actx=null;
function ga(){if(!actx)actx=new(window.AudioContext||window.webkitAudioContext)();return actx;}
function beep(t){try{const c=ga();if(c.state==='suspended')c.resume();const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);const n=c.currentTime;if(t==='new'){o.frequency.value=880;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.2);o.start(n);o.stop(n+.2);}else if(t==='col'){o.frequency.setValueAtTime(660,n);o.frequency.setValueAtTime(880,n+.12);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.3);o.start(n);o.stop(n+.3);}else if(t==='del'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(660,n+.1);o.frequency.setValueAtTime(880,n+.2);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='err'){o.type='sawtooth';o.frequency.value=220;g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.4);o.start(n);o.stop(n+.4);}else if(t==='dup'){o.frequency.setValueAtTime(440,n);o.frequency.setValueAtTime(220,n+.15);g.gain.setValueAtTime(.3,n);g.gain.exponentialRampToValueAtTime(.001,n+.35);o.start(n);o.stop(n+.35);}}catch(e){}}

// API
async function api(method,url,data){
  const opts={method,headers:{'Content-Type':'application/json'}};
  if(data)opts.body=JSON.stringify(data);
  const r=await fetch(url,opts);
  if(!r.ok)throw new Error(r.statusText);
  return r.json();
}

// INIT
window.onload=()=>{
  loadAll();
  const lt=localStorage.getItem('lastThick');
  if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}
  setPeriod(30);
  const dz=document.getElementById('dropZ');
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length)handleMultiDxf(Array.from(e.dataTransfer.files));});
};
document.addEventListener('click',e=>{if(actx&&actx.state==='suspended')actx.resume();if(document.getElementById('view-lk').classList.contains('active')&&!e.target.closest('input,button,select'))focusScan();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.mbg').forEach(m=>m.style.display='none');});

async function loadAll(){await loadLk();await loadDxfOrds();await loadStock();await loadHist();await loadStages();}

// NAVIGACIJA
function SW(v){
  document.querySelectorAll('.view').forEach(e=>e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
  document.getElementById('view-'+v).classList.add('active');
  const t=document.getElementById('tab-'+v);if(t)t.classList.add('active');
  if(v==='lk')focusScan();
  if(v==='dv'){const lt=localStorage.getItem('lastThick');if(lt){const s=document.getElementById('dThk');if(s)s.value=lt;const s2=document.getElementById('mThk');if(s2)s2.value=lt;}}
}
function CM(id){document.getElementById(id).style.display='none';}
function focusScan(){try{document.getElementById('scanInp').focus();}catch(e){}}
function toast(msg,w=false,t=''){const el=document.getElementById('toast');el.textContent=msg;el.className='toast '+(w?'w':t)+' show';clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('show'),3000);}

// ════ LAKŠTAI ════
const scanInp=document.getElementById('scanInp');
scanInp.addEventListener('keydown',async e=>{if(e.key==='Enter'){const c=scanInp.value.trim();if(c){scanInp.value='';await handleScan(c);}}});

async function handleScan(kodas){
  const now=Date.now();
  if(kodas===lkLC&&now-lkLT<3000){lkRes('rp','DUBLIKATAS',kodas,'Tas pats kodas du kartus!');beep('dup');toast('Dublikatas: '+kodas,false,'p');lkLC=null;return;}
  lkLC=kodas;lkLT=now;
  const local=lkOrders.find(o=>o.kodas===kodas);
  if(local){
    if(local.delivered){lkRes('ra','JAU PERDUOTA',kodas,'Perduota: '+local.deliveredAt);beep('err');return;}
    if(local.collected){
      lkRes('rd','PERDUOTA',kodas,'3× — siunčiama...');beep('del');
      local.delivered=true;local.deliveredAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Perduota: '+kodas,false,'b');else{local.delivered=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }else{
      lkRes('rc','SURINKTA',kodas,'2× — siunčiama...');beep('col');
      local.collected=true;local.collectedAt=nowS();lkStats();rlkList();
      api('POST','/api/lakstai/next',{kodas}).then(r=>{if(r.success)toast('Surinkta: '+kodas);else{local.collected=false;lkRes('re','KLAIDA',kodas,r.message||'Nepavyko');beep('err');lkStats();rlkList();}});
    }
    return;
  }
  lkRes('rn','NAUJAS',kodas,'1× — siunčiama...');beep('new');
  const newOrd={kodas,registered:nowS(),collected:false,collectedAt:'',delivered:false,deliveredAt:''};
  lkOrders.push(newOrd);lkStats();rlkList();
  api('POST','/api/lakstai/register',{kodas}).then(r=>{
    if(r.success)toast('Užregistruota: '+kodas);
    else if(r.alreadyExists){lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkAddL(r.order);lkStats();rlkList();handleScan(kodas);}
    else{lkOrders=lkOrders.filter(o=>o.kodas!==kodas);lkRes('re','KLAIDA',kodas,'Nepavyko');beep('err');lkStats();rlkList();}
  });
}

function lkRes(c,t,kodas,s){
  const b=document.getElementById('lkRes');
  b.className='res '+c;b.style.display='block';
  document.getElementById('lkRt').textContent=t;
  document.getElementById('lkRc').textContent=kodas;
  document.getElementById('lkRs').textContent=s;
}

async function loadLk(){
  try{const r=await api('GET','/api/lakstai');lkOrders=r.orders||[];lkStats();rlkList();document.getElementById('connDot').className='dot ok';}
  catch(e){document.getElementById('connDot').className='dot err';toast('Nepavyko prisijungti',true);}
}
function lkAddL(o){const i=lkOrders.findIndex(x=>x.kodas===o.kodas);if(i>=0)lkOrders[i]=o;else lkOrders.push(o);}
function lkStats(){
  const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length,p=lkOrders.filter(o=>!o.collected).length;
  const pc=t>0?Math.round(c/t*100):0,pd=t>0?Math.round(d/t*100):0;
  document.getElementById('lkT').textContent=t;document.getElementById('lkC').textContent=c;
  document.getElementById('lkD').textContent=d;document.getElementById('lkP').textContent=p;
  document.getElementById('lkPct').textContent=pc+'%';
  document.getElementById('lkPfc').style.width=pc+'%';document.getElementById('lkPfd').style.width=pd+'%';
  document.getElementById('lkBdg').textContent=p||t;
}
function lkFlt(f,b){lkF=f;document.querySelectorAll('.frow .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rlkList();}
function sortLk(l){return[...l].sort((a,b)=>{const n=s=>parseInt((s.match(/[0-9]+/)||[0])[0]);return n(a.kodas)-n(b.kodas);});}
function rlkList(){
  const el=document.getElementById('lkList'),q=(document.getElementById('lkSrch').value||'').toLowerCase();
  let l=sortLk(lkOrders);
  if(lkF==='p')l=l.filter(o=>!o.collected);if(lkF==='c')l=l.filter(o=>o.collected&&!o.delivered);if(lkF==='d')l=l.filter(o=>o.delivered);
  if(q)l=l.filter(o=>o.kodas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(lkOrders.length===0?'Nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>{
    const sc=o.delivered?'sdd':o.collected?'sc':'';
    const sl=o.delivered?'s2':o.collected?'s1':'s0';
    const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
    const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(11,16);
    return`<div class="oi ${sc}"><div class="od"></div><div class="oc">${o.kodas}</div><span class="ost ${sl}">${st}</span><div class="otm">${tm}</div><button class="btn btn-d btn-sm" onclick="lkDel('${o.kodas}')">✕</button></div>`;
  }).join('');
}
async function lkDel(k){if(!confirm('Ištrinti "'+k+'"?'))return;await api('DELETE','/api/lakstai/'+k);lkOrders=lkOrders.filter(o=>o.kodas!==k);lkStats();rlkList();toast('Ištrinta');}
function askStage(){
  const n=document.getElementById('stageInp').value.trim();
  if(!n){toast('Įvesk etapo pavadinimą!',true);return;}
  if(!lkOrders.length){toast('Nėra užsakymų',true);return;}
  pendingSt=n;const t=lkOrders.length,c=lkOrders.filter(o=>o.collected).length,d=lkOrders.filter(o=>o.delivered).length;
  document.getElementById('stMn').textContent='Etapas: "'+n+'"';
  document.getElementById('stMs').innerHTML='Iš viso: <strong>'+t+'</strong><br>Surinkta: <strong>'+c+'</strong><br>Perduota: <strong>'+d+'</strong><br>Laukia: <strong>'+(t-c)+'</strong>';
  document.getElementById('stModal').style.display='flex';
}
async function confirmStage(){
  CM('stModal');
  const r=await api('POST','/api/lakstai/archive',{pavadinimas:pendingSt});
  if(r.success){lkOrders=[];document.getElementById('stageInp').value='';lkStats();rlkList();await loadStages();beep('del');toast('Archyvuota: "'+r.archiveName+'"');lkRes('ra','ARCHYVUOTA',r.archiveName,r.collected+'/'+r.total+' surinkta');}
  else toast(r.message||'Klaida',true);
  focusScan();
}

// ════ SANDĖLIS ════
async function loadStock(){try{const r=await api('GET','/api/sandelis');stock=r.stock||[];rStock();document.getElementById('stkBdg').textContent=stock.length;}catch(e){}}
async function loadHist(){try{const r=await api('GET','/api/sandelis/istorija');history=r.history||[];rHist();}catch(e){}}

function rStock(){
  const el=document.getElementById('stkTbl'),su=document.getElementById('stkSum');
  if(!stock.length){el.innerHTML='<div class="empty-s">Sandėlis tuščias</div>';su.innerHTML='';return;}
  const totVnt=stock.reduce((s,r)=>s+r.likoVnt,0);
  const totKg=stock.reduce((s,r)=>s+r.likoKg,0);
  const totT=Math.round(totKg/10)/100;
  const totVal=stock.reduce((s,r)=>s+r.verte,0);
  const byT={};stock.forEach(r=>{if(!byT[r.storis])byT[r.storis]={vnt:0,kg:0};byT[r.storis].vnt+=r.likoVnt;byT[r.storis].kg+=r.likoKg;});
  su.innerHTML=`<div class="stk-s"><div class="stk-n">${totVnt}</div><div class="stk-l">Viso vnt.</div></div><div class="stk-s"><div class="stk-n">${totKg.toFixed(1)}</div><div class="stk-l">Viso kg</div></div><div class="stk-s"><div class="stk-n" style="color:var(--gn)">${totT}</div><div class="stk-l">Tonos</div></div><div class="stk-s"><div class="stk-n" style="color:var(--or)">${totVal.toFixed(2)}</div><div class="stk-l">Vertė €</div></div>`+
    Object.entries(byT).sort((a,b)=>parseFloat(a[0])-parseFloat(b[0])).map(([t,v])=>`<div class="stk-s"><div class="stk-n" style="font-size:15px">${v.vnt}vnt</div><div class="stk-l">${t}mm · ${(Math.round(v.kg/10)/100).toFixed(2)}t</div></div>`).join('');
  const sorted=[...stock].sort((a,b)=>a.storis-b.storis);
  el.innerHTML=sorted.map(r=>{
    const nc=r.likoVnt===0?'empty':r.likoVnt<=settings.lowAlert?'warn':'ok';
    return`<div class="stk-row"><div><div class="stk-thick">${r.storis}<span>mm</span></div></div><div><div class="stk-dims">${r.matmenys}mm</div><div class="stk-sub">${r.pastabos||''}</div></div><div><div class="stk-num ${nc}">${r.likoVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:13px;color:var(--tx2)">${r.likoKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${r.likoT.toFixed(3)}</div><div class="stk-sub">t</div></div><div><div class="stk-val">${r.verte.toFixed(2)}€</div><div class="stk-sub">${r.kainaKg>0?r.kainaKg+'€/kg':''}</div></div><div class="stk-acts"><button class="btn btn-y btn-sm" onclick="showUse('${r.id}','${r.storis}mm ${r.matmenys}',${r.likoVnt})">−</button><button class="btn btn-d btn-sm" onclick="delStk('${r.id}')">✕</button></div></div>`;
  }).join('')+`<div class="stk-tot"><div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tx2);font-weight:700">VISO</div><div></div><div><div class="stk-num" style="font-size:13px;color:var(--ac)">${totVnt}</div><div class="stk-sub">vnt.</div></div><div><div class="stk-num" style="font-size:12px;color:var(--tx2)">${totKg.toFixed(1)}</div><div class="stk-sub">kg</div></div><div><div class="stk-num" style="font-size:13px;color:var(--gn);font-weight:800">${totT}</div><div class="stk-sub">t</div></div><div><div class="stk-val" style="font-size:13px;font-weight:800">${totVal.toFixed(2)}€</div></div><div></div></div>`;
}

function rHist(){
  const el=document.getElementById('histTbl');
  if(!history.length){el.innerHTML='<div class="empty-s">Dar nėra istorijos</div>';return;}
  el.innerHTML=`<table><thead><tr><th>Data</th><th>Veiksmas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris kg</th></tr></thead><tbody>${history.slice(0,50).map(h=>`<tr><td class="mono" style="font-size:10px;color:var(--tx3)">${h.data}</td><td><span class="hist-act ${h.veiksmas[0]}">${h.veiksmas}</span></td><td class="mono">${h.storis}mm</td><td class="mono" style="color:var(--tx2)">${h.matmenys}</td><td class="mono">${h.kiekis}vnt.</td><td class="num">${h.svorisIšViso.toFixed(2)}</td></tr>`).join('')}</tbody></table>`;
}

function showRecv(){
  if(settings.defaultPrice)document.getElementById('recP').value=settings.defaultPrice;
  document.getElementById('recvModal').style.display='flex';
}
function rcRecv(){
  const t=parseFloat(document.getElementById('recThk').value)||0,w=parseFloat(document.getElementById('recW').value)||0,l=parseFloat(document.getElementById('recL').value)||0,q=parseInt(document.getElementById('recQ').value)||1,p=parseFloat(document.getElementById('recP').value)||0;
  if(!w||!l){document.getElementById('recPrev').textContent='Įvesk matmenis...';return;}
  const we=Math.round((w/1000)*(l/1000)*(t/1000)*TANKIS*100)/100;
  const tot=Math.round(we*q*100)/100,totT=Math.round(tot/10)/100,val=p>0?Math.round(tot*p*100)/100:0;
  document.getElementById('recPrev').innerHTML=`1 lakštas: <strong style="color:var(--ac)">${we}kg</strong> · ${q}vnt.: <strong style="color:var(--gn)">${tot}kg = ${totT}t</strong>${val>0?' · <strong style="color:var(--or)">'+val+'€</strong>':''}`;
}
async function doRecv(){
  const t=document.getElementById('recThk').value,w=document.getElementById('recW').value,l=document.getElementById('recL').value,q=document.getElementById('recQ').value,p=document.getElementById('recP').value,n=document.getElementById('recN').value;
  if(!w||!l){toast('Įvesk matmenis!',true);return;}
  const r=await api('POST','/api/sandelis/gauti',{storis:t,plotis:w,ilgis:l,kiekis:q,kaina:p,pastabos:n});
  if(r.success){CM('recvModal');await loadStock();await loadHist();toast('Pridėta: '+q+'vnt. × '+t+'mm ('+r.likoT+'t)');}
}
function showUse(id,label,rem){curStockId=id;document.getElementById('useInfo').innerHTML='<strong>'+label+'</strong><br>Liko: <strong style="color:var(--gn)">'+rem+'vnt.</strong>';document.getElementById('useQ').value=1;document.getElementById('useNote').value='';document.getElementById('useModal').style.display='flex';}
async function doUse(){
  const q=parseInt(document.getElementById('useQ').value)||1,n=document.getElementById('useNote').value;
  const r=await api('POST','/api/sandelis/'+curStockId+'/naudoti',{kiekis:q,pastabos:n});
  if(r.success){CM('useModal');await loadStock();await loadHist();toast('Sunaudota: '+q+'vnt. Liko: '+r.likoVnt+'vnt.');}
  else toast('Klaida',true);
}
async function delStk(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/sandelis/'+id);await loadStock();toast('Ištrinta');}
function showSett(){document.getElementById('settP').value=settings.defaultPrice||'';document.getElementById('settL').value=settings.lowAlert||2;document.getElementById('settModal').style.display='flex';}
function saveSett(){settings.defaultPrice=parseFloat(document.getElementById('settP').value)||0;settings.lowAlert=parseInt(document.getElementById('settL').value)||2;CM('settModal');localStorage.setItem('sandSettings',JSON.stringify(settings));toast('Nustatymai išsaugoti');}

// ════ ARCHYVAI ════
async function loadStages(){try{const r=await api('GET','/api/etapai');stages=r.stages||[];document.getElementById('archBdg').textContent=stages.length;rStages();}catch(e){}}
function rStages(){
  const el=document.getElementById('stageCards');
  if(!stages.length){el.innerHTML='<div class="empty-s">Dar nėra archyvų</div>';return;}
  el.innerHTML=stages.map(s=>{
    const t=s.total||0,c=s.collected||0,d=s.delivered||0,p=s.pending||(t-c),pct=t>0?Math.round(c/t*100):0;
    return`<div class="scc ${archOpen===s.name?'open':''}" onclick="toggleArch('${s.name.replace(/'/g,"\\'")}')"><div class="scn">${s.name}</div><div class="scst"><div><span class="n">${t}</span><span class="l">Viso</span></div><div><span class="n g">${c}</span><span class="l">Surinkta</span></div><div><span class="n b">${d}</span><span class="l">Perduota</span></div><div><span class="n ${p>0?'r':'g'}">${p}</span><span class="l">Liko</span></div></div><div class="scp"><div class="scpf" style="width:${pct}%"></div></div></div>`;
  }).join('');
}
async function toggleArch(name){
  if(archOpen===name){archOpen=null;closeAd();rStages();return;}
  archOpen=name;rStages();
  document.getElementById('adTitle').textContent=name;
  document.getElementById('adList').innerHTML='<div class="empty-s"><span class="sp"></span> Kraunama...</div>';
  document.getElementById('adBox').style.display='block';
  try{
    const r=await api('GET','/api/etapai/'+encodeURIComponent(name));
    const items=sortLk(r.orders||[]);
    if(!items.length){document.getElementById('adList').innerHTML='<div class="empty-s">Tuščias</div>';return;}
    document.getElementById('adList').innerHTML=items.map(o=>{
      const sc=o.delivered?'sdd':o.collected?'sc':'';const tc=o.delivered?'d':o.collected?'c':'r';const st=o.delivered?'Perduota':o.collected?'Surinkta':'Registruota';
      const tm=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(0,16);
      return`<div class="adi ${sc}"><div class="addot"></div><div class="adcode">${o.kodas}</div><span class="adtag ${tc}">${st}</span><div class="adtime">${tm}</div></div>`;
    }).join('');
  }catch(e){}
}
function closeAd(){document.getElementById('adBox').style.display='none';archOpen=null;rStages();}

// ════ DXF ════
async function loadDxfOrds(){try{const r=await api('GET','/api/uzsakymai');dxfOrders=r.orders||[];dxfSum();rOrds();document.getElementById('dxfBdg').textContent=dxfOrders.length;}catch(e){}}
function dxfSum(){
  const t=dxfOrders.length,n=dxfOrders.filter(o=>o.statusas==='Naujas').length,a=dxfOrders.filter(o=>o.statusas==='Vykdomas').length,d=dxfOrders.filter(o=>o.statusas==='Baigtas').length,w=dxfOrders.reduce((s,o)=>s+o.bendraSvoris,0);
  document.getElementById('dxfSum').innerHTML=`<div class="smc"><div class="smn a">${t}</div><div class="sml">Iš viso</div></div><div class="smc"><div class="smn" style="color:var(--yw)">${n}</div><div class="sml">Nauji</div></div><div class="smc"><div class="smn a">${a}</div><div class="sml">Vykdomi</div></div><div class="smc"><div class="smn" style="color:var(--gn)">${d}</div><div class="sml">Baigti</div></div><div class="smc"><div class="smn a">${w.toFixed(2)}</div><div class="sml">Svoris kg</div></div>`;
}
function dxfFlt(f,b){dxfF=f;document.querySelectorAll('.fbar .fb').forEach(x=>x.classList.remove('active'));b.classList.add('active');rOrds();}
function rOrds(){
  const el=document.getElementById('ordsGrid'),q=(document.getElementById('dxfSrch').value||'').toLowerCase();
  let l=[...dxfOrders].sort((a,b)=>new Date(b.sukurta)-new Date(a.sukurta));
  if(dxfF!=='all')l=l.filter(o=>o.statusas===dxfF);if(q)l=l.filter(o=>o.klientas.toLowerCase().includes(q));
  if(!l.length){el.innerHTML='<div class="empty-s">'+(dxfOrders.length===0?'Dar nėra užsakymų':'Nerasta')+'</div>';return;}
  el.innerHTML=l.map(o=>`<div class="ocard" onclick="openOrd('${o.id}')"><div class="oct"><div class="oid">${o.id}</div><div style="display:flex;gap:4px"><span class="stb ${o.statusas}">${o.statusas}</span><button class="btn btn-d btn-sm" onclick="event.stopPropagation();quickDelOrd('${o.id}','${o.klientas.replace(/'/g,"\\'")}')">✕</button></div></div><div class="ocli">${o.klientas}</div><div class="ocdesc">${o.aprasymas||'—'}</div><div class="ocm"><div class="ocmi"><span class="v">${o.bendraSvoris.toFixed(3)}</span><span class="l"> kg</span></div><div class="ocmi"><span class="v">${o.detaliuSk}</span><span class="l"> det.</span></div><div class="ocmi"><span class="l">${(o.sukurta||'').slice(0,10)}</span></div></div></div>`).join('');
}
async function quickDelOrd(id,klientas){if(!confirm('Ištrinti "'+klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+id);dxfOrders=dxfOrders.filter(o=>o.id!==id);dxfSum();rOrds();toast('Ištrinta');}
function showNewOrd(){document.getElementById('noModal').style.display='flex';setTimeout(()=>document.getElementById('noC').focus(),100);}
async function createOrd(){
  const c=document.getElementById('noC').value.trim();if(!c){toast('Įvesk klientą!',true);return;}
  const r=await api('POST','/api/uzsakymai',{klientas:c,aprasymas:document.getElementById('noD').value.trim(),pastabos:document.getElementById('noN').value.trim()});
  if(r.success){CM('noModal');document.getElementById('noC').value='';document.getElementById('noD').value='';document.getElementById('noN').value='';await loadDxfOrds();toast('Sukurta!');openOrd(r.id);}
}
async function openOrd(id){
  const o=dxfOrders.find(x=>x.id===id);if(!o)return;curOrd=o;
  document.getElementById('dvId').textContent=o.id;document.getElementById('dvCli').textContent=o.klientas;document.getElementById('dvDsc').textContent=o.aprasymas||'';
  document.getElementById('dvWt').textContent=o.bendraSvoris.toFixed(3);document.getElementById('dvSt').value=o.statusas||'Naujas';
  document.getElementById('dvMeta').textContent=(o.sukurta||'').slice(0,16)+(o.pastabos?' · '+o.pastabos:'');
  SW('dv');await loadDets();
}
function back2Ords(){SW('dxf');loadDxfOrds();curArea=0;curContour='';document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';}
async function chSt(){if(!curOrd)return;await api('PUT','/api/uzsakymai/'+curOrd.id+'/statusas',{statusas:document.getElementById('dvSt').value});toast('Statusas atnaujintas');}
async function delOrd(){if(!curOrd)return;if(!confirm('Ištrinti "'+curOrd.klientas+'"?'))return;await api('DELETE','/api/uzsakymai/'+curOrd.id);toast('Ištrinta');back2Ords();}
async function loadDets(){
  if(!curOrd)return;
  const r=await api('GET','/api/uzsakymai/'+curOrd.id+'/detales');
  dxfDets=r.details||[];rDets();
  document.getElementById('dvWt').textContent=dxfDets.reduce((s,d)=>s+d.svoris,0).toFixed(3);
}

function rDets(){
  const w=document.getElementById('dtWrap');
  dxfDets.sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  if(!dxfDets.length){w.innerHTML='<div class="empty-s">Dar nėra detalių</div>';return;}
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  const tq=dxfDets.reduce((s,d)=>s+d.kiekis,0);
  const groups={};
  dxfDets.forEach(d=>{const t=String(d.storis);if(!groups[t])groups[t]={t,dets:[],w:0,q:0};groups[t].dets.push(d);groups[t].w+=d.svoris;groups[t].q+=d.kiekis;});
  let rows='';let idx=0;
  Object.values(groups).forEach(g=>{
    rows+=`<tr class="det-grp-hdr"><td colspan="2"></td><td colspan="2"><span class="det-grp-t">${g.t}mm</span></td><td><span class="det-grp-s">${g.dets.length}det.</span></td><td><span class="det-grp-s">${g.q}vnt.</span></td><td><span class="det-grp-s" style="color:var(--ac)">${g.w.toFixed(3)}kg</span></td><td></td></tr>`;
    g.dets.forEach(d=>{
      idx++;
      rows+=`<tr><td class="mono" style="color:var(--tx3);font-size:10px">${idx}</td><td style="font-weight:600">${d.pavadinimas}</td><td><select class="det-inp" onchange="updDet('${d.detId}','storis',this.value)">${STORIAI.map(t=>`<option value="${t}"${d.storis===t?' selected':''}>${t}mm</option>`).join('')}</select></td><td class="mono" style="font-size:11px;color:var(--tx2)">${calcDims(d)}</td><td><input type="number" class="det-inp" value="${d.kiekis}" min="1" style="width:50px" onchange="updDet('${d.detId}','kiekis',this.value)"></td><td><input type="number" class="det-inp num" value="${d.svoris.toFixed(3)}" min="0" step="0.001" style="width:70px;color:var(--ac);font-weight:700" id="w-${d.detId}" onchange="updDetW('${d.detId}',this.value)"><span style="font-size:10px;color:var(--tx3)">kg</span></td><td><button class="btn btn-d btn-sm" onclick="delDet('${d.detId}')">✕</button></td></tr>`;
    });
  });
  w.innerHTML=`<table><thead><tr><th>#</th><th>Pavadinimas</th><th>Storis</th><th>Matmenys</th><th>Kiekis</th><th>Svoris</th><th></th></tr></thead><tbody>${rows}</tbody></table><div class="dttot"><span style="color:var(--tx3)">Viso: <strong style="color:var(--tx)">${tq}vnt.</strong></span><span>Bendras svoris: <span class="tot">${tw.toFixed(3)}kg</span></span></div>`;
}

async function updDet(detId,field,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  if(field==='storis')d.storis=parseFloat(value);else if(field==='kiekis')d.kiekis=parseInt(value)||1;
  d.svoris=Math.round(d.plotas*(d.storis/10)*(TANKIS/1000)*d.kiekis/1000*1000)/1000;
  const wEl=document.getElementById('w-'+detId);if(wEl)wEl.value=d.svoris.toFixed(3);
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,plotas:d.plotas});
}
async function updDetW(detId,value){
  const d=dxfDets.find(x=>x.detId===detId);if(!d)return;
  d.svoris=Math.round(parseFloat(value)*1000)/1000;
  _updateTotals();
  api('PUT','/api/detales/'+detId,{storis:d.storis,kiekis:d.kiekis,svoris:d.svoris,plotas:d.plotas});
}
function _updateTotals(){
  const tw=dxfDets.reduce((s,d)=>s+d.svoris,0);
  document.getElementById('dvWt').textContent=tw.toFixed(3);
}
async function delDet(id){if(!confirm('Ištrinti?'))return;await api('DELETE','/api/detales/'+id);dxfDets=dxfDets.filter(d=>d.detId!==id);rDets();_updateTotals();toast('Ištrinta');}

// DXF ĮKĖLIMAS
function handleDxf(e){if(e.target.files.length)handleMultiDxf(Array.from(e.target.files));}
function handleFolder(e){
  if(!e.target.files.length)return;
  const files=Array.from(e.target.files).filter(f=>f.name.toLowerCase().endsWith('.dxf'));
  if(!files.length){toast('Aplanke nerasta .dxf failų!',true);return;}
  const folderName=(files[0].webkitRelativePath||'').split('/')[0]||'';
  const ft=thickFromName(folderName);
  if(ft){document.getElementById('dThk').value=ft;document.getElementById('mThk').value=ft;localStorage.setItem('lastThick',String(ft));toast('Aplankas: '+folderName+' → '+ft+'mm, '+files.length+' failų',false,'b');}
  handleMultiDxf(files);
}
async function handleMultiDxf(files){
  if(!curOrd){toast('Pirma atidaryk užsakymą!',true);return;}
  if(files.length===1){procDxf(files[0]);return;}
  const defThick=parseFloat(localStorage.getItem('lastThick')||document.getElementById('dThk').value)||3;
  const defQty=parseInt(document.getElementById('dQty').value)||1;
  let ok=0,fail=0;
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Įkeliama '+files.length+' failų...';
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
  document.getElementById('dropZ').querySelector('.dz-t').textContent='Tempk DXF failus čia arba spusk';
  document.getElementById('dxfFile').value='';
  await loadDets();
  toast(fail>0?`Įkelta: ${ok}, nepavyko: ${fail}`:`Sėkmingai įkeltos ${ok} detalės!`);
}
function procDxf(file){
  const r=new FileReader();
  r.onload=e=>{
    try{
      const res=pDxf(e.target.result);
      curArea=res.areaCm2;
      curContour=serializeContour(res.entities,res.dimW,res.dimH);
      document.getElementById('dName').value=file.name.replace(/[.]dxf$/i,'');
      const at=thickFromName(file.name);const aq=qtyFromName(file.name);
      if(at){document.getElementById('dThk').value=at;localStorage.setItem('lastThick',String(at));}
      if(aq)document.getElementById('dQty').value=aq;
      drawPrev(res.entities);
      document.getElementById('pForm').style.display='block';
      rcW();
      toast('DXF: '+res.areaCm2.toFixed(2)+'cm²'+(at?' · '+at+'mm':''));
    }catch(ex){toast('Klaida: '+ex.message,true);}
  };
  r.readAsText(file);
}
function rcW(){const t=parseFloat(document.getElementById('dThk').value)||3,q=parseInt(document.getElementById('dQty').value)||1,w=curArea*(t/10)*(TANKIS/1000)*q/1000;document.getElementById('wPv').textContent=w.toFixed(3);document.getElementById('wAr').textContent='Plotas: '+curArea.toFixed(2)+'cm² · '+t+'mm × '+q+'vnt.';}
function rcM(){const t=parseFloat(document.getElementById('mThk').value)||3,a=parseFloat(document.getElementById('mArea').value)||0,q=parseInt(document.getElementById('mQty').value)||1;document.getElementById('mWp').textContent=(a*(t/10)*(TANKIS/1000)*q/1000).toFixed(3)+' kg';}
async function addDet(){
  if(!curOrd)return;if(curArea<=0){toast('Plotas=0',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('dName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('dThk').value),plotas:curArea,kiekis:parseInt(document.getElementById('dQty').value)||1,konturas:curContour});
  if(r.success){document.getElementById('pForm').style.display='none';document.getElementById('cvW').style.display='none';document.getElementById('dxfFile').value='';curArea=0;curContour='';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}
async function addMDet(){
  if(!curOrd)return;const a=parseFloat(document.getElementById('mArea').value)||0;if(a<=0){toast('Įvesk plotą!',true);return;}
  const r=await api('POST','/api/detales',{uzsakymoId:curOrd.id,pavadinimas:document.getElementById('mName').value.trim()||'Detalė',storis:parseFloat(document.getElementById('mThk').value),plotas:a,kiekis:parseInt(document.getElementById('mQty').value)||1,konturas:''});
  if(r.success){document.getElementById('mName').value='';document.getElementById('mArea').value='';document.getElementById('mQty').value='1';document.getElementById('mWp').textContent='0.000 kg';await loadDets();toast('Detalė: '+r.svoris.toFixed(3)+'kg');}
}

// ATASKAITA
function setPeriod(days){
  const to=new Date(),from=new Date();
  if(days===0)from.setDate(1);else from.setDate(to.getDate()-days);
  document.getElementById('repFrom').value=from.toISOString().slice(0,10);
  document.getElementById('repTo').value=to.toISOString().slice(0,10);
}
async function genRep(){
  const from=document.getElementById('repFrom').value,to=document.getElementById('repTo').value;
  if(!from||!to){toast('Pasirink laikotarpį!',true);return;}
  const r=await api('GET',`/api/ataskaita?nuo=${from}&iki=${to}`);
  const el=document.getElementById('repOut');
  el.style.display='block';
  el.innerHTML=`<div class="card"><div class="rep-s"><div class="rep-st">Laikotarpis: ${from} — ${to}</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.lakstai.gauta}</div><div class="l">Lakštų gauta</div></div><div class="rep-sc"><div class="n">${r.lakstai.surinkta}</div><div class="l">Surinkta</div></div><div class="rep-sc"><div class="n">${r.lakstai.perduota}</div><div class="l">Perduota</div></div><div class="rep-sc"><div class="n">${r.dxf.sk}</div><div class="l">DXF užsakymų</div></div><div class="rep-sc"><div class="n">${r.dxf.svoris.toFixed(1)}</div><div class="l">DXF svoris kg</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio judėjimas</div><div class="rep-sr"><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.sandelis.gautaKg.toFixed(1)}</div><div class="l">Gauta kg</div></div><div class="rep-sc"><div class="n" style="color:var(--rd)">${r.sandelis.sunaudotaKg.toFixed(1)}</div><div class="l">Sunaudota kg</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.gautaVerte.toFixed(2)}</div><div class="l">Gauta vertė €</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.sandelis.sunaudotaVerte.toFixed(2)}</div><div class="l">Sunaudota €</div></div></div></div><div class="rep-s"><div class="rep-st">Sandėlio likutis dabar</div><div class="rep-sr"><div class="rep-sc"><div class="n">${r.likutis.vnt}</div><div class="l">Viso vnt.</div></div><div class="rep-sc"><div class="n" style="color:var(--gn)">${r.likutis.t}</div><div class="l">Tonos</div></div><div class="rep-sc"><div class="n" style="color:var(--or)">${r.likutis.verte.toFixed(2)}</div><div class="l">Vertė €</div></div></div></div></div>`;
}

// SPAUSDINIMAS
function printOrd(){
  if(!curOrd)return;
  const sorted=[...dxfDets].sort((a,b)=>a.storis-b.storis||a.pavadinimas.localeCompare(b.pavadinimas));
  const groups=new Map();sorted.forEach(d=>{if(!groups.has(d.storis))groups.set(d.storis,[]);groups.get(d.storis).push(d);});
  const totW=sorted.reduce((s,d)=>s+d.svoris,0),totQ=sorted.reduce((s,d)=>s+d.kiekis,0);
  const now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  const sumRows=[...groups.entries()].map(([t,dets])=>{const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);return`<tr><td style="font-weight:700;color:#1e3a5f">${t}mm</td><td style="text-align:center">${dets.length}</td><td style="text-align:center">${gq}</td><td style="text-align:right;font-weight:700">${gw.toFixed(3)}</td></tr>`;}).join('');
  let html=`<div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right"><div class="ppbc"><svg id="pbc"></svg></div></div></div><div class="ppinfo"><div><div class="ppi-l">Bendras svoris</div><div class="ppi-v">${totW.toFixed(3)} kg</div></div><div><div class="ppi-l">Viso detalių</div><div class="ppi-v">${totQ} vnt.</div></div><div><div class="ppi-l">Storių sk.</div><div class="ppi-v">${groups.size} storiai</div></div></div><table class="pptable" style="margin-bottom:4mm"><thead><tr><th>Storis</th><th style="text-align:center">Poz.</th><th style="text-align:center">Vnt.</th><th style="text-align:right">Svoris kg</th></tr></thead><tbody>${sumRows}<tr style="background:#f0f0f0;font-weight:700"><td>VISO</td><td style="text-align:center">${sorted.length}</td><td style="text-align:center">${totQ}</td><td style="text-align:right">${totW.toFixed(3)}</td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>Išspausdinta: ${now}</span><span>${curOrd.id}</span></div>`;
  groups.forEach((dets,thick)=>{
    const gw=dets.reduce((s,d)=>s+d.svoris,0),gq=dets.reduce((s,d)=>s+d.kiekis,0);
    const rows=dets.map((d,i)=>`<tr><td>${i+1}</td><td><strong>${d.pavadinimas}</strong></td><td style="text-align:center">${calcDims(d)}</td><td style="text-align:center">${d.kiekis}</td><td style="text-align:right"><strong>${d.svoris.toFixed(3)}</strong></td><td style="text-align:center;vertical-align:middle">${drawContourSvg(d.konturas,12)}</td></tr>`).join('');
    html+=`<div style="page-break-before:always"><div class="pph"><div><div class="pptitle">${curOrd.klientas}</div><div class="ppid">${curOrd.id}</div></div><div style="text-align:right;font-size:22pt;font-weight:900;color:#1e3a5f;border:3px solid #1e3a5f;padding:2mm 4mm;display:inline-block">${thick}mm</div></div><div class="ppinfo"><div><div class="ppi-l">Svoris (${thick}mm)</div><div class="ppi-v">${gw.toFixed(3)} kg</div></div><div><div class="ppi-l">Kiekis</div><div class="ppi-v">${gq}vnt. (${dets.length}poz.)</div></div><div><div class="ppi-l">Data</div><div class="ppi-v">${now}</div></div></div><table class="pptable"><thead><tr><th>#</th><th>Pavadinimas</th><th style="text-align:center">Matmenys</th><th style="text-align:center">Kiekis</th><th style="text-align:right">Svoris kg</th><th style="text-align:center;width:25mm">Vaizdas</th></tr></thead><tbody>${rows}<tr style="background:#f0f0f0;font-weight:700"><td colspan="3" style="text-align:right">VISO:</td><td style="text-align:center">${gq}vnt.</td><td style="text-align:right">${gw.toFixed(3)}kg</td><td></td></tr></tbody></table><div class="ppsign"><div class="pss">Pagamino</div><div class="pss">Priėmė</div><div class="pss">Data</div></div><div class="ppfoot"><span>${thick}mm · ${dets.length}poz. · ${gq}vnt. · ${gw.toFixed(3)}kg</span><span>${curOrd.id}</span></div></div>`;
  });
  document.getElementById('printArea').innerHTML=html;
  setTimeout(()=>{try{JsBarcode('#pbc',curOrd.id,{format:'CODE128',width:2,height:45,displayValue:false,margin:0});}catch(e){}},100);
  document.getElementById('printMod').style.display='flex';
}

function dlPdf(){
  const c=document.getElementById('printArea').innerHTML;
  const w=window.open('','_blank');
  const s='<style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.pptable{width:100%;border-collapse:collapse;margin-bottom:3mm;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:1.5mm 2mm;text-align:left;font-size:7pt;text-transform:uppercase}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style>';
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'+s+'</head><body>'+c+'</body>');
  w.document.close();
  setTimeout(function(){w.print();},500);
}

function nowS(){return new Date().toISOString().replace('T',' ').slice(0,19);}

// Nustatymų įkėlimas
const savedSett=localStorage.getItem('sandSettings');
if(savedSett)try{settings=JSON.parse(savedSett);}catch(e){}

async function siustiEmail(){
  const btn=document.getElementById('emailBtn');
  btn.textContent='Siunčiama...';btn.disabled=true;
  try{
    const r=await fetch('/api/email/siusti',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    const d=await r.json();
    if(d.success){alert('✓ '+d.message);}
    else{alert('Klaida: '+(d.detail||d.message));}
  }catch(e){alert('Klaida: '+e.message);}
  btn.textContent='✉ Siųsti ataskaitą';btn.disabled=false;
}

function genPdfReport(){
  var surinkti=lkOrders.filter(function(o){return o.collected&&!o.delivered;}).sort(function(a,b){var na=parseInt((a.kodas.match(/[0-9]+/g)||[0]).join(''))||0;var nb=parseInt((b.kodas.match(/[0-9]+/g)||[0]).join(''))||0;return na-nb;});
  var perduoti=lkOrders.filter(function(o){return o.delivered;}).sort(function(a,b){var na=parseInt((a.kodas.match(/[0-9]+/g)||[0]).join(''))||0;var nb=parseInt((b.kodas.match(/[0-9]+/g)||[0]).join(''))||0;return na-nb;});
  var laukia=lkOrders.filter(function(o){return !o.collected;}).sort(function(a,b){var na=parseInt((a.kodas.match(/[0-9]+/g)||[0]).join(''))||0;var nb=parseInt((b.kodas.match(/[0-9]+/g)||[0]).join(''))||0;return na-nb;});
  var now=new Date().toLocaleDateString('lt-LT')+' '+new Date().toTimeString().slice(0,5);
  function tableRows(arr,color){
    if(!arr.length)return '<tr><td colspan="2" style="color:#aaa;padding:4px 8px">Tuscia</td></tr>';
    return arr.map(function(o){var t=(o.delivered?o.deliveredAt:o.collected?o.collectedAt:o.registered||'').slice(11,16);return '<tr><td style="padding:4px 10px;border-bottom:1px solid #eee;font-family:monospace">'+o.kodas+'</td><td style="padding:4px 10px;border-bottom:1px solid #eee;color:'+color+'">'+t+'</td></tr>';}).join('');
  }
  var html='<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:Arial,sans-serif;margin:0;padding:12mm;font-size:10pt}h1{font-size:16pt;font-weight:900;margin-bottom:2mm}h2{font-size:11pt;font-weight:700;margin:6mm 0 2mm;padding:2mm 4mm;border-left:4px solid #0969da}h2.g{border-left-color:#1a7f37}h2.b{border-left-color:#0969da}h2.y{border-left-color:#9a6700}table{width:100%;border-collapse:collapse;margin-bottom:4mm}th{background:#1e3a5f;color:white;padding:2mm 4mm;text-align:left;font-size:9pt}td{padding:2mm 4mm;font-size:9pt}.sum{display:flex;gap:8mm;margin:4mm 0;padding:3mm;background:#f5f5f5}.sum-n{font-size:18pt;font-weight:900;font-family:monospace}.sum-l{font-size:8pt;color:#666;text-transform:uppercase}.foot{margin-top:8mm;font-size:8pt;color:#aaa;border-top:1px solid #ddd;padding-top:3mm}@page{margin:8mm;size:A4}</style></head><body>'
    +'<h1>Sandelio ataskaita</h1><div style="font-size:9pt;color:#666;margin-bottom:4mm">'+now+'</div>'
    +'<div class="sum"><div><div class="sum-n" style="color:#1f2328">'+lkOrders.length+'</div><div class="sum-l">Is viso</div></div><div><div class="sum-n" style="color:#1a7f37">'+surinkti.length+'</div><div class="sum-l">Surinkta</div></div><div><div class="sum-n" style="color:#0969da">'+perduoti.length+'</div><div class="sum-l">Perduota</div></div><div><div class="sum-n" style="color:#9a6700">'+laukia.length+'</div><div class="sum-l">Laukia</div></div></div>'
    +'<h2 class="g">Surinkta ('+surinkti.length+')</h2><table><tr><th>Kodas</th><th>Laikas</th></tr>'+tableRows(surinkti,'#1a7f37')+'</table>'
    +'<h2 class="b">Perduota ('+perduoti.length+')</h2><table><tr><th>Kodas</th><th>Laikas</th></tr>'+tableRows(perduoti,'#0969da')+'</table>'
    +'<h2 class="y">Laukia ('+laukia.length+')</h2><table><tr><th>Kodas</th><th>Laikas</th></tr>'+tableRows(laukia,'#9a6700')+'</table>'
    +'<div class="foot">Metalcraft - Sandelio sistema - '+now+'</div></body></html>';
  var blob=new Blob([html],{type:'text/html'});
  var url=URL.createObjectURL(blob);
  var a=document.createElement('a');
  a.href=url;
  a.download='ataskaita_'+new Date().toISOString().slice(0,10)+'.html';
  a.click();
  setTimeout(function(){URL.revokeObjectURL(url);},1000);
}

function dlPdf(){
  var c=document.getElementById('printArea').innerHTML;
  var w=window.open('','_blank');
  if(!w){alert('Leiskite popup langus!');return;}
  w.document.open();
  w.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:Arial,sans-serif;margin:0;padding:10mm}.pptable{width:100%;border-collapse:collapse;font-size:8pt}.pptable th{background:#1e3a5f;color:white;padding:2mm}.pptable td{padding:1mm 2mm;border-bottom:1px solid #ddd}.pph{display:flex;justify-content:space-between;margin-bottom:3mm;border-bottom:2px solid #000;padding-bottom:2mm}.pptitle{font-size:16pt;font-weight:900}.ppid{font-size:8pt;color:#666}.ppinfo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2mm;margin-bottom:3mm;background:#f5f5f5;padding:2.5mm}.ppi-l{font-size:7pt;color:#888;text-transform:uppercase}.ppi-v{font-size:10pt;font-weight:700}.ppsign{display:flex;gap:10mm;margin-top:4mm}.pss{border-top:1px solid #000;width:45mm;padding-top:2mm;font-size:7pt;color:#666}.ppfoot{display:flex;justify-content:space-between;font-size:7pt;color:#aaa;border-top:1px solid #ddd;padding-top:2mm;margin-top:3mm}@page{margin:6mm;size:A4}</style></head><body>'+c+'</body></html>');
  w.document.close();
  setTimeout(function(){w.print();},600);
}
