# """
# collector.py
# ------------
# Fetches messages from the WhatsApp Cloud API.
# Supports two collection modes:
#   1. By message COUNT  → grab the last N messages from a conversation
#   2. By TIME RANGE     → grab all messages between two timestamps

# WhatsApp Cloud API does NOT provide a native "get all messages" endpoint.
# Messages arrive via webhooks and are stored. This collector reads from
# your own database (messages table) where the webhook handler has already
# saved them — OR it calls the API to fetch messages for a specific thread.

# NOTE: The WhatsApp Business Cloud API only lets you *send* messages and
# receive them via webhooks. There is no "inbox read" endpoint. So the
# real flow is:
#     Webhook → saves raw msg to DB → this collector queries your DB.

# This file handles BOTH paths:
#   - query_by_count()      : fetch last N unprocessed messages from DB
#   - query_by_time_range() : fetch messages between two datetimes from DB
#   - register_webhook_message(): called by your webhook handler to save incoming msgs
# """

# import os
# from datetime import datetime
# from dotenv import load_dotenv
# import requests

# load_dotenv()

# WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
# WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
# API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v19.0")
# BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


# class WhatsAppCollector:
#     """
#     Collects WhatsApp messages from your local database.
#     Also provides a helper to save incoming webhook payloads.
#     """

#     def __init__(self, db_manager):
#         """
#         Args:
#             db_manager: An instance of DatabaseManager (from storage/db_manager.py)
#         """
#         self.db = db_manager
#         self.headers = {
#             "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#             "Content-Type": "application/json",
#         }

#     # ─────────────────────────────────────────────
#     # MODE 1: Collect by COUNT
#     # ─────────────────────────────────────────────
#     def collect_by_count(self, count: int) -> list[dict]:
#         """
#         Fetch the last `count` unprocessed messages from the database.

#         Args:
#             count: Number of messages to retrieve.

#         Returns:
#             List of message dicts with keys: message_id, user_id, content, timestamp
#         """
#         query = """
#             SELECT message_id, user_id, content, timestamp
#             FROM messages
#             WHERE is_processed = FALSE
#             ORDER BY timestamp DESC
#             LIMIT :count;
#         """
#         try:
#             from sqlalchemy import text
#             with self.db.engine.connect() as conn:
#                 rows = conn.execute(text(query), {"count": count}).fetchall()
#             messages = [
#                 {
#                     "message_id": row[0],
#                     "user_id": row[1],
#                     "content": row[2],
#                     "timestamp": row[3],
#                 }
#                 for row in rows
#             ]
#             print(f"✅ Collected {len(messages)} messages (by count={count})")
#             return messages
#         except Exception as e:
#             print(f"❌ collect_by_count error: {e}")
#             return []

#     # ─────────────────────────────────────────────
#     # MODE 2: Collect by TIME RANGE
#     # ─────────────────────────────────────────────
#     def collect_by_time_range(self, start: datetime, end: datetime) -> list[dict]:
#         """
#         Fetch all unprocessed messages between start and end timestamps.

#         Args:
#             start: Start datetime (inclusive)
#             end:   End datetime (inclusive)

#         Returns:
#             List of message dicts.
#         """
#         query = """
#             SELECT message_id, user_id, content, timestamp
#             FROM messages
#             WHERE is_processed = FALSE
#               AND timestamp BETWEEN :start AND :end
#             ORDER BY timestamp ASC;
#         """
#         try:
#             from sqlalchemy import text
#             with self.db.engine.connect() as conn:
#                 rows = conn.execute(text(query), {"start": start, "end": end}).fetchall()
#             messages = [
#                 {
#                     "message_id": row[0],
#                     "user_id": row[1],
#                     "content": row[2],
#                     "timestamp": row[3],
#                 }
#                 for row in rows
#             ]
#             print(f"✅ Collected {len(messages)} messages (time range: {start} → {end})")
#             return messages
#         except Exception as e:
#             print(f"❌ collect_by_time_range error: {e}")
#             return []

#     # ─────────────────────────────────────────────
#     # WEBHOOK HELPER: Save incoming message to DB
#     # ─────────────────────────────────────────────
#     def register_webhook_message(self, payload: dict) -> bool:
#         """
#         Parses a WhatsApp webhook payload and saves it to the database.
#         Call this from your Flask/FastAPI webhook endpoint.

#         Expected payload shape (WhatsApp Cloud API format):
#         {
#           "entry": [{
#             "changes": [{
#               "value": {
#                 "messages": [{
#                   "from": "201XXXXXXXXX",
#                   "id": "wamid.XXX",
#                   "timestamp": "1712345678",
#                   "text": {"body": "Hello!"},
#                   "type": "text"
#                 }],
#                 "contacts": [{"profile": {"name": "Ahmed"}, "wa_id": "201XXXXXXXXX"}]
#               }
#             }]
#           }]
#         }
#         """
#         try:
#             entry = payload["entry"][0]["changes"][0]["value"]
#             messages = entry.get("messages", [])
#             contacts = {c["wa_id"]: c["profile"]["name"] for c in entry.get("contacts", [])}

#             for msg in messages:
#                 if msg.get("type") != "text":
#                     continue  # Skip non-text messages (images, audio, etc.)

#                 phone = msg["from"]
#                 user_id = phone  # Use phone number as user_id
#                 content = msg["text"]["body"]
#                 timestamp = datetime.fromtimestamp(int(msg["timestamp"]))
#                 name = contacts.get(phone, "Unknown")

#                 # Save user (ignore if exists)
#                 self.db.add_user(user_id=user_id, phone_number=phone, name=name)

#                 # Save message
#                 self.db.add_message(user_id=user_id, content=content, timestamp=timestamp)

#             print(f"✅ Webhook: saved {len(messages)} message(s) to DB")
#             return True

#         except (KeyError, IndexError, ValueError) as e:
#             print(f"❌ register_webhook_message parse error: {e}")
#             return False

#     # ─────────────────────────────────────────────
#     # OPTIONAL: Send a message via WhatsApp API
#     # ─────────────────────────────────────────────
#     def send_message(self, to_phone: str, text: str) -> bool:
#         """
#         Sends a WhatsApp text message to a phone number.
#         Useful for sending clustered interest announcements later.
#         """
#         url = f"{BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
#         body = {
#             "messaging_product": "whatsapp",
#             "to": to_phone,
#             "type": "text",
#             "text": {"body": text},
#         }
#         try:
#             response = requests.post(url, headers=self.headers, json=body, timeout=10)
#             response.raise_for_status()
#             print(f"✅ Message sent to {to_phone}")
#             return True
#         except requests.RequestException as e:
#             print(f"❌ send_message error: {e}")
#             return False

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
            print(f"❌ Error: {e}")
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
            print(f"❌ Error: {e}")
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
                print(f"💾 Saved message from {name}: {content}")

            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False