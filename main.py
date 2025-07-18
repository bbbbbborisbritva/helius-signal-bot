from flask import Flask, request
import requests
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Hardcoded temporarily
TELEGRAM_TOKEN = "7444501428:AAESyTC8EwqQN1YybvmubepbCsDVrMzoQ5w"
TELEGRAM_CHANNEL_ID = "-1002749606748"

print("🧪 TELEGRAM_TOKEN loaded:", TELEGRAM_TOKEN[:10] + "...")
print("🧪 TELEGRAM_CHANNEL_ID loaded:", TELEGRAM_CHANNEL_ID)

try:
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHANNEL_ID, "text": "🧪 Bot online — now logging raw webhook payloads."}
    )
except Exception as e:
    print("❌ Telegram startup message failed:", e)

# DB
conn = sqlite3.connect('trades.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS buys (
    token TEXT,
    wallet TEXT,
    amount REAL,
    timestamp DATETIME
)''')
conn.commit()

wallets = {
    "2JarGaaVhqcV2FbsxQPLagFpPi4qh3SuKt7adYk299hr": ("aaaw1", "🥝"),
    "3gHfSNNpSYE3DrDYUsfZ62fGnFrCxiLuR2n8BiBybonk": ("dust dev", "🧤"),
    "4BdKaxN8G6ka4GYtQQWk4G4dZRUTX2vQH9GcXdBREFUk": ("jijo", "🪂"),
    "4DdrfiDHpmx55i4SPssxVzS9ZaKLb8qr45NKY9Er9nNh": ("mr. frog", "🐸"),
    "4WPTQA7BB4iRdrPhgNpJihGcxKh8T43gLjMn5PbEVfQw": ("oura", "♒"),
    "73LnJ7G9ffBDjEBGgJDdgvLUhD5APLonKrNiHsKDCw5B": ("Waddles", "💦"),
    "9FNz4MjPUmnJqTf6yEDbL1D4SsHVh7uA8zRHhR5K138r": ("danny", "🕳️"),
    "9yYya3F5EJoLnBNKW6z4bZvyQytMXzDcpU5D6yYr4jqL": ("Loopier", "🥭"),
    "AeLaMjzxErZt4drbWVWvcxpVyo8p94xu5vrg41eZPFe3": ("s1mple", "🚹"),
    "AFT3jqzzt9pnv6DtFundS1LhQBVrxxHJSXJrKxQjWGAF": ("simple copy", "☮️"),
    "Av3xWHJ5EsoLZag6pr7LKbrGgLRTaykXomDD5kBhL9YQ": ("heyitsyolo", "👨‍🦲"),
    "BCagckXeMChUKrHEd6fKFA1uiWDtcmCXMsqaheLiUPJd": ("dv", "🧭")
}

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("✅ Raw webhook payload received:")
        print(data)

        txs = data.get("transactions", [])
        print(f"📦 {len(txs)} transactions found in payload")

        for tx in txs:
            print("🔍 Full transaction object:")
            print(tx)

    except Exception as e:
        print("❌ Webhook error:", e)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
