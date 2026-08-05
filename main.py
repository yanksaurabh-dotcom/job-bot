import requests
from telegram_sender import send_message

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
}

try:
    r = requests.get(
        "https://www.sarkariresult.com/",
        headers=headers,
        timeout=30
    )

    send_message(
        f"Status Code : {r.status_code}\nLength : {len(r.text)}"
    )

except Exception as e:
    send_message(str(e))
