-- ============================================================
-- NER AgroLink — Database Schema
-- SQLite (dev) | compatible with PostgreSQL (prod)
-- ============================================================

PRAGMA foreign_keys = ON;

-- Shipments: live dashboard table
CREATE TABLE IF NOT EXISTS shipments (
    id      TEXT    PRIMARY KEY,          -- e.g. NER-2024-001
    route   TEXT    NOT NULL,
    produce TEXT    NOT NULL,
    weight  INTEGER NOT NULL,
    mode    TEXT    NOT NULL,
    status  TEXT    NOT NULL DEFAULT 'loading',  -- transit | arrived | loading
    eta     TEXT
);

-- IoT sensor readings: one row per shipment (latest reading)
CREATE TABLE IF NOT EXISTS iot_readings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id TEXT    NOT NULL REFERENCES shipments(id),
    farmer      TEXT,
    village     TEXT,
    route       TEXT,
    produce     TEXT,
    weight      INTEGER,
    mode        TEXT,
    status      TEXT,
    distance    TEXT,
    eta         TEXT,
    operator    TEXT,
    temp        REAL,
    humidity    INTEGER,
    vibration   REAL,
    battery     INTEGER,
    solar       TEXT,
    temp_status TEXT    DEFAULT 'ok',   -- ok | warn | bad
    notes       TEXT
);

-- Bookings: submitted transport requests
CREATE TABLE IF NOT EXISTS bookings (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_name    TEXT    NOT NULL,
    village        TEXT    NOT NULL,
    produce        TEXT    NOT NULL,
    weight_kg      REAL    NOT NULL,
    pickup_date    TEXT    NOT NULL,
    phone          TEXT,
    notes          TEXT,
    transport_mode TEXT    DEFAULT 'system_recommended',
    status         TEXT    DEFAULT 'confirmed',
    created_at     TEXT
);

-- Dashboard stats: snapshot for baseline display
CREATE TABLE IF NOT EXISTS dashboard_stats (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    active_routes   INTEGER,
    kg_today        INTEGER,
    cost_avg_per_kg REAL,
    spoilage_pct    REAL
);

-- ============================================================
-- Seed data
-- ============================================================

INSERT OR IGNORE INTO shipments VALUES
('NER-2024-001','Ukhrul → NH-2',       'Tomatoes',    320,'🚡 Cable',   'transit','14:35'),
('NER-2024-002','Senapati → NH-37',    'Paddy',        800,'🚝 Monorail','arrived','13:50'),
('NER-2024-003','Mawsynram → NH-6',    'Ginger',       150,'🛺 Trike',   'loading','15:20'),
('NER-2024-004','Phek → NH-29',        'Cabbage',      420,'🎋 Bamboo',  'transit','16:00'),
('NER-2024-005','Tamenglong → NH-37',  'Banana',       600,'🚡 Cable',   'arrived','13:10'),
('NER-2024-006','Longding → NH-415',   'Orange',       280,'🛺 Trike',   'transit','15:45'),
('NER-2024-007','Ri Bhoi → NH-6',      'Bamboo Shoot', 500,'🎋 Bamboo',  'loading','17:00'),
('NER-2024-008','Churachandpur → NH-2','Chilli',        180,'🚝 Monorail','transit','14:55');

INSERT OR IGNORE INTO iot_readings
  (shipment_id,farmer,village,route,produce,weight,mode,status,distance,eta,operator,temp,humidity,vibration,battery,solar,temp_status,notes)
VALUES
('NER-2024-001','Kh. Rameshwar Singh','Ukhrul, Manipur',
 'Ukhrul Farm → NH-2','Tomatoes',320,'Smart Cable Conveyor','In Transit','6.4 km','14:35','Ratan Meitei',
 12.4,72,0.3,84,'Active','ok','Optimal cold chain maintained.'),
('NER-2024-004','Vizokho Khruomo','Phek, Nagaland',
 'Phek Hill Farm → NH-29 Road','Cabbage',420,'Bamboo Carrier','In Transit','4.1 km','16:00','Vizol Sangtam',
 16.8,65,0.6,72,'Active','ok','Slight vibration spike over rocky section — within limits.'),
('NER-2024-007','Pynbait Nongkynmaw','Ri Bhoi, Meghalaya',
 'Mawphlang Farm → NH-6','Bamboo Shoots',500,'Electric Cargo Trike','Loading','3.2 km','17:00','Baiakmenlang Lyngdoh',
 22.1,88,0.1,91,'Charging','warn','Temperature slightly elevated. Recommend shading.');

INSERT OR IGNORE INTO dashboard_stats (active_routes, kg_today, cost_avg_per_kg, spoilage_pct)
VALUES (12, 4280, 1.12, 3.2);
