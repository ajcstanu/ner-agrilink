#!/usr/bin/env python3
"""
init_db.py — Create and seed the NER AgroLink SQLite database.
Run once before starting the server:
    python database/init_db.py
"""

import sqlite3
import os

DB_PATH     = os.path.join(os.path.dirname(__file__), "ner_agrilink.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def init():
    print(f"[init_db] Creating database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("[init_db] Done — tables created and seed data inserted.")


if __name__ == "__main__":
    init()
