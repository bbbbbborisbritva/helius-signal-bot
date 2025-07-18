from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "7444501428:AAESyTC8EwqQN1YybvmubepbCsDVrMzoQ5w"
TELEGRAM_CHANNEL_ID = "-1002749606748"

print("🧪 TELEGRAM_TOKEN loaded:", TELEGRAM_TOKEN[:10] + "...")
print("🧪 TELEGRAM_CHANNEL_ID loaded:", TELEGRAM_CHANNEL_ID)

# Test Telegram startup
try:
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHANNEL_ID, "text": "🧪 Bot online — webhook logger ready"}
    )
except Exception as e:
    print("❌ Telegram test failed:", e)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("✅ Webhook received.")
        print(f"📦 Payload preview:\n{str(data)[:1000]}")

        # Optional: notify in Telegram
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": "📩 Webhook received\nPayload logged in Railway",
            }
        )

    except Exception as e:
        print("❌ Webhook crash:", e)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
