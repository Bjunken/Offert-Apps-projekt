import sqlite3

DB = "app.db"


class Service:
    def __init__(self, id, name, price, price_type, description):
        self.id = id
        self.name = name
        self.price = price
        self.price_type = price_type
        self.description = description


def create_table():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        price_type TEXT,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_service(name, price, price_type, description):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO services (name, price, price_type, description)
    VALUES (?, ?, ?, ?)
    """, (name, price, price_type, description))

    conn.commit()
    conn.close()


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
            description=r[4]
        ))

    conn.close()
    return services


def update_service(id, name, price, price_type, description):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    UPDATE services
    SET name=?, price=?, price_type=?, description=?
    WHERE id=?
    """, (name, price, price_type, description, id))

    conn.commit()
    conn.close()