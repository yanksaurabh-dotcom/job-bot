from scrapers.sarkariresult import get_latest
from scrapers.detail_scraper import get_details
from scrapers.parser import parse
from formatter import make_post
from database import is_new
from telegram_sender import send_message
import time

jobs = get_latest()

for job in jobs:

    if not is_new(job["link"]):
        continue

    details = get_details(job["link"])

    data = parse(details)

    message = make_post(data, job["link"])

    send_message(message)

    time.sleep(2)
