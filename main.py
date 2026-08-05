import requests
from telegram_sender import send_message

try:
    r = requests.get("https://www.sarkariresult.com", timeout=30)

    if r.status_code == 200:
        send_message("✅ JobBot Bihar Started Successfully!\n\nSarkari Result website is reachable.")
    else:
        send_message(f"❌ Website Error : {r.status_code}")

except Exception as e:
    send_message(f"❌ Error\n\n{e}")
