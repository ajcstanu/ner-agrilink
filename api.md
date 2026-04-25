# NER AgroLink — API Reference

## Base URL
```
http://localhost:5000/api
```

All responses are JSON. All errors return `{ "error": "message" }`.

---

## Endpoints

### `GET /api/health`
Service health check.

**Response 200:**
```json
{ "status": "ok", "service": "NER AgroLink API", "version": "1.0.0" }
```

---

### `GET /api/calculate`
Returns recommended transport mode, cost estimate, time, CO2, and spoilage risk.

**Query Parameters:**

| Param | Required | Type | Default | Values |
|---|---|---|---|---|
| `weight` | No | float | 500 | kg, must be > 0 |
| `distance` | No | float | 5.0 | km, must be > 0 |
| `slope` | No | string | `steep` | `flat` `moderate` `steep` `extreme` |
| `produce` | No | string | `veg` | `veg` `fruit` `paddy` `bamboo` |

**Response 200:**
```json
{
  "best_mode": "cable",
  "mode_name": "Smart Cable Conveyor 🚡",
  "per_kg": 1.08,
  "total_cost": 346,
  "est_time_min": 51,
  "co2_saved_kg": 1.2,
  "spoil_risk": "Medium",
  "alternatives": [
    { "mode_key": "mono",   "mode_name": "Lightweight Monorail 🚝",  "total_cost": 519, "per_kg": 1.62 },
    { "mode_key": "trike",  "mode_name": "Electric Cargo Trike 🛺",   "total_cost": 648, "per_kg": 2.03 },
    { "mode_key": "bamboo", "mode_name": "Bamboo Carrier 🎋",          "total_cost": 259, "per_kg": 0.81 }
  ],
  "inputs": { "weight_kg": 320.0, "distance_km": 6.4, "slope": "steep", "produce": "veg" }
}
```

**Errors:** `400` if slope or produce value is invalid, or weight/distance ≤ 0.

---

### `GET /api/shipments`
Returns all active shipments from the database.

**Response 200:**
```json
{
  "count": 8,
  "fetched_at": "2024-07-15T10:30:00",
  "shipments": [
    {
      "id": "NER-2024-001",
      "route": "Ukhrul → NH-2",
      "produce": "Tomatoes",
      "weight": 320,
      "mode": "🚡 Cable",
      "status": "transit",
      "eta": "14:35"
    }
  ]
}
```

**Status values:** `transit` | `arrived` | `loading`

---

### `GET /api/stats`
Live dashboard statistics. Values include simulated real-time variance on each call.

**Response 200:**
```json
{
  "active_routes": 13,
  "kg_today": 4412,
  "cost_avg_per_kg": 1.14,
  "spoilage_pct": 2.8,
  "fetched_at": "2024-07-15T10:30:05"
}
```

---

### `GET /api/track/<shipment_id>`
Returns IoT sensor readings for a shipment. Sensor values vary slightly on each call (simulates live hardware).

**Path parameter:** `shipment_id` — case-insensitive (e.g. `NER-2024-001`)

**Demo IDs:** `NER-2024-001`, `NER-2024-004`, `NER-2024-007`

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `live` | bool | `false` | Add sensor noise to simulate real-time hardware |

**Response 200:**
```json
{
  "shipment_id": "NER-2024-001",
  "farmer": "Kh. Rameshwar Singh",
  "village": "Ukhrul, Manipur",
  "route": "Ukhrul Farm → NH-2 Collection Point",
  "produce": "Tomatoes",
  "weight": 320,
  "mode": "Smart Cable Conveyor",
  "status": "In Transit",
  "distance": "6.4 km",
  "eta": "14:35",
  "operator": "Ratan Meitei",
  "temp": 12.2,
  "humidity": 71,
  "vibration": 0.28,
  "battery": 83,
  "solar": "Active",
  "temp_status": "ok",
  "notes": "Optimal cold chain maintained.",
  "spoilage_risk": "LOW",
  "last_updated": "10:30:07"
}
```

**`temp_status` values:** `ok` | `warn` | `bad`  
**`spoilage_risk` values:** `LOW` | `MEDIUM`

**Error 404:**
```json
{
  "error": "Shipment 'NER-9999-999' not found.",
  "hint": "Try NER-2024-001, NER-2024-004, or NER-2024-007"
}
```

---

### `POST /api/booking`
Submit a new transport pickup booking.

**Request Body (JSON):**

| Field | Required | Type | Description |
|---|---|---|---|
| `farmer_name` | Yes | string | Full name of farmer |
| `village` | Yes | string | Village, District, State |
| `produce` | Yes | string | Produce type |
| `weight_kg` | Yes | float | Estimated weight in kg |
| `pickup_date` | Yes | string | Preferred date (YYYY-MM-DD) |
| `phone` | No | string | Contact number |
| `notes` | No | string | Special instructions |
| `transport_mode` | No | string | Preferred mode (default: `system_recommended`) |

**Response 201:**
```json
{
  "success": true,
  "booking_id": "BK-00001",
  "message": "Booking confirmed! Our operator will contact you 30 minutes before pickup.",
  "details": {
    "id": 1,
    "booking_id": "BK-00001",
    "farmer_name": "Ratan Singh",
    "village": "Ukhrul, Manipur",
    "produce": "veg",
    "weight_kg": 300.0,
    "pickup_date": "2024-07-20",
    "phone": "+91 98765 43210",
    "transport_mode": "system_recommended",
    "status": "confirmed",
    "created_at": "2024-07-15T10:30:00"
  }
}
```

**Error 400:** Missing required fields or invalid JSON body.

---

### `GET /api/bookings`
List all submitted bookings (admin view).

**Response 200:**
```json
{
  "count": 3,
  "bookings": [ ... ]
}
```
