from scrapers.sarkariresult import get_latest
from telegram_sender import send_message

jobs = get_latest()

msg = ""

for i, job in enumerate(jobs, 1):
    msg += f"{i}. {job['title']}\n\n"

send_message(msg[:4000])
