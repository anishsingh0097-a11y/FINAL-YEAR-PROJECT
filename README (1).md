# 🍯 Honeypot-Based Attack Monitoring System
### Final Year Project — Anish Kumar Singh (2313019)
### Usha Martin University, Ranchi | Guide: Mr. Pankaj Kumar

---

## Project Overview
A web-based honeypot system that simulates a vulnerable corporate login portal to attract and monitor malicious login attempts. Captures IP addresses, credentials, timestamps, and browser details. Uses IP geolocation to map attack origins on an interactive world map.

---

## Project Structure
```
honeypot/
├── app.py               # Main Flask application (all routes)
├── config.py            # Configuration (DB, keys, admin credentials)
├── requirements.txt     # Python dependencies
├── modules/
│   ├── __init__.py      # Module exports
│   ├── db.py            # SQLite database init & connection
│   ├── geo.py           # IP geolocation (ip-api.com)
│   └── logger.py        # Attack & behavior logging
└── templates/
    ├── login.html        # Honeypot fake login page
    ├── company.html      # Fake company portal (post-login)
    ├── data.html         # Fake confidential data page
    ├── admin_login.html  # Admin panel login
    ├── admin.html        # Full monitoring dashboard
    └── 404.html          # Custom 404 page
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
python app.py
```

### 3. Access the system
| URL | Description |
|-----|-------------|
| http://localhost:5000/ | Honeypot login page (shown to attackers) |
| http://localhost:5000/admin | Admin panel login |

### 4. Admin Credentials
```
Username: admin
Password: admin123
```
*(Change in config.py before deployment)*

---

## How It Works
1. Attacker visits the fake TechCorp login page
2. Any credentials entered are **always accepted** (honeypot behaviour)
3. The system logs: username, password, IP, browser, timestamp, country, city
4. Attacker is redirected to fake company portal — behavior is also tracked
5. Admin views all data on the monitoring dashboard with geo map
