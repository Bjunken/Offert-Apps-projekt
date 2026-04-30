import sqlite3
import json
import os
import sys


def get_db_path():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "app.db")


class Service:
    def __init__(self, id, name, price, price_type, description, materials):
        self.id          = id
        self.name        = name
        self.price       = price
        self.price_type  = price_type
        self.description = description
        self.materials   = materials or []


def create_table():
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT,
        price       REAL,
        price_type  TEXT,
        description TEXT,
        materials   TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_service(name, price, price_type, description, materials):
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("""
    INSERT INTO services (name, price, price_type, description, materials)
    VALUES (?, ?, ?, ?, ?)
    """, (name, price, price_type, description, json.dumps(materials)))

    conn.commit()
    conn.close()


def get_services():
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("SELECT * FROM services")
    rows = c.fetchall()
    conn.close()

    return [
        Service(
            id          = r[0],
            name        = r[1],
            price       = r[2],
            price_type  = r[3],
            description = r[4],
            materials   = json.loads(r[5]) if r[5] else []
        )
        for r in rows
    ]


def update_service(id, name, price, price_type, description, materials):
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("""
    UPDATE services
    SET name=?, price=?, price_type=?, description=?, materials=?
    WHERE id=?
    """, (name, price, price_type, description, json.dumps(materials), id))

    conn.commit()
    conn.close()


def delete_service(service_id):
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("DELETE FROM services WHERE id=?", (service_id,))

    conn.commit()
    conn.close()