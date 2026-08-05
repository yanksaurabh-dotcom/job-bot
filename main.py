import cloudscraper
from telegram_sender import send_message

scraper = cloudscraper.create_scraper()

try:
    r = scraper.get("https://www.sarkariresult.com.cm/", timeout=30)

    send_message(
        f"Status : {r.status_code}\nLength : {len(r.text)}"
    )

except Exception as e:
    send_message(str(e))
