import os
os.environ["PYTHONUNBUFFERED"] = "1"

from flask import Flask, render_template, request, redirect, session, jsonify
from modules import init_db, log_attack, log_behavior
from config import Config
import sqlite3

app = Flask(__name__, template_folder='templates')
app.secret_key = Config.SECRET_KEY

init_db()




@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username   = request.form.get('username', '')
    password   = request.form.get('password', '')
    ip         = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')

    log_attack(username, password, ip, user_agent)
    session['logged_in'] = True
    return redirect('/company')


@app.route('/company')
def company():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(
        request.headers.get('X-Forwarded-For', request.remote_addr),
        "Visited Company Portal"
    )
    return render_template('company.html')


@app.route('/employees')
def employees():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(
        request.headers.get('X-Forwarded-For', request.remote_addr),
        "Accessed Employee Records"
    )
    return render_template('employees.html')


@app.route('/projects')
def projects():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(
        request.headers.get('X-Forwarded-For', request.remote_addr),
        "Viewed Active Projects"
    )
    return render_template('projects.html')


@app.route('/settings')
def settings():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(
        request.headers.get('X-Forwarded-For', request.remote_addr),
        "Visited System Settings"
    )
    return render_template('settings.html')


@app.route('/data')
def data():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(
        request.headers.get('X-Forwarded-For', request.remote_addr),
        "Accessed Confidential Data"
    )
    return render_template('data.html')


@app.route('/track', methods=['POST'])
def track():
    ip     = request.headers.get('X-Forwarded-For', request.remote_addr)
    action = request.json.get('action', 'Unknown action')
    log_behavior(ip, action)
    return jsonify({"status": "ok"})




@app.route('/admin')
def admin_login_page():
    return render_template('admin_login.html')


@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
        session['admin'] = True
        return redirect('/admin/dashboard')
    return render_template('admin_login.html', error="Invalid credentials")


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin')

    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_attacks   = c.execute("SELECT COUNT(*) FROM attack_logs").fetchone()[0]
    unique_ips      = c.execute("SELECT COUNT(DISTINCT ip) FROM attack_logs").fetchone()[0]
    total_countries = c.execute("SELECT COUNT(DISTINCT country) FROM attack_logs").fetchone()[0]
    recent_attacks  = c.execute("SELECT * FROM attack_logs ORDER BY id DESC LIMIT 50").fetchall()
    top_countries   = c.execute("SELECT country, COUNT(*) as cnt FROM attack_logs GROUP BY country ORDER BY cnt DESC LIMIT 10").fetchall()
    top_usernames   = c.execute("SELECT username, COUNT(*) as cnt FROM attack_logs GROUP BY username ORDER BY cnt DESC LIMIT 10").fetchall()
    top_passwords   = c.execute("SELECT password, COUNT(*) as cnt FROM attack_logs GROUP BY password ORDER BY cnt DESC LIMIT 10").fetchall()
    geo_data        = c.execute("SELECT latitude, longitude, country, city, ip, timestamp FROM attack_logs WHERE latitude != 0").fetchall()
    behavior_logs   = c.execute("SELECT * FROM behavior_logs ORDER BY id DESC LIMIT 50").fetchall()

    conn.close()

    return render_template('admin.html',
        total_attacks=total_attacks,
        unique_ips=unique_ips,
        total_countries=total_countries,
        recent_attacks=recent_attacks,
        top_countries=top_countries,
        top_usernames=top_usernames,
        top_passwords=top_passwords,
        geo_data=list(dict(r) for r in geo_data),
        behavior_logs=behavior_logs,
    )


@app.route('/admin/api/stats')
def api_stats():
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 401
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    total  = c.execute("SELECT COUNT(*) FROM attack_logs").fetchone()[0]
    unique = c.execute("SELECT COUNT(DISTINCT ip) FROM attack_logs").fetchone()[0]
    geo    = [dict(r) for r in c.execute(
        "SELECT latitude, longitude, country, city, ip FROM attack_logs WHERE latitude != 0"
    ).fetchall()]
    conn.close()
    return jsonify({"total": total, "unique": unique, "geo": geo})


@app.route('/admin/api/export')
def api_export():
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 401
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM attack_logs ORDER BY id DESC"
    ).fetchall()]
    conn.close()
    return jsonify(rows)



@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)