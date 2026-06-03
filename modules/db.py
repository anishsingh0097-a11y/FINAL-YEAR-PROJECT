import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


def get_connection():
    import sqlite3
    conn = sqlite3.connect(Config.DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    import sqlite3
    conn = sqlite3.connect(Config.DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS attack_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT,
            password    TEXT,
            ip          TEXT,
            country     TEXT,
            city        TEXT,
            latitude    REAL,
            longitude   REAL,
            user_agent  TEXT,
            timestamp   TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS behavior_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ip          TEXT,
            action      TEXT,
            country     TEXT,
            city        TEXT,
            timestamp   TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS registered_users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT,
            username    TEXT,
            email       TEXT,
            password    TEXT,
            phone       TEXT,
            ip          TEXT,
            country     TEXT,
            city        TEXT,
            user_agent  TEXT,
            timestamp   TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialised successfully.", flush=True)


def backup_database():
    import shutil, datetime
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = f"honeypot_backup_{ts}.db"
    shutil.copy(Config.DB_NAME, dest)
    return dest