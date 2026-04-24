# """
# webhook_server.py
# -----------------
# A minimal Flask server that:
#   1. Handles WhatsApp webhook verification (GET)
#   2. Receives incoming messages and saves them to DB (POST)
# """

# from flask import Flask, request, jsonify
# from src.storage.db_manager import DatabaseManager
# from src.ingestion.collector import WhatsAppCollector
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# db = DatabaseManager()
# collector = WhatsAppCollector(db)

# VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "my_secret_token")


# # ── Step 1: WhatsApp verifies your webhook (one-time) ────────────────
# @app.route("/webhook", methods=["GET"])
# def verify():
#     mode = request.args.get("hub.mode")
#     token = request.args.get("hub.verify_token")
#     challenge = request.args.get("hub.challenge")

#     if mode == "subscribe" and token == VERIFY_TOKEN:
#         print("✅ Webhook verified!")
#         return challenge, 200
#     return "Forbidden", 403


# # ── Step 2: Receive incoming messages ────────────────────────────────
# @app.route("/webhook", methods=["POST"])
# def receive_message():
#     payload = request.get_json()
#     print(f"📨 Incoming webhook: {payload}")
#     collector.register_webhook_message(payload)
#     return jsonify({"status": "ok"}), 200


# if __name__ == "__main__":
#     app.run(port=5000, debug=True)

# from flask import Flask, request, jsonify
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "my_secret_token")

# @app.route("/webhook", methods=["GET"])
# def verify():
#     mode = request.args.get("hub.mode")
#     token = request.args.get("hub.verify_token")
#     challenge = request.args.get("hub.challenge")
#     if mode == "subscribe" and token == VERIFY_TOKEN:
#         print("✅ Webhook verified!")
#         return challenge, 200
#     return "Forbidden", 403

# @app.route("/webhook", methods=["POST"])
# def receive_message():
#     payload = request.get_json()
#     print(f"📨 Incoming webhook: {payload}")
#     return jsonify({"status": "ok"}), 200

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
# from flask import Flask, request, jsonify
# import os
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)

# @app.route("/", methods=["GET"])
# @app.route("/webhook", methods=["GET"])
# def verify():
#     mode = request.args.get("hub.mode")
#     token = request.args.get("hub.verify_token")
#     challenge = request.args.get("hub.challenge")

#     print(f"Mode: {mode}, Token: {token}, Challenge: {challenge}")

#     if mode == "subscribe":
#         print("✅ Webhook verified!")
#         return challenge, 200
#     return "Forbidden", 403

# @app.route("/", methods=["POST"])
# @app.route("/webhook", methods=["POST"])
# def receive_message():
#     payload = request.get_json()
#     print(f"📨 Incoming webhook: {payload}")
#     return jsonify({"status": "ok"}), 200

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
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