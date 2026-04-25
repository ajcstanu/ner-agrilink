"""database.py — SQLAlchemy instance and init helper."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Create all tables and seed demo data if empty."""
    from models import Shipment, IoTReading, Booking, DashboardStat
    with app.app_context():
        db.create_all()
        _seed(db)


def _seed(db):
    from models import Shipment, IoTReading, DashboardStat

    if Shipment.query.first():
        return  # already seeded

    shipments = [
        Shipment(id="NER-2024-001", route="Ukhrul → NH-2",        produce="Tomatoes",    weight=320, mode="🚡 Cable",    status="transit", eta="14:35"),
        Shipment(id="NER-2024-002", route="Senapati → NH-37",      produce="Paddy",        weight=800, mode="🚝 Monorail", status="arrived", eta="13:50"),
        Shipment(id="NER-2024-003", route="Mawsynram → NH-6",      produce="Ginger",       weight=150, mode="🛺 Trike",    status="loading", eta="15:20"),
        Shipment(id="NER-2024-004", route="Phek → NH-29",          produce="Cabbage",      weight=420, mode="🎋 Bamboo",   status="transit", eta="16:00"),
        Shipment(id="NER-2024-005", route="Tamenglong → NH-37",    produce="Banana",       weight=600, mode="🚡 Cable",    status="arrived", eta="13:10"),
        Shipment(id="NER-2024-006", route="Longding → NH-415",     produce="Orange",       weight=280, mode="🛺 Trike",    status="transit", eta="15:45"),
        Shipment(id="NER-2024-007", route="Ri Bhoi → NH-6",        produce="Bamboo Shoot", weight=500, mode="🎋 Bamboo",   status="loading", eta="17:00"),
        Shipment(id="NER-2024-008", route="Churachandpur → NH-2",  produce="Chilli",       weight=180, mode="🚝 Monorail", status="transit", eta="14:55"),
    ]
    db.session.add_all(shipments)

    iot = [
        IoTReading(shipment_id="NER-2024-001", farmer="Kh. Rameshwar Singh", village="Ukhrul, Manipur",
                   route="Ukhrul Farm → NH-2", produce="Tomatoes", weight=320, mode="Smart Cable Conveyor",
                   status="In Transit", distance="6.4 km", eta="14:35", operator="Ratan Meitei",
                   temp=12.4, humidity=72, vibration=0.3, battery=84, solar="Active",
                   temp_status="ok", notes="Optimal cold chain maintained."),
        IoTReading(shipment_id="NER-2024-004", farmer="Vizokho Khruomo", village="Phek, Nagaland",
                   route="Phek Hill Farm → NH-29 Road", produce="Cabbage", weight=420, mode="Bamboo Carrier",
                   status="In Transit", distance="4.1 km", eta="16:00", operator="Vizol Sangtam",
                   temp=16.8, humidity=65, vibration=0.6, battery=72, solar="Active",
                   temp_status="ok", notes="Slight vibration spike over rocky section — within limits."),
        IoTReading(shipment_id="NER-2024-007", farmer="Pynbait Nongkynmaw", village="Ri Bhoi, Meghalaya",
                   route="Mawphlang Farm → NH-6", produce="Bamboo Shoots", weight=500, mode="Electric Cargo Trike",
                   status="Loading", distance="3.2 km", eta="17:00", operator="Baiakmenlang Lyngdoh",
                   temp=22.1, humidity=88, vibration=0.1, battery=91, solar="Charging",
                   temp_status="warn", notes="Temperature slightly elevated. Recommend shading."),
    ]
    db.session.add_all(iot)

    db.session.add(DashboardStat(active_routes=12, kg_today=4280, cost_avg_per_kg=1.12, spoilage_pct=3.2))
    db.session.commit()
