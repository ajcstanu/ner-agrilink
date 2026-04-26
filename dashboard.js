// dashboard.js — Live shipment dashboard for NER AgroLink
// Fetches data from Flask API: GET /api/shipments and GET /api/stats
const API_BASE = window.API_BASE || "http://localhost:5000/api";
function renderShipments(data) {
  const tbody = document.getElementById("shipment-body");
  if (!tbody) return;
  tbody.innerHTML = data.map(s => `
    <tr>
      <td style="color:var(--sky);font-weight:700">${s.id}</td>
      <td>${s.route}</td>
      <td>${s.produce}</td>
      <td>${s.weight}</td>
      <td>${s.mode}</td>
      <td><span class="status-badge status-${s.status}">${s.status.toUpperCase()}</span></td>
      <td style="color:var(--gold)">${s.eta}</td>
    </tr>
  `).join("");
}

async function refreshShipments() {
  try {
    const res  = await fetch(`${API_BASE}/shipments`);
    const data = await res.json();
    renderShipments(data.shipments);
  } catch {
    console.warn("Could not reach API — showing cached data.");
  }
}

async function refreshStats() {
  try {
    const res  = await fetch(`${API_BASE}/stats`);
    const data = await res.json();
    const set  = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set("active-routes", data.active_routes);
    set("kg-today",      data.kg_today.toLocaleString());
    set("cost-avg",      "₹" + data.cost_avg_per_kg);
    set("spoilage",      data.spoilage_pct + "%");
  } catch {
    console.warn("Stats fetch failed.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  refreshShipments();
  refreshStats();
  setInterval(refreshStats,    5000);
  setInterval(refreshShipments, 15000);
});
