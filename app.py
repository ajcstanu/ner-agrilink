"""
NER AgroLink — Flask Backend
Smart Transport Solution for Remote Farms (Northeast India)
"""
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from database import db, init_db
from models import Shipment, Booking, IoTReading, DashboardStat
import random
from datetime import datetime
import os as _os

app = Flask(__name__)
_default_db = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "database", "ner_agrilink.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = _os.environ.get("DATABASE_URL", f"sqlite:///{_default_db}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)

# ---------------------------------------------------------------------------
# Transport logic constants
# ---------------------------------------------------------------------------

MODE_COSTS = {
    "cable":  {"base": 0.80, "name": "Smart Cable Conveyor 🚡", "time_per_km": 8},
    "mono":   {"base": 1.20, "name": "Lightweight Monorail 🚝",  "time_per_km": 10},
    "trike":  {"base": 1.50, "name": "Electric Cargo Trike 🛺",  "time_per_km": 12},
    "bamboo": {"base": 0.60, "name": "Bamboo Carrier 🎋",         "time_per_km": 20},
}
SLOPE_MULTIPLIER = {"flat": 1.0, "moderate": 1.15, "steep": 1.35, "extreme": 1.6}
PRODUCE_MULT     = {"veg": 1.0, "fruit": 1.1, "paddy": 0.9, "bamboo": 0.85}
SLOPE_BEST_MODE  = {"flat": "trike", "moderate": "mono", "steep": "cable", "extreme": "cable"}

def calculate_cost(weight, distance, slope, produce):
    best = SLOPE_BEST_MODE.get(slope, "cable")
    mode = MODE_COSTS[best]
    sm   = SLOPE_MULTIPLIER[slope]
    pm   = PRODUCE_MULT[produce]
    per_kg     = round(mode["base"] * sm * pm, 2)
    total      = round(per_kg * weight)
    est_time   = round(mode["time_per_km"] * distance)
    co2        = round(weight * 0.001 * distance * 0.6, 1)
    spoil_risk = "Low" if est_time < 30 else ("Medium" if est_time < 60 else "High")
    alternatives = [
        {"mode_key": k, "mode_name": v["name"],
         "total_cost": round(v["base"] * sm * pm * weight),
         "per_kg": round(v["base"] * sm * pm, 2)}
        for k, v in MODE_COSTS.items() if k != best
    ]
    return dict(best_mode=best, mode_name=mode["name"], per_kg=per_kg,
                total_cost=total, est_time_min=est_time,
                co2_saved_kg=co2, spoil_risk=spoil_risk, alternatives=alternatives)

# ---------------------------------------------------------------------------
# Routes — Calculator
# ---------------------------------------------------------------------------
@app.route("/api/calculate", methods=["GET"])
def api_calculate():
    """
    GET /api/calculate?weight=500&distance=5&slope=steep&produce=veg
    Returns cost estimate, recommended mode, spoilage risk, CO2 saved.
    """
    try:
        weight   = float(request.args.get("weight", 500))
        distance = float(request.args.get("distance", 5.0))
    except ValueError:
        abort(400, "weight and distance must be numbers.")
    slope   = request.args.get("slope", "steep").lower()
    produce = request.args.get("produce", "veg").lower()
    if slope not in SLOPE_MULTIPLIER:
        abort(400, f"slope must be one of {list(SLOPE_MULTIPLIER)}")
    if produce not in PRODUCE_MULT:
        abort(400, f"produce must be one of {list(PRODUCE_MULT)}")
    if weight <= 0 or distance <= 0:
        abort(400, "weight and distance must be positive.")
    result = calculate_cost(weight, distance, slope, produce)
    result["inputs"] = dict(weight_kg=weight, distance_km=distance, slope=slope, produce=produce)
    return jsonify(result)

# ---------------------------------------------------------------------------
# Routes — Dashboard
# ---------------------------------------------------------------------------

