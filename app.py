import os
import datetime
import sqlite3

os.environ["PYTHONUNBUFFERED"] = "1"

from flask import Flask, render_template, request, redirect, session, jsonify
from modules import init_db, log_attack, log_behavior
from modules.geo import get_location
from config import Config

app = Flask(__name__, template_folder='templates')
app.secret_key = Config.SECRET_KEY

init_db()


def get_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    return ip


def is_registered(username):
    """Check karo ki username (email) registered hai ya nahi."""
    conn = sqlite3.connect(Config.DB_NAME)
    c    = conn.cursor()
    row  = c.execute(
        "SELECT id FROM registered_users WHERE email = ? OR username = ?",
        (username, username)
    ).fetchone()
    conn.close()
    return row is not None


# ══════════════════════════════════════════════════════════════════
# REGISTER
# ══════════════════════════════════════════════════════════════════

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_post():
    name       = request.form.get('name', '')
    username   = request.form.get('username', '')
    email      = request.form.get('email', '')
    password   = request.form.get('password', '')
    phone      = request.form.get('phone', '')
    ip         = get_ip()
    user_agent = request.headers.get('User-Agent', '')
    geo        = get_location(ip)
    timestamp  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(Config.DB_NAME)
    c    = conn.cursor()
    c.execute("""
        INSERT INTO registered_users
        (name, username, email, password, phone, ip, country, city, user_agent, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, username, email, password, phone,
          ip, geo['country'], geo['city'], user_agent, timestamp))
    conn.commit()
    conn.close()

    print(f"\033[92m[REGISTER]\033[0m {ip} | {geo['country']}/{geo['city']} | "
          f"Name:{name} | User:{username} | Email:{email} | "
          f"Phone:{phone} | Pass:{password}", flush=True)

    return redirect('/?registered=1')


# ══════════════════════════════════════════════════════════════════
# HOME / LOGIN
# ══════════════════════════════════════════════════════════════════

@app.route('/')
def home():
    registered = request.args.get('registered', '')
    failed     = request.args.get('failed', '')
    return render_template('login.html',
                           registered=registered,
                           failed=failed)


@app.route('/login', methods=['POST'])
def login():
    username   = request.form.get('username', '')
    password   = request.form.get('password', '')
    ip         = get_ip()
    user_agent = request.headers.get('User-Agent', '')

    # Hamesha data save karo
    log_attack(username, password, ip, user_agent)

    # Check karo registered hai ya nahi
    if is_registered(username):
        # Registered — login allow
        session['logged_in'] = True
        print(f"\033[92m[LOGIN SUCCESS]\033[0m {ip} | {username}", flush=True)
        return redirect('/company')
    else:
        # Not registered — login failed
        print(f"\033[91m[LOGIN FAILED]\033[0m {ip} | {username}:{password} | Not Registered", flush=True)
        return redirect('/?failed=1')


# ══════════════════════════════════════════════════════════════════
# COMPANY PORTAL
# ══════════════════════════════════════════════════════════════════

@app.route('/company')
def company():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(get_ip(), "Visited Company Portal")
    return render_template('company.html')


@app.route('/employees')
def employees():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(get_ip(), "Accessed Employee Records")
    return render_template('employees.html')


@app.route('/projects')
def projects():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(get_ip(), "Viewed Active Projects")
    return render_template('projects.html')


@app.route('/settings')
def settings():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(get_ip(), "Visited System Settings")
    return render_template('settings.html')


@app.route('/data')
def data():
    if not session.get('logged_in'):
        return redirect('/')
    log_behavior(get_ip(), "Accessed Confidential Data")
    return render_template('data.html')


@app.route('/track', methods=['POST'])
def track():
    action = request.json.get('action', 'Unknown action')
    log_behavior(get_ip(), action)
    return jsonify({"status": "ok"})


# ══════════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════════

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

    total_attacks    = c.execute("SELECT COUNT(*) FROM attack_logs").fetchone()[0]
    unique_ips       = c.execute("SELECT COUNT(DISTINCT ip) FROM attack_logs").fetchone()[0]
    total_countries  = c.execute("SELECT COUNT(DISTINCT country) FROM attack_logs").fetchone()[0]
    total_registered = c.execute("SELECT COUNT(*) FROM registered_users").fetchone()[0]
    failed_logins    = c.execute("SELECT COUNT(*) FROM attack_logs").fetchone()[0]

    recent_attacks   = c.execute("SELECT * FROM attack_logs ORDER BY id DESC LIMIT 50").fetchall()
    top_countries    = c.execute("SELECT country, COUNT(*) as cnt FROM attack_logs GROUP BY country ORDER BY cnt DESC LIMIT 10").fetchall()
    top_usernames    = c.execute("SELECT username, COUNT(*) as cnt FROM attack_logs GROUP BY username ORDER BY cnt DESC LIMIT 10").fetchall()
    top_passwords    = c.execute("SELECT password, COUNT(*) as cnt FROM attack_logs GROUP BY password ORDER BY cnt DESC LIMIT 10").fetchall()
    geo_data         = c.execute("SELECT latitude, longitude, country, city, ip, timestamp FROM attack_logs WHERE latitude != 0").fetchall()
    behavior_logs    = c.execute("SELECT * FROM behavior_logs ORDER BY id DESC LIMIT 50").fetchall()
    registered_users = c.execute("SELECT * FROM registered_users ORDER BY id DESC LIMIT 50").fetchall()

    conn.close()

    return render_template('admin.html',
        total_attacks=total_attacks,
        unique_ips=unique_ips,
        total_countries=total_countries,
        total_registered=total_registered,
        recent_attacks=recent_attacks,
        top_countries=top_countries,
        top_usernames=top_usernames,
        top_passwords=top_passwords,
        geo_data=list(dict(r) for r in geo_data),
        behavior_logs=behavior_logs,
        registered_users=registered_users,
    )


@app.route('/admin/api/export')
def api_export():
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 401
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM attack_logs ORDER BY id DESC").fetchall()]
    conn.close()
    return jsonify(rows)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)