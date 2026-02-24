from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import threading
import time

app = Flask(__name__)
CORS(app)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Almacena los chats activos: {session_id: [mensajes]}
active_chats = {}
# Almacena respuestas pendientes: {session_id: [respuestas]}
pending_responses = {}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

@app.route("/send-message", methods=["POST"])
def send_message():
    data = request.json
    session_id = data.get("session_id", "")
    customer_name = data.get("name", "Anónimo")
    customer_phone = data.get("phone", "Sin teléfono")
    message = data.get("message", "")

    if session_id not in active_chats:
        active_chats[session_id] = []
        pending_responses[session_id] = []
        # Primer mensaje: mostrar info del cliente
        send_telegram(f"💬 *Nuevo chat iniciado*\n👤 *Nombre:* {customer_name}\n📞 *Teléfono:* {customer_phone}\n🔑 *ID:* `{session_id}`\n\n_Para responder escribe:_ `{session_id}: tu mensaje`")

    active_chats[session_id].append({"role": "customer", "text": message})
    send_telegram(f"👤 *{customer_name}* `[{session_id}]`:\n{message}")

    return jsonify({"success": True}), 200

@app.route("/get-responses", methods=["GET"])
def get_responses():
    session_id = request.args.get("session_id", "")
    if session_id in pending_responses and pending_responses[session_id]:
        responses = pending_responses[session_id].copy()
        pending_responses[session_id] = []
        return jsonify({"responses": responses}), 200
    return jsonify({"responses": []}), 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.json
    if "message" in data:
        text = data["message"].get("text", "")
        # Formato esperado: "SESSION_ID: mensaje"
        if ": " in text:
            parts = text.split(": ", 1)
            session_id = parts[0].strip()
            response_text = parts[1].strip()
            if session_id in pending_responses:
                pending_responses[session_id].append(response_text)
                send_telegram(f"✅ Respuesta enviada a `{session_id}`")
            else:
                send_telegram(f"⚠️ No se encontró la sesión `{session_id}`")
    return jsonify({"ok": True}), 200

@app.route("/", methods=["GET"])
def home():
    return "Chat backend funcionando ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
