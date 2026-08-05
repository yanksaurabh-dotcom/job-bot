import requests
from config import BOT_TOKEN, CHAT_ID

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_message(text):

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",          # ✅ HTML formatting
        "disable_web_page_preview": False
    }

    r = requests.post(
        URL,
        json=payload,
        timeout=30
    )

    if not r.ok:
        print("Telegram Error:")
        print(r.text)

    return r
