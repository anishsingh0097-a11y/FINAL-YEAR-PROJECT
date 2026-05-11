import sqlite3
import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.geo import get_location
from config import Config

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Terminal Colors
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _line():
    print(f"{DIM}{'─' * 60}{RESET}", flush=True)

def log_attack(username, password, ip, user_agent):
    try:
        geo = get_location(ip)
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        c.execute("""
            INSERT INTO attack_logs
                (username, password, ip, country, city, latitude, longitude, user_agent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, password, ip,
            geo["country"], geo["city"],
            geo["latitude"], geo["longitude"],
            user_agent, _now()
        ))
        conn.commit()
        conn.close()

        _line()
        print(f"{BOLD}{RED}  ⚠  HONEYPOT LOGIN ATTEMPT DETECTED{RESET}", flush=True)
        _line()
        print(f"  {YELLOW}Time      {RESET}: {WHITE}{_now()}{RESET}", flush=True)
        print(f"  {YELLOW}IP Address{RESET}: {CYAN}{ip}{RESET}", flush=True)
        print(f"  {YELLOW}Location  {RESET}: {WHITE}{geo['country']} / {geo['city']}{RESET}", flush=True)
        print(f"  {YELLOW}Username  {RESET}: {BOLD}{RED}{username}{RESET}", flush=True)
        print(f"  {YELLOW}Password  {RESET}: {BOLD}{RED}{password}{RESET}", flush=True)
        print(f"  {YELLOW}Browser   {RESET}: {DIM}{user_agent[:70]}{RESET}", flush=True)
        _line()

    except Exception as e:
        print(f"{RED}[LOG ERROR]{RESET} {e}", flush=True)


def log_behavior(ip, action):
    try:
        geo = get_location(ip)
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        c.execute("""
            INSERT INTO behavior_logs (ip, action, country, city, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (ip, action, geo["country"], geo["city"], _now()))
        conn.commit()
        conn.close()

        print(f"  {GREEN}[BEHAVIOR]{RESET} {CYAN}{ip}{RESET} ({geo['country']})  →  {WHITE}{action}{RESET}  {DIM}{_now()}{RESET}", flush=True)

    except Exception as e:
        print(f"{RED}[BEHAVIOR ERROR]{RESET} {e}", flush=True)