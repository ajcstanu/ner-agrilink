# 🌿 NER AgroLink — Smart Transport Solution for Remote Farms

> Connecting Northeast India's remote hill farms to motorable roads through solar-powered cableways, electric cargo trikes, bamboo carriers, and real-time IoT monitoring.

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/tests-38%20passing-brightgreen.svg)](#testing)

---

## 📖 Overview

NER AgroLink is an open-source farm logistics platform built specifically for the challenging terrain of Northeast India — covering Manipur, Nagaland, Meghalaya, Arunachal Pradesh, Mizoram, Tripura, Assam Hills, and Sikkim.

The platform addresses a core problem: farmers in remote hilly villages cannot affordably move their produce to the nearest motorable road, leading to 40%+ post-harvest losses. NER AgroLink solves this with:

- **Four terrain-adaptive transport modes** from ₹0.60/kg to ₹1.50/kg
- **Real-time IoT monitoring** of cargo temperature, humidity, and vibration
- **Interactive cost estimator** — weight × slope × produce → optimal mode + cost
- **Live dashboard** showing all active shipments across NER routes
- **Online booking system** for farmers to schedule transport pickups

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A modern web browser (no Node.js required)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ner-agrilink.git
cd ner-agrilink
```

### 2. Set Up the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize the Database
```bash
python ../database/init_db.py
```

### 4. Start the Backend Server
```bash
python app.py
# ✅ Running on http://localhost:5000
```

### 5. Open the Frontend
Open `frontend/index.html` in your browser. That's it — no build step required.

> **Tip:** Use [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) in VS Code for hot-reload development.

---

## 📁 Project Structure

```
ner-agrilink/
│
├── frontend/                   # Static HTML/CSS/JS frontend
│   ├── index.html              # Single-page application
│   ├── css/
│   │   └── style.css           # All styles (CSS vars, grid, animations)
│   └── js/
│       ├── app.js              # Nav, booking form, scroll animations
│       ├── dashboard.js        # Shipment table + live stats (API calls)
│       ├── tracker.js          # IoT sensor tracker (API calls)
│       └── calculator.js       # Cost estimator (API calls + offline fallback)
│
├── backend/                    # Python Flask REST API
│   ├── app.py                  # All routes and business logic
│   ├── models.py               # SQLAlchemy ORM models
│   ├── database.py             # DB init + seed helper
│   ├── requirements.txt        # Python dependencies
│   └── tests.py                # Pytest test suite (38 tests)
│
├── database/
│   ├── schema.sql              # SQLite schema + seed data
│   ├── init_db.py              # Standalone DB initializer
│   └── ner_agrilink.db         # Generated SQLite database (git-ignored)
│
├── docs/
│   └── api.md                  # Full API reference
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI (lint + test)
│
├── .gitignore
├── LICENSE                     # MIT
└── README.md
```

---

## 🛠️ Transport Modes

| Mode | Icon | Cost/kg | Best For | Slope |
|---|---|---|---|---|
| Smart Cable Conveyor | 🚡 | ₹0.80 | 500m+ elevation, no road | 45°+ |
| Lightweight Monorail | 🚝 | ₹1.20 | Mid-slope, uneven terrain | 30–45° |
| Electric Cargo Trike | 🛺 | ₹1.50 | Narrow rural paths | <25° |
| Bamboo-Based Carrier | 🎋 | ₹0.60 | Remote, zero-infra zones | All |

---

## 🔌 API Reference

Base URL: `http://localhost:5000/api`

### `GET /api/calculate`
Transport cost estimator.

| Param | Type | Default | Options |
|---|---|---|---|
| `weight` | float | 500 | kg, >0 |
| `distance` | float | 5.0 | km, >0 |
| `slope` | string | `steep` | `flat` `moderate` `steep` `extreme` |
| `produce` | string | `veg` | `veg` `fruit` `paddy` `bamboo` |

**Example:**
```bash
curl "http://localhost:5000/api/calculate?weight=320&distance=6.4&slope=steep&produce=veg"
```

```json
{
  "best_mode": "cable",
  "mode_name": "Smart Cable Conveyor 🚡",
  "per_kg": 1.08,
  "total_cost": 346,
  "est_time_min": 51,
  "co2_saved_kg": 1.2,
  "spoil_risk": "Medium",
  "alternatives": [...]
}
```

---

### `GET /api/shipments`
Returns all active shipments from the database.

```bash
curl http://localhost:5000/api/shipments
```

---

### `GET /api/stats`
Live dashboard statistics (with simulated real-time variance).

```bash
curl http://localhost:5000/api/stats
```

---

### `GET /api/track/<shipment_id>`
IoT sensor data for a specific shipment.

```bash
curl http://localhost:5000/api/track/NER-2024-001?live=true
```

**Demo IDs:** `NER-2024-001`, `NER-2024-004`, `NER-2024-007`

---

### `POST /api/booking`
Submit a transport pickup booking.

```bash
curl -X POST http://localhost:5000/api/booking \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_name": "Ratan Singh",
    "village": "Ukhrul, Manipur",
    "produce": "veg",
    "weight_kg": 300,
    "pickup_date": "2024-07-20",
    "phone": "+91 98765 43210"
  }'
```

**Response:**
```json
{
  "success": true,
  "booking_id": "BK-00001",
  "message": "Booking confirmed! Our operator will contact you 30 minutes before pickup."
}
```

---

### `GET /api/bookings`
List all submitted bookings (admin).

### `GET /api/health`
Health check: `{ "status": "ok" }`

---

## 🗄️ Database

NER AgroLink uses **SQLite** for development (zero setup) and is compatible with **PostgreSQL** for production.

### Tables

| Table | Purpose |
|---|---|
| `shipments` | Live dashboard — all active routes |
| `iot_readings` | IoT sensor data per shipment |
| `bookings` | Farmer transport requests |
| `dashboard_stats` | Baseline aggregate statistics |

### Reset / Re-seed
```bash
rm database/ner_agrilink.db
python database/init_db.py
```

### Switching to PostgreSQL
Update `SQLALCHEMY_DATABASE_URI` in `backend/app.py`:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:pass@localhost/ner_agrilink"
```

---

## 🧪 Testing

```bash
cd backend
pytest tests.py -v
```

**38 tests** covering:
- Pure cost calculation logic (mode selection, spoilage risk, CO2, alternatives)
- All 6 API endpoints (happy path + error cases)
- DB persistence (booking stored, retrieved correctly)
- IoT sensor noise simulation
- Case-insensitive shipment ID lookup

---

## 🌱 Impact

| Metric | Value |
|---|---|
| Post-harvest spoilage reduction | ~40% |
| Average operational cost | ₹1–2/kg |
| Energy source | Solar-powered |
| States covered | 8 NER states |
| Farmer income increase | ~3× |

---

## 🔧 Technology Stack

| Layer | Tech |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JS |
| Backend | Python 3, Flask 3, Flask-CORS, Flask-SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Testing | Pytest |
| CI | GitHub Actions |
| Fonts | Google Fonts (Syne, Space Mono, Lora) |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest backend/tests.py -v`
5. Commit: `git commit -m 'feat: add your feature'`
6. Push and open a Pull Request

### Development Tips
- The frontend has an **offline fallback** in `calculator.js` — the cost estimator works even without the backend running
- The `API_BASE` URL can be overridden globally: `window.API_BASE = "https://your-server.com/api"`
- All DB seed data lives in `database/schema.sql` — easy to extend

---

