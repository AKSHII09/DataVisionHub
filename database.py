import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
DB_PATH = os.path.join(INSTANCE_DIR, "users.db")

def ensure_instance():
    os.makedirs(INSTANCE_DIR, exist_ok=True)

def get_db_connection():
    ensure_instance()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    ensure_instance()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        address TEXT,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin','user')) NOT NULL DEFAULT 'user'
    )
    """)
    conn.commit()

    # Add default admin if not exists
    cur.execute("SELECT * FROM users WHERE email = ?", ("admin@quantumsoft.net",))
    if not cur.fetchone():
        hashed = generate_password_hash("Admin@123")
        cur.execute("INSERT INTO users (name, email, address, password, role) VALUES (?, ?, ?, ?, ?)",
                    ("Admin", "admin@quantumsoft.net", "Quantum HQ", hashed, "admin"))
        conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
