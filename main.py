from flask import Flask, request
import requests
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Hardcoded temporarily for debug
TELEGRAM_TOKEN = "7444501428:AAESyTC8EwqQN1YybvmubepbCsDVrMzoQ5w"
TELEGRAM_CHANNEL_ID = "-1002749606748"

# Debug: print hardcoded values
print("🧪 TELEGRAM_TOKEN loaded:", TELEGRAM_TOKEN[:10] + "...")
print("🧪 TELEGRAM_CHANNEL_ID loaded:", TELEGRAM_CHANNEL_ID)

# Telegram test message at startup
try:
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHANNEL_ID, "text": "🚀 Bot is online and listening (hardcoded)."}
    )
except Exception as e:
    print("❌ Telegram startup message failed:", e)

# DB setup
conn = sqlite3.connect('trades.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS buys (
    token TEXT,
    wallet TEXT,
    amount REAL,
    timestamp DATETIME
)''')
conn.commit()

# Tracked wallets
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
