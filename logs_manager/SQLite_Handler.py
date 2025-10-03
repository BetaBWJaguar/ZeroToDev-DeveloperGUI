import logging, sqlite3, json
from datetime import datetime

class SQLiteLogHandler(logging.Handler):
    def __init__(self, db_path):
        super().__init__()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS logs (
                                                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              timestamp TEXT,
                                                              level TEXT,
                                                              event TEXT,
                                                              data TEXT
                          )
                          """)
        self.conn.commit()

    def emit(self, record):
        try:
            msg = record.getMessage()

            try:
                payload = json.loads(msg)
                event = payload.get("event", "UNKNOWN")
                data = payload.get("data", {})
                timestamp = payload.get("timestamp", datetime.fromtimestamp(record.created).isoformat())
            except Exception:
                event = "RAW"
                data = {"message": msg}
                timestamp = datetime.fromtimestamp(record.created).isoformat()

            self.conn.execute(
                "INSERT INTO logs (timestamp, level, event, data) VALUES (?, ?, ?, ?)",
                (
                    timestamp,
                    record.levelname,
                    event,
                    json.dumps(data, ensure_ascii=False)
                )
            )
            self.conn.commit()

        except Exception as e:
            print("SQLite logging error:", e)
