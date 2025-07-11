from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import csv
import hashlib

app = Flask(__name__)
app.secret_key = 'secretkey123'

def get_logs(src_ip=None, action=None, protocol=None):
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()

    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    if src_ip:
        query += " AND src_ip LIKE ?"
        params.append(f"%{src_ip}%")
    if action:
        query += " AND action = ?"
        params.append(action)
    if protocol:
        query += " AND protocol = ?"
        params.append(protocol)

    query += " ORDER BY timestamp DESC"
    c.execute(query, params)
    logs = c.fetchall()
    conn.close()
    return logs

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        conn = sqlite3.connect('logs.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['logged_in'] = True
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    src_ip = request.args.get('src_ip')
    action = request.args.get('action')
    protocol = request.args.get('protocol')

    if session.get('role') == 'analyst':
        action = 'deny'  # analysts only see deny logs

    logs = get_logs(src_ip, action, protocol)
    allow_count = sum(1 for log in logs if log[6].lower() == 'allow')
    deny_count = sum(1 for log in logs if log[6].lower() == 'deny')

    return render_template('index.html',
                           logs=logs,
                           allow_count=allow_count,
                           deny_count=deny_count,
                           session=session)

@app.route('/download_csv')
def download_csv():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))

    logs = get_logs()
    with open('logs_export.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Timestamp', 'Source IP', 'Destination IP', 'Port', 'Protocol', 'Action'])
        writer.writerows(logs)

    return send_file('logs_export.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
