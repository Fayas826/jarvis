import os
import sqlite3
import time
import json
import logging

MEMORY_DB_PATH = r"c:\jarvis AI\jarvis\core\memory\jarvis_longitudinal_memory.db"
logging.basicConfig(level=logging.INFO, format="%(asctime)s [LONGITUDINAL_MEMORY] %(message)s")

class SQLiteLongitudinalMemory:
    """
    SQLite-backed Longitudinal Memory & Emotion Trend Injector.
    Preserves context across sessions, tracking user emotion trends, task history, and preference state.
    """

    def __init__(self, db_path=MEMORY_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        logging.info(f"SQLite Longitudinal Memory operational at {self.db_path}")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_text TEXT,
                agent_response TEXT,
                detected_emotion TEXT,
                confidence REAL,
                intent TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def record_turn(self, user_text, agent_response, emotion="neutral", confidence=0.9, intent="general"):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversation_history (timestamp, user_text, agent_response, detected_emotion, confidence, intent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ts, user_text, agent_response, emotion, confidence, intent))
        conn.commit()
        conn.close()

    def get_longitudinal_context(self, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, user_text, agent_response, detected_emotion FROM conversation_history
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        history = []
        emotions = []
        for r in reversed(rows):
            history.append(f"User: {r[1]}\nJARVIS: {r[2]}")
            if r[3]:
                emotions.append(r[3])

        # Check emotion trend
        trend_note = ""
        if len(emotions) >= 3 and len(set(emotions[-3:])) == 1:
            trend_note = f"[LONGITUDINAL MEMORY NOTE: User has consistently expressed '{emotions[-1]}' over the last {len(emotions[-3:])} turns.]"

        return "\n".join(history), trend_note

if __name__ == "__main__":
    mem = SQLiteLongitudinalMemory()
    mem.record_turn("Hello JARVIS", "Greetings sir! How may I assist you?", "joy", 0.95, "greeting")
    hist, trend = mem.get_longitudinal_context()
    print("History:\n", hist)
    print("Trend:", trend)
