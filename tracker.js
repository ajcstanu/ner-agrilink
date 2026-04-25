// tracker.js — IoT Cargo Condition Tracker for NER AgroLink
// Fetches live sensor data from Flask API: GET /api/track/<id>

const API_BASE = window.API_BASE || "http://localhost:5000/api";

async function trackShipment() {
  const id = document.getElementById("track-id").value.trim().toUpperCase();
  if (!id) return;
  displayShipment(id);
}

function loadSample(id) {
  document.getElementById("track-id").value = id;
  displayShipment(id);
}

async function displayShipment(id) {
  const result = document.getElementById("tracker-result");
  result.innerHTML = `<div class="tracker-placeholder"><span>⏳</span><p>Loading ${id}…</p></div>`;

  let data;
  try {
    const res = await fetch(`${API_BASE}/track/${id}?live=true`);
    if (!res.ok) {
      const err = await res.json();
      result.innerHTML = `
        <div class="tracker-placeholder">
          <span>❌</span>
          <p>${err.error}<br/><small style="color:var(--text-muted)">${err.hint}</small></p>
        </div>`;
      return;
    }
    data = await res.json();
  } catch {
    result.innerHTML = `<div class="tracker-placeholder"><span>⚠️</span><p>API unreachable. Is the backend running?</p></div>`;
    return;
  }

  const tempClass = data.temp_status === "ok" ? "temp-ok" : data.temp_status === "warn" ? "temp-warn" : "temp-bad";
  const tempIcon  = data.temp_status === "ok" ? "✅" : "⚠️";

  result.innerHTML = `
    <div class="tracker-data">
      <div class="tracker-info">
        <h4>📦 ${data.shipment_id} — ${data.produce}</h4>
        <div class="info-row"><span>Farmer</span><span>${data.farmer}</span></div>
        <div class="info-row"><span>Village</span><span>${data.village}</span></div>
        <div class="info-row"><span>Route</span><span>${data.route}</span></div>
        <div class="info-row"><span>Transport Mode</span><span>${data.mode}</span></div>
        <div class="info-row"><span>Weight</span><span>${data.weight} kg</span></div>
        <div class="info-row"><span>Distance</span><span>${data.distance}</span></div>
        <div class="info-row"><span>Status</span><span style="color:var(--gold)">${data.status}</span></div>
        <div class="info-row"><span>ETA</span><span>${data.eta}</span></div>
        <div class="info-row"><span>Operator</span><span>${data.operator}</span></div>
        <div style="margin-top:12px;font-size:0.78rem;color:var(--text-muted);font-family:var(--font-mono)">
          ${tempIcon} ${data.notes}
        </div>
      </div>
      <div>
        <h4 style="font-family:var(--font-display);font-size:1rem;font-weight:700;margin-bottom:16px;color:var(--gold)">📡 Live IoT Sensors</h4>
        <div class="sensor-grid">
          <div class="sensor-card"><div class="sensor-label">Temperature</div>
            <div class="sensor-val ${tempClass}">${data.temp}°C</div></div>
          <div class="sensor-card"><div class="sensor-label">Humidity</div>
            <div class="sensor-val" style="color:var(--sky)">${data.humidity}%</div></div>
          <div class="sensor-card"><div class="sensor-label">Vibration (g)</div>
            <div class="sensor-val" style="color:${data.vibration < 0.5 ? '#81c784' : '#f4c542'}">${data.vibration}</div></div>
          <div class="sensor-card"><div class="sensor-label">Battery</div>
            <div class="sensor-val" style="color:var(--green-leaf)">${data.battery}%</div></div>
          <div class="sensor-card"><div class="sensor-label">Solar Status</div>
            <div class="sensor-val" style="font-size:1rem;color:var(--gold)">${data.solar}</div></div>
          <div class="sensor-card"><div class="sensor-label">Spoilage Risk</div>
            <div class="sensor-val" style="font-size:1rem;color:${data.spoilage_risk === 'LOW' ? '#81c784' : '#f4c542'}">${data.spoilage_risk}</div></div>
        </div>
        <div style="margin-top:16px;font-family:var(--font-mono);font-size:0.7rem;color:var(--text-muted)">
          Last updated: ${data.last_updated} · Auto-refreshes every 30s
        </div>
      </div>
    </div>`;

  // Auto-refresh sensor data every 30s
  if (window._trackerInterval) clearInterval(window._trackerInterval);
  window._trackerInterval = setInterval(() => displayShipment(id), 30000);
}
