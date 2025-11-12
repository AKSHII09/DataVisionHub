import sqlite3

def init_db():
    conn = sqlite3.connect('instance/data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT UNIQUE,
                        password TEXT,
                        address TEXT,
                        role TEXT)''')
    conn.commit()
    conn.close()

def add_user(name, email, password, address, role):
    conn = sqlite3.connect('instance/data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password, address, role) VALUES (?, ?, ?, ?, ?)",
                   (name, email, password, address, role))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect('instance/data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect('instance/data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users
