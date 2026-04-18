// ===== GLOBAL =====
let curEtapas = null;
let lkOrders = [];

// ===== API =====
async function api(method, url, data) {
  const r = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: data ? JSON.stringify(data) : undefined
  });

  if (!r.ok) {
    const txt = await r.text();
    console.error("API ERROR:", txt);
    throw new Error(txt);
  }

  return r.json();
}

// ===== ETAPAS SELECT =====
document.addEventListener('change', (e) => {
  if (e.target.id === 'etapasSelect') {
    curEtapas = e.target.value;
    console.log("Pasirinktas etapas:", curEtapas);
  }
});

// ===== SUKURTI ETAPA =====
async function newEtapas() {
  const inp =
    document.getElementById('newEtapasInp') ||
    document.querySelector('button[onclick="newEtapas()"]')?.previousElementSibling;

  if (!inp) {
    alert("Nerastas input");
    return;
  }

  const name = inp.value.trim();
  if (!name) {
    alert("Įvesk etapą");
    return;
  }

  try {
    await fetch('/api/etapai/issaugoti', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pavadinimas: name })
    });

    curEtapas = name;
    inp.value = '';

    alert("Etapas sukurtas: " + name);

  } catch (e) {
    console.error(e);
    alert("Klaida kuriant etapą");
  }
}

window.newEtapas = newEtapas;

// ===== INIT =====
window.onload = () => {
  const inp = document.getElementById('scanInp');

  if (!inp) {
    console.error("scanInp nerastas");
    return;
  }

  inp.focus();

  inp.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
      const kodas = inp.value.trim();
      if (!kodas) return;

      inp.value = "";
      await handleScan(kodas);
    }
  });
};

// ===== SCAN LOGIKA =====
async function handleScan(kodas) {

  if (!curEtapas) {
    alert("Pasirink etapą!");
    return;
  }

  console.log("SCAN:", kodas);

  const existing = lkOrders.find(o => o.kodas === kodas);

  // ===== JAU YRA =====
  if (existing) {

    if (existing.delivered) {
      alert("Jau perduota");
      return;
    }

    // PERDUOTI
    if (existing.collected) {
      existing.delivered = true;

      try {
        await api('POST', '/api/lakstai/next_v2', {
          kodas: kodas,
          etapas: curEtapas === '__be_etapo__' ? null : curEtapas
        });
      } catch (e) {
        existing.delivered = false;
        alert("Klaida perduodant");
      }

      return;
    }

    // SURINKTI
    existing.collected = true;

    try {
      await api('POST', '/api/lakstai/next_v2', {
        kodas: kodas,
        etapas: curEtapas === '__be_etapo__' ? null : curEtapas
      });
    } catch (e) {
      existing.collected = false;
      alert("Klaida surenkant");
    }

    return;
  }

  // ===== NAUJAS =====
  const obj = {
    kodas: kodas,
    collected: false,
    delivered: false,
    etapas: curEtapas
  };

  lkOrders.push(obj);

  try {
    await api('POST', '/api/lakstai/register_v2', {
      kodas: kodas,
      etapas: curEtapas === '__be_etapo__' ? null : curEtapas
    });

    console.log("Užregistruota:", kodas);

  } catch (e) {
    lkOrders = lkOrders.filter(o => o.kodas !== kodas);
    alert("Klaida registruojant");
  }
}
