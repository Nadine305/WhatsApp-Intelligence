import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v19.0")
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


class WhatsAppCollector:

    def __init__(self, db_manager):
        self.db = db_manager
        self.headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

    def collect_by_count(self, count: int) -> list[dict]:
        query = """
            SELECT message_id, user_id, content, timestamp
            FROM messages
            WHERE is_processed = FALSE
            ORDER BY timestamp DESC
            LIMIT :count;
        """
        try:
            with self.db.engine.connect() as conn:
                rows = conn.execute(text(query), {"count": count}).fetchall()
            return [{"message_id": r[0], "user_id": r[1], "content": r[2], "timestamp": r[3]} for r in rows]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def collect_by_time_range(self, start: datetime, end: datetime) -> list[dict]:
        query = """
            SELECT message_id, user_id, content, timestamp
            FROM messages
            WHERE is_processed = FALSE
              AND timestamp BETWEEN :start AND :end
            ORDER BY timestamp ASC;
        """
        try:
            with self.db.engine.connect() as conn:
                rows = conn.execute(text(query), {"start": start, "end": end}).fetchall()
            return [{"message_id": r[0], "user_id": r[1], "content": r[2], "timestamp": r[3]} for r in rows]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def register_webhook_message(self, payload: dict) -> bool:
        try:
            entry = payload["entry"][0]["changes"][0]["value"]
            messages = entry.get("messages", [])
            contacts = {c["wa_id"]: c["profile"]["name"] for c in entry.get("contacts", [])}

            for msg in messages:
                if msg.get("type") != "text":
                    continue
                phone = msg["from"]
                user_id = phone
                content = msg["text"]["body"]
                timestamp = datetime.fromtimestamp(int(msg["timestamp"]))
                name = contacts.get(phone, "Unknown")

                self.db.add_user(user_id=user_id, phone_number=phone, name=name)
                self.db.add_message(user_id=user_id, content=content, timestamp=timestamp)
                print(f"Saved message from {name}: {content}")

            return True
        except Exception as e:
            print(f"Error: {e}")
            return False