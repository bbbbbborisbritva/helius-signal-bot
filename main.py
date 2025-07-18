import os
import requests

print("✅ Starting Helius Telegram Bot")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
print("🧪 TELEGRAM_TOKEN loaded:", "✅" if TELEGRAM_TOKEN else "❌ MISSING")
print("🧪 TELEGRAM_CHANNEL_ID loaded:", "✅" if TELEGRAM_CHANNEL_ID else "❌ MISSING")

try:
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHANNEL_ID, "text": "🧪 Bot is alive"}
    )
    print("✅ Telegram test sent:", r.status_code)
except Exception as e:
    print("❌ Telegram test failed:", e)

from flask import Flask, request
app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return "alive", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("✅ Webhook hit:")
        print(str(data)[:1000])

        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": "📩 Webhook triggered!",
            }
        )
    except Exception as e:
        print("❌ Error in webhook:", e)
    return "ok", 200

if __name__ == "__main__":
    print("🚀 Launching Flask server...")
    app.run(host="0.0.0.0", port=5000)
