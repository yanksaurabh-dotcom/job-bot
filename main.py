from scrapers.sarkariresult import get_latest
from scrapers.detail_scraper import get_details
from scrapers.parser import parse
from formatter import make_post
from database import is_new
from telegram_sender import send_message
import traceback
import time


def main():

    jobs = get_latest()

    if not jobs:
        send_message("❌ Homepage se koi update nahi mila.")
        return

    new_count = 0

    for job in jobs:

        try:

            if not is_new(job["link"]):
                continue

            details = get_details(job["link"])

            parsed = parse(details)

            message = make_post(parsed)

            send_message(message)

            new_count += 1

            # Telegram rate limit
            time.sleep(2)

        except Exception as e:

            print(e)
            traceback.print_exc()

    print(f"Done. New Posts : {new_count}")


if name == "main":
    main()
