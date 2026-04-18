// ===== API helper =====
async function api(method, url, data) {
  const r = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: data ? JSON.stringify(data) : undefined
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// ===== GLOBAL =====
let lkOrders = [];
let curEtapas = null;

// ===== SCAN INPUT =====
const scanInp = document.getElementById('scanInp');

if (scanInp) {
  scanInp.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
      const kodas = scanInp.value.trim();
      if (!kodas) return;

      scanInp.value = "";
      await handleScan(kodas);
    }
  });
}

// ===== HANDLE SCAN =====
async function handleScan(kodas) {
  if (!curEtapas) {
    alert("Pasirink etapą");
    return;
  }

  const existing = lkOrders.find(o => o.kodas === kodas);

  // ===== JAU YRA =====
  if (existing) {

    // PERDUOTA
    if (existing.delivered) {
      alert("Jau perduota");
      return;
    }

    // SURINKTA → PERDUOTI
    if (existing.collected) {
      existing.delivered = true;

      try {
        await api('POST', '/api/lakstai/next_v2', {
          kodas,
          etapas: curEtapas === '__be_etapo__' ? null : curEtapas
        });
      } catch (e) {
        existing.delivered = false;
        alert("Klaida perduodant");
      }

      return;
    }

    // REGISTRUOTA → SURINKTI
    existing.collected = true;

    try {
      await api('POST', '/api/lakstai/next_v2', {
        kodas,
        etapas: curEtapas === '__be_etapo__' ? null : curEtapas
      });
    } catch (e) {
      existing.collected = false;
      alert("Klaida surenkant");
    }

    return;
  }

  // ===== NAUJAS =====
  const newItem = {
    kodas,
    collected: false,
    delivered: false,
    etapas: curEtapas
  };

  lkOrders.push(newItem);

  try {
    await api('POST', '/api/lakstai/register_v2', {
      kodas,
      etapas: curEtapas === '__be_etapo__' ? null : curEtapas
    });
  } catch (e) {
    lkOrders = lkOrders.filter(o => o.kodas !== kodas);
    alert("Klaida registruojant");
  }
}
