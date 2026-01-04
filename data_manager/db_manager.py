import sqlite3
from datetime import datetime


class DBManager:
    def __init__(self, db_path="parking.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        con = self._connect()
        cur = con.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS slot_status (
            slot_id INTEGER PRIMARY KEY,
            occupied INTEGER,
            updated_at TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            level TEXT,
            message TEXT
        )
        """)

        con.commit()
        con.close()

    def update_slot(self, slot_id, occupied):
        con = self._connect()
        cur = con.cursor()
        ts = datetime.utcnow().isoformat()

        cur.execute("""
        INSERT INTO slot_status(slot_id, occupied, updated_at)
        VALUES(?,?,?)
        ON CONFLICT(slot_id) DO UPDATE SET
        occupied=excluded.occupied,
        updated_at=excluded.updated_at
        """, (slot_id, int(occupied), ts))

        con.commit()
        con.close()

    def log_alert(self, level, message):
        con = self._connect()
        cur = con.cursor()
        ts = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO alerts(ts, level, message) VALUES(?,?,?)",
            (ts, level, message)
        )
        con.commit()
        con.close()
