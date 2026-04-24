from flask import Flask, request, jsonify
from src.storage.db_manager import DatabaseManager
from src.ingestion.collector import WhatsAppCollector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db = DatabaseManager()
collector = WhatsAppCollector(db)

@app.route("/", methods=["GET"])
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe":
        print("✅ Webhook verified!")
        return challenge, 200
    return "Forbidden", 403

@app.route("/", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def receive_message():
    payload = request.get_json()
    print(f"📨 Incoming webhook: {payload}")
    collector.register_webhook_message(payload)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)