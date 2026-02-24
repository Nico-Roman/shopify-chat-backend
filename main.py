from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

@app.route("/send-message", methods=["POST"])
def send_message():
    data = request.json
    customer_name = data.get("name", "Anónimo")
    customer_email = data.get("email", "Sin email")
    message = data.get("message", "")

    text = f"""
💬 *Nuevo mensaje de chat*

👤 *Nombre:* {customer_name}
📧 *Email:* {customer_email}
📝 *Mensaje:* {message}
    """

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(telegram_url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

    if response.status_code == 200:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 500

@app.route("/", methods=["GET"])
def home():
    return "Chat backend funcionando ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
