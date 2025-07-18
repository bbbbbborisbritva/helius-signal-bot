from flask import Flask, request
import requests
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Debug: print env vars
print("🧪 TELEGRAM_TOKEN loaded:", TELEGRAM_TOKEN[:10] + "..." if TELEGRAM_TOKEN else "❌ MISSING")
print("🧪 TELEGRAM_CHANNEL_ID loaded:", TELEGRAM_CHANNEL_ID if TELEGRAM_CHANNEL_ID else "❌ MISSING")

# Optional: test Telegram connection at startup
try:
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHANNEL_ID, "text": "🚀 Bot is online and listening."}
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

# Wallet map (shortened list for clarity — use full list)
wallets = {
    "2JarGaaVhqcV2FbsxQPLagFpPi4qh3SuKt7adYk299hr": ("aaaw1", "🥝"),
    "3gHfSNNpSYE3DrDYUsfZ62fGnFrCxiLuR2n8BiBybonk": ("dust dev", "🧤"),
    "4BdKaxN8G6ka4GYtQQWk4G4dZRUTX2vQH9GcXdBREFUk": ("jijo", "🪂"),
    "4DdrfiDHpmx55i4SPssxVzS9ZaKLb8qr45NKY9Er9nNh": ("mr. frog", "🐸"),
    # ...add the rest
}

def send_alert(token, contract, buyers):
    message = f"⚠️ 5 Smart Wallets Aped In!\n\n" \
              f"🪙 Token: {token}\n" \
              f"📄 Contract: `{contract}`\n\n" \
              f"👤 Buyers:\n"
    for b in buyers:
        name, emoji, amount = b
        message += f"{emoji} {name}: {amount:.2f} SOL\n"

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data)
        print("✅ Telegram alert sent:", response.status_code)
    except Exception as e:
        print("❌ Failed to send Telegram alert:", e)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("✅ Webhook received")
        txs = data.get("transactions", [])

        for tx in txs:
            wallet = tx.get("accountData", [{}])[0].get("account", "")
            if wallet in wallets:
                token_transfers = tx.get("tokenTransfers", [])
                if not token_transfers:
                    continue

                token_info = token_transfers[0]
                token = token_info.get("symbol", "UNKNOWN")
                contract = token_info.get("mint", "")
                try:
                    amount = float(token_info.get("tokenAmount", 0))
                except:
                    amount = 0

                now = datetime.utcnow()
                print(f"🔍 {wallet} bought {token} ({amount} SOL)")

                c.execute("INSERT INTO buys VALUES (?, ?, ?, ?)", (token, wallet, amount, now))
                conn.commit()

                cutoff = now - timedelta(minutes=10)
                c.execute("SELECT wallet, amount FROM buys WHERE token=? AND timestamp > ?", (token, cutoff))
                rows = c.fetchall()
                unique_wallets = list(set([r[0] for r in rows]))

                if len(unique_wallets) >= 1:  # test mode
                    buyers_info = [(wallets[w][0], wallets[w][1], amt) for w, amt in rows if w in wallets][:1]
                    send_alert(token, contract, buyers_info)
    except Exception as e:
        print("❌ Webhook error:", e)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
