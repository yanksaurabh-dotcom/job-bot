from scrapers.sarkariresult import get_latest
from scrapers.detail_scraper import get_details
from database import is_new
from telegram_sender import send_message
import time

try:
    jobs = get_latest()

    for job in jobs:

        if not is_new(job["link"]):
            continue

        details = get_details(job["link"])

        message = f"""
📢 {details['title']}

━━━━━━━━━━━━━━━━━━

📝 {details['description']}

━━━━━━━━━━━━━━━━━━

{details['content'][:3000]}

━━━━━━━━━━━━━━━━━━

🔗 Read Full Details
{job['link']}

🤖 @jobupdatesbihar
"""

        send_message(message)

        time.sleep(2)

except Exception as e:
    send_message(f"❌ {e}")
