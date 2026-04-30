import sqlite3
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


class Material:
    def __init__(self, id, name, price):
        self.id    = id
        self.name  = name
        self.price = price


def create_table():
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT,
        price REAL
    )
    """)

    conn.commit()
    conn.close()


def add_material(name, price):
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("INSERT INTO materials (name, price) VALUES (?, ?)", (name, price))

    conn.commit()
    conn.close()


def get_materials():
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("SELECT * FROM materials")
    rows = c.fetchall()
    conn.close()

    return [Material(id=r[0], name=r[1], price=r[2]) for r in rows]


def update_material(id, name, price):
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("UPDATE materials SET name=?, price=? WHERE id=?", (name, price, id))

    conn.commit()
    conn.close()


def delete_material(id):
    conn = sqlite3.connect(get_db_path())
    c    = conn.cursor()

    c.execute("DELETE FROM materials WHERE id=?", (id,))

    conn.commit()
    conn.close()