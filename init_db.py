import sqlite3

# Connect to a new database file (it will create it)
conn = sqlite3.connect('logs.db')
c = conn.cursor()

# Create a logs table
c.execute('''
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    src_ip TEXT,
    dst_ip TEXT,
    port INTEGER,
    protocol TEXT,
    action TEXT
)
''')

# Insert some dummy data
dummy_logs = [
    ("2025-07-10 08:00", "192.168.1.10", "8.8.8.8", 53, "UDP", "allow"),
    ("2025-07-10 08:05", "192.168.1.12", "185.199.108.153", 443, "TCP", "allow"),
    ("2025-07-10 08:10", "192.168.1.11", "145.100.179.217", 6666, "TCP", "deny"),
    ("2025-07-10 08:15", "192.168.1.14", "10.10.10.10", 22, "TCP", "allow")
]

c.executemany('''
INSERT INTO logs (timestamp, src_ip, dst_ip, port, protocol, action)
VALUES (?, ?, ?, ?, ?, ?)
''', dummy_logs)

conn.commit()
conn.close()
print("Database created and dummy logs inserted.")
