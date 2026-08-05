from scrapers.sarkariresult import get_latest
from scrapers.detail_scraper import get_details
from scrapers.parser import parse
from formatter import make_post
from database import is_new
from telegram_sender import send_message

import traceback
import time


def process_job(job):

    # Duplicate check
    if not is_new(job["link"]):
        return False

    # Article scrape
    details = get_details(job["link"])

    # Parse
    parsed = parse(details)

    # Agar title parser se nahi mila
    if not parsed.get("title"):
        parsed["title"] = job["title"]

    # Telegram Message
    message = make_post(parsed)

    # Send
    send_message(message)

    return True


def main():

    print("=" * 60)
    print("SarkariResult Bot Started")
    print("=" * 60)

    jobs = get_latest()

    if not jobs:

        print("No Jobs Found")

        return

    total = 0

    sent = 0

    for job in jobs:

        total += 1

        try:

            if process_job(job):

                sent += 1

                print(f"[{sent}] {job['title']}")

                # Telegram Rate Limit
                time.sleep(2)

        except Exception as e:

            print(e)

            traceback.print_exc()

    print("=" * 60)
    print(f"Checked : {total}")
    print(f"Sent    : {sent}")
    print("=" * 60)


if name == "main":
    main()
