from scrapers.sarkariresult import get_latest
from database import is_new
from formatter import make_post
from telegram_sender import send_message
import time

try:
    jobs = get_latest()

    if not jobs:
        send_message("❌ Homepage se koi update nahi mila.")
        raise SystemExit()

    new_count = 0

    for job in jobs:

        if is_new(job["link"]):

            msg = make_post(
                "SarkariResult",
                job["title"],
                job["link"]
            )

            send_message(msg)

            new_count += 1

            # Telegram rate limit se bachne ke liye
            time.sleep(2)

    if new_count == 0:
        print("No new updates found.")

except Exception as e:
    send_message(f"❌ ERROR\n\n{e}")
