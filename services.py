import sqlite3
import json

DB = "app.db"


# 📦 Datamodell
class Service:
    def __init__(self, id, name, price, price_type, description, materials):
        self.id = id
        self.name = name
        self.price = price
        self.price_type = price_type
        self.description = description
        self.materials = materials or []


# 🏗️ Skapa tabell
def create_table():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        price_type TEXT,
        description TEXT,
        materials TEXT
    )
    """)

    conn.commit()
    conn.close()


# ➕ Lägg till tjänst
def add_service(name, price, price_type, description, materials):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO services (name, price, price_type, description, materials)
    VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        price,
        price_type,
        description,
        json.dumps(materials)
    ))

    conn.commit()
    conn.close()


# 📋 Hämta alla tjänster
def get_services():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM services")
    rows = c.fetchall()

    services = []

    for r in rows:
        services.append(Service(
            id=r[0],
            name=r[1],
            price=r[2],
            price_type=r[3],
            description=r[4],
            materials=json.loads(r[5]) if r[5] else []
        ))

    conn.close()
    return services


# ✏️ Uppdatera tjänst
def update_service(id, name, price, price_type, description, materials):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    UPDATE services
    SET name=?, price=?, price_type=?, description=?, materials=?
    WHERE id=?
    """, (
        name,
        price,
        price_type,
        description,
        json.dumps(materials),
        id
    ))

    conn.commit()
    conn.close()


# ❌ Ta bort tjänst
def delete_service(service_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM services WHERE id=?", (service_id,))

    conn.commit()
    conn.close()