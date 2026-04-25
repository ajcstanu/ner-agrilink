"""models.py — SQLAlchemy ORM models for NER AgroLink."""

from database import db


class Shipment(db.Model):
    __tablename__ = "shipments"
    id      = db.Column(db.String(20), primary_key=True)
    route   = db.Column(db.String(100))
    produce = db.Column(db.String(50))
    weight  = db.Column(db.Integer)
    mode    = db.Column(db.String(30))
    status  = db.Column(db.String(20))
    eta     = db.Column(db.String(10))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class IoTReading(db.Model):
    __tablename__ = "iot_readings"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shipment_id = db.Column(db.String(20), db.ForeignKey("shipments.id"))
    farmer      = db.Column(db.String(80))
    village     = db.Column(db.String(80))
    route       = db.Column(db.String(120))
    produce     = db.Column(db.String(50))
    weight      = db.Column(db.Integer)
    mode        = db.Column(db.String(40))
    status      = db.Column(db.String(20))
    distance    = db.Column(db.String(15))
    eta         = db.Column(db.String(10))
    operator    = db.Column(db.String(60))
    temp        = db.Column(db.Float)
    humidity    = db.Column(db.Integer)
    vibration   = db.Column(db.Float)
    battery     = db.Column(db.Integer)
    solar       = db.Column(db.String(15))
    temp_status = db.Column(db.String(10))
    notes       = db.Column(db.Text)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Booking(db.Model):
    __tablename__ = "bookings"
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_name    = db.Column(db.String(80))
    village        = db.Column(db.String(100))
    produce        = db.Column(db.String(50))
    weight_kg      = db.Column(db.Float)
    pickup_date    = db.Column(db.String(20))
    phone          = db.Column(db.String(20))
    notes          = db.Column(db.Text)
    transport_mode = db.Column(db.String(30))
    status         = db.Column(db.String(20))
    created_at     = db.Column(db.String(40))

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d["booking_id"] = f"BK-{self.id:05d}"
        return d


class DashboardStat(db.Model):
    __tablename__ = "dashboard_stats"
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active_routes   = db.Column(db.Integer)
    kg_today        = db.Column(db.Integer)
    cost_avg_per_kg = db.Column(db.Float)
    spoilage_pct    = db.Column(db.Float)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
