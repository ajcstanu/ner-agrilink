"""
tests.py — Pytest suite for NER AgroLink Flask backend
Run: pytest tests.py -v
"""

import os
import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app as flask_app, db, calculate_cost  # noqa: E402


@pytest.fixture(scope="module")
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with flask_app.app_context():
        db.create_all()
        from database import _seed
        _seed(db)
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Pure logic
# ---------------------------------------------------------------------------

class TestCalculateCost:
    def test_steep_recommends_cable(self):
        r = calculate_cost(500, 5, "steep", "veg")
        assert r["best_mode"] == "cable"

    def test_flat_recommends_trike(self):
        r = calculate_cost(300, 3, "flat", "veg")
        assert r["best_mode"] == "trike"

    def test_cost_math(self):
        r = calculate_cost(500, 5, "steep", "veg")
        assert r["per_kg"] == round(0.80 * 1.35 * 1.0, 2)
        assert r["total_cost"] == round(r["per_kg"] * 500)

    def test_spoil_low(self):
        assert calculate_cost(100, 0.5, "flat", "veg")["spoil_risk"] == "Low"

    def test_spoil_high(self):
        assert calculate_cost(100, 10, "extreme", "veg")["spoil_risk"] == "High"

    def test_alternatives_count(self):
        r = calculate_cost(300, 5, "steep", "veg")
        assert len(r["alternatives"]) == 3
        assert r["best_mode"] not in [a["mode_key"] for a in r["alternatives"]]

    def test_co2(self):
        r = calculate_cost(200, 4, "flat", "veg")
        assert r["co2_saved_kg"] == round(200 * 0.001 * 4 * 0.6, 1)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

class TestCalculateAPI:
    def test_defaults(self, client):
        r = client.get("/api/calculate")
        assert r.status_code == 200
        assert "total_cost" in r.get_json()

    def test_custom(self, client):
        r = client.get("/api/calculate?weight=320&distance=6.4&slope=steep&produce=veg")
        d = r.get_json()
        assert d["inputs"]["weight_kg"] == 320.0

    def test_bad_slope(self, client):
        assert client.get("/api/calculate?slope=cliff").status_code == 400

    def test_zero_weight(self, client):
        assert client.get("/api/calculate?weight=0").status_code == 400


class TestShipmentsAPI:
    def test_count(self, client):
        r = client.get("/api/shipments")
        assert r.status_code == 200
        assert r.get_json()["count"] == 8

    def test_fields(self, client):
        s = client.get("/api/shipments").get_json()["shipments"][0]
        for f in ("id", "route", "produce", "weight", "mode", "status", "eta"):
            assert f in s


class TestStatsAPI:
    def test_keys(self, client):
        d = client.get("/api/stats").get_json()
        for k in ("active_routes", "kg_today", "cost_avg_per_kg", "spoilage_pct"):
            assert k in d


class TestTrackerAPI:
    def test_known(self, client):
        r = client.get("/api/track/NER-2024-001")
        assert r.status_code == 200
        d = r.get_json()
        assert d["shipment_id"] == "NER-2024-001"
        assert "temp" in d and "humidity" in d and "spoilage_risk" in d

    def test_case_insensitive(self, client):
        assert client.get("/api/track/ner-2024-001").status_code == 200

    def test_unknown_404(self, client):
        r = client.get("/api/track/NER-9999-999")
        assert r.status_code == 404
        assert "hint" in r.get_json()


class TestBookingAPI:
    PAYLOAD = {
        "farmer_name": "Test Farmer",
        "village": "Ukhrul, Manipur",
        "produce": "veg",
        "weight_kg": 250,
        "pickup_date": "2024-07-15",
    }

    def test_valid(self, client):
        r = client.post("/api/booking", json=self.PAYLOAD)
        assert r.status_code == 201
        d = r.get_json()
        assert d["success"] is True
        assert d["booking_id"].startswith("BK-")

    def test_missing_field(self, client):
        p = dict(self.PAYLOAD)
        del p["farmer_name"]
        assert client.post("/api/booking", json=p).status_code == 400

    def test_no_body(self, client):
        assert client.post("/api/booking", data="x", content_type="text/plain").status_code == 400

    def test_stored_in_db(self, client):
        client.post("/api/booking", json=self.PAYLOAD)
        r = client.get("/api/bookings")
        assert r.get_json()["count"] >= 1


class TestHealthAPI:
    def test_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.get_json()["status"] == "ok"
