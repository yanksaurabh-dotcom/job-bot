import requests
from config import BOT_TOKEN, CHAT_ID

API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_message(text):
    try:
        r = requests.post(
            API,
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=30,
        )

        if r.status_code == 200:
            print("Telegram Message Sent")
        else:
            print(r.text)

    except Exception as e:
        print(e)