@app.route("/api/shipments", methods=["GET"])
def api_shipments():
    """GET /api/shipments  — returns all shipments from DB."""
    rows = Shipment.query.order_by(Shipment.id).all()
    return jsonify({"count": len(rows), "shipments": [s.to_dict() for s in rows],
                    "fetched_at": datetime.utcnow().isoformat()})


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """GET /api/stats  — live dashboard aggregate stats."""
    stat = DashboardStat.query.order_by(DashboardStat.id.desc()).first()
    if stat:
        data = stat.to_dict()
    else:
        data = dict(active_routes=12, kg_today=4280, cost_avg_per_kg=1.12, spoilage_pct=3.2)
    # Add simulated live variance
    data["active_routes"]    = random.randint(10, 15)
    data["kg_today"]         = random.randint(4000, 4800)
    data["cost_avg_per_kg"]  = round(1.05 + random.uniform(0, 0.20), 2)
    data["spoilage_pct"]     = round(2.0  + random.uniform(0, 2.0),  1)
    data["fetched_at"]       = datetime.utcnow().isoformat()
    return jsonify(data)

# ---------------------------------------------------------------------------
# Routes — IoT Tracker
# ---------------------------------------------------------------------------

@app.route("/api/track/<shipment_id>", methods=["GET"])
def api_track(shipment_id):
    """GET /api/track/NER-2024-001  — returns IoT sensor readings."""
    sid    = shipment_id.upper()
    latest = (IoTReading.query
              .filter_by(shipment_id=sid)
              .order_by(IoTReading.id.desc())
              .first())
    if not latest:
        return jsonify({"error": f"Shipment '{sid}' not found.",
                        "hint": "Try NER-2024-001, NER-2024-004, or NER-2024-007"}), 404
    data = latest.to_dict()
    # Simulate live sensor noise on each call
    data["temp"]        = round(data["temp"]        + random.uniform(-0.4, 0.4), 1)
    data["humidity"]    = min(100, max(0, data["humidity"]    + random.randint(-2, 2)))
    data["vibration"]   = round(max(0, data["vibration"]      + random.uniform(-0.05, 0.05)), 2)
    data["battery"]     = min(100, max(0, data["battery"]     + random.randint(-1, 1)))
    data["last_updated"] = datetime.utcnow().strftime("%H:%M:%S")
    data["spoilage_risk"] = "LOW" if data["temp_status"] == "ok" else "MEDIUM"
    return jsonify(data)
# ---------------------------------------------------------------------------
# Routes — Booking
# ---------------------------------------------------------------------------

@app.route("/api/booking", methods=["POST"])
def api_booking():
    """
    POST /api/booking
    Body: { farmer_name, village, produce, weight_kg, pickup_date, phone?, notes?, transport_mode? }
    """
    body = request.get_json(silent=True)
    if not body:
        abort(400, "Request body must be JSON.")
    required = ["farmer_name", "village", "produce", "weight_kg", "pickup_date"]
    missing  = [f for f in required if f not in body]
    if missing:
        abort(400, f"Missing required fields: {missing}")

    booking = Booking(
        farmer_name    = body["farmer_name"],
        village        = body["village"],
        produce        = body["produce"],
        weight_kg      = float(body["weight_kg"]),
        pickup_date    = body["pickup_date"],
        phone          = body.get("phone", ""),
        notes          = body.get("notes", ""),
        transport_mode = body.get("transport_mode", "system_recommended"),
        status         = "confirmed",
        created_at     = datetime.utcnow().isoformat(),
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify({
        "success": True,
        "booking_id": f"BK-{booking.id:05d}",
        "message": "Booking confirmed! Our operator will contact you 30 minutes before pickup.",
        "details": booking.to_dict(),
    }), 201


@app.route("/api/bookings", methods=["GET"])
def api_bookings():
    """GET /api/bookings  — list all bookings (admin view)."""
    rows = Booking.query.order_by(Booking.id.desc()).all()
    return jsonify({"count": len(rows), "bookings": [b.to_dict() for b in rows]})

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "NER AgroLink API", "version": "1.0.0"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
