// calculator.js — Transport Cost Estimator for NER AgroLink
// Calls Flask API: GET /api/calculate

const API_BASE = window.API_BASE || "http://localhost:5000/api";

async function calcCost() {
  const weight   = +document.getElementById("weight").value;
  const distance = +document.getElementById("distance").value;
  const slope    = document.getElementById("slope").value;
  const produce  = document.getElementById("produce").value;
  document.getElementById("weight-val").textContent = weight + " kg";
  document.getElementById("dist-val").textContent   = distance + " km";
  try {
    const res  = await fetch(
      `${API_BASE}/calculate?weight=${weight}&distance=${distance}&slope=${slope}&produce=${produce}`
    );
    const data = await res.json();

    document.getElementById("result-mode").textContent  = "Recommended: " + data.mode_name;
    document.getElementById("cost-total").textContent   = "₹" + data.total_cost.toLocaleString();
    document.getElementById("per-kg").textContent       = "₹" + data.per_kg;
    document.getElementById("est-time").textContent     = data.est_time_min + " min";
    document.getElementById("co2").textContent          = data.co2_saved_kg + " kg";

    const spoilEl = document.getElementById("spoil-risk");
    spoilEl.textContent = data.spoil_risk;
    spoilEl.className   = data.spoil_risk === "Low" ? "risk-low" : data.spoil_risk === "Medium" ? "risk-med" : "risk-high";

    document.getElementById("alt-modes").innerHTML =
      '<strong style="color:var(--text-muted);font-size:0.7rem">ALTERNATIVES:</strong><br>' +
      data.alternatives.map(a => `${a.mode_name}: ₹${a.total_cost.toLocaleString()}`).join("<br>");

  } catch {
    // Fallback: run calculation client-side if API unreachable
    _calcCostLocal(weight, distance, slope, produce);
  }
}
// Offline fallback (mirrors backend logic exactly)
const _MODE = { cable:{base:0.80,name:"Smart Cable Conveyor 🚡",tpk:8}, mono:{base:1.20,name:"Lightweight Monorail 🚝",tpk:10}, trike:{base:1.50,name:"Electric Cargo Trike 🛺",tpk:12}, bamboo:{base:0.60,name:"Bamboo Carrier 🎋",tpk:20} };
const _SM   = { flat:1.0, moderate:1.15, steep:1.35, extreme:1.6 };
const _PM   = { veg:1.0, fruit:1.1, paddy:0.9, bamboo:0.85 };
const _BEST = { flat:"trike", moderate:"mono", steep:"cable", extreme:"cable" };

function _calcCostLocal(weight, distance, slope, produce) {
  const bk  = _BEST[slope] || "cable";
  const md  = _MODE[bk];
  const pk  = +( md.base * _SM[slope] * _PM[produce] ).toFixed(2);
  const tot = Math.round(pk * weight);
  const et  = Math.round(md.tpk * distance);
  const co2 = +(weight * 0.001 * distance * 0.6).toFixed(1);
  const sr  = et < 30 ? "Low" : et < 60 ? "Medium" : "High";
  document.getElementById("result-mode").textContent = "Recommended: " + md.name;
  document.getElementById("cost-total").textContent  = "₹" + tot.toLocaleString();
  document.getElementById("per-kg").textContent      = "₹" + pk;
  document.getElementById("est-time").textContent    = et + " min";
  document.getElementById("co2").textContent         = co2 + " kg";
  const se = document.getElementById("spoil-risk");
  se.textContent = sr; se.className = sr === "Low" ? "risk-low" : sr === "Medium" ? "risk-med" : "risk-high";
  document.getElementById("alt-modes").innerHTML =
    '<strong style="color:var(--text-muted);font-size:0.7rem">ALTERNATIVES (offline):</strong><br>' +
    Object.entries(_MODE).filter(([k]) => k !== bk)
      .map(([,v]) => `${v.name}: ₹${Math.round(v.base * _SM[slope] * _PM[produce] * weight).toLocaleString()}`).join("<br>");
}
document.addEventListener("DOMContentLoaded", calcCost);
