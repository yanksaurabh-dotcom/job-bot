import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"Checking Token: {BOT_TOKEN[:6] if BOT_TOKEN else 'NOT FOUND'}")
print(f"Checking Chat ID: {CHAT_ID}")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "🤖 <b>Test Message:</b> Telegram Bot Connection Successfully Working!",
    "parse_mode": "HTML"
}

res = requests.post(url, json=payload)
print(f"HTTP Status Code: {res.status_code}")
print(f"Telegram API Response: {res.text}")
