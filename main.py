from flask import Flask, request
import requests
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

print("🧪 TELEGRAM_TOKEN loaded:", "✅" if TELEGRAM_TOKEN else "❌ MISSING")
print("🧪 TELEGRAM_CHANNEL_ID loaded:", "✅" if TELEGRAM_CHANNEL_ID else "❌ MISSING")

# Test Telegram on boot
if TELEGRAM_TOKEN and TELEGRAM_CHANNEL_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": "🚀 Helius Telegram Bot Started!",
    }
    r = requests.post(url, data=data)
    print("📡 Telegram test sent:", r.status_code)

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
}

def send_alert(token, contract, buyers):
    message = f"⚠️ Wallet Bought!\n\n" \
              f"🪙 Token: {token}\n" \
              f"📄 Contract: `{contract}`\n\n" \
              f"👤 Buyers:\n"
    for b in buyers:
        name, emoji, amount = b
        message += f"{emoji} {name}: {amount:.2f} SOL\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    print("📨 Sending Telegram alert...")
    requests.post(url, data=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("🔔 Webhook hit:", data)
        txs = data.get("transactions", [])

        for tx in txs:
            wallet = tx.get("accountData", [{}])[0].get("account", "")
            if wallet in wallets:
                token_info = tx.get("tokenTransfers", [{}])[0]
                token = token_info.get("symbol", "UNKNOWN")
                contract = token_info.get("mint", "")
                amount = float(token_info.get("tokenAmount", 0))

                now = datetime.utcnow()
                c.execute("INSERT INTO buys VALUES (?, ?, ?, ?)", (token, wallet, amount, now))
                conn.commit()

                cutoff = now - timedelta(minutes=10)
                c.execute("SELECT wallet, amount FROM buys WHERE token=? AND timestamp > ?", (token, cutoff))
                rows = c.fetchall()
                unique_wallets = list(set([r[0] for r in rows]))

                if len(unique_wallets) >= 1:  # testing mode
                    buyers_info = [(wallets[w][0], wallets[w][1], amt) for w, amt in rows if w in wallets][:1]
                    send_alert(token, contract, buyers_info)

        return "ok", 200

    except Exception as e:
        print("❌ Webhook error:", e)
        return "error", 500

if __name__ == "__main__":
    print("🚀 Launching Flask server...")
    app.run(host="0.0.0.0", port=5000)
