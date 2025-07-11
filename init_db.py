import sqlite3
import hashlib
from datetime import datetime
import random

conn = sqlite3.connect('logs.db')
c = conn.cursor()

# Users table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
''')

# Logs table
c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        src_ip TEXT,
        dest_ip TEXT,
        port INTEGER,
        protocol TEXT,
        action TEXT
    )
''')

# Add users (admin and analyst)
users = [
    ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin'),
    ('analyst', hashlib.sha256('analyst123'.encode()).hexdigest(), 'analyst')
]
for user in users:
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", user)
    except sqlite3.IntegrityError:
        pass

# Add sample logs
sample_logs = []
for _ in range(30):
    sample_logs.append((
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        f"192.168.1.{random.randint(2,254)}",
        f"10.0.0.{random.randint(2,254)}",
        random.choice([80, 443, 23, 3389, 445]),
        random.choice(["TCP", "UDP"]),
        random.choice(["allow", "deny"])
    ))

c.executemany("INSERT INTO logs (timestamp, src_ip, dest_ip, port, protocol, action) VALUES (?, ?, ?, ?, ?, ?)", sample_logs)

conn.commit()
conn.close()
print("✅ Database initialized successfully.")
