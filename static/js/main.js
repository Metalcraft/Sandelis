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

// ===== ETAPAS =====
function newEtapas() {
  const inp = document.getElementById('newEtapasInp');
  if (!inp) return;

  const name = inp.value.trim();
  if (!name) {
    alert("Įvesk etapą");
    return;
  }

  curEtapas = name;
  inp.value = "";

  console.log("Aktyvus etapas:", curEtapas);
}

// ===== SCAN =====
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

// ===== HANDLE SCAN =====
async function handleScan(kodas) {

  if (!curEtapas) {
    alert("Pasirink etapą!");
    return;
  }

  console.log("SCAN:", kodas);

  const existing = lkOrders.find(o => o.kodas === kodas);

  // ===== EXISTING =====
  if (existing) {

    if (existing.delivered) {
      alert("Jau perduota");
      return;
    }

    if (existing.collected) {
      // PERDUOTI
      existing.delivered = true;

      try {
        await api('POST', '/api/lakstai/next_v2', {
          kodas: kodas,
          etapas: curEtapas === '__be_etapo__' ? null : curEtapas
        });
        console.log("PERDUOTA:", kodas);
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
      console.log("SURINKTA:", kodas);
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

    console.log("UŽREGISTRUOTA:", kodas);

  } catch (e) {
    lkOrders = lkOrders.filter(o => o.kodas !== kodas);
    alert("Klaida registruojant");
  }
}
