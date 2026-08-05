from scrapers.sarkariresult import get_latest
from database import is_new
from formatter import make_post
from telegram_sender import send_message

try:
    jobs = get_latest()

    if not jobs:
        send_message("❌ Homepage se koi update nahi mila.")
        raise SystemExit()

    for job in jobs:

        if is_new(job["link"]):

            msg = make_post(
                "SarkariResult",
                job["title"],
                job["link"]
            )

            send_message(msg)

            break

except Exception as e:
    send_message(f"❌ ERROR\n\n{e}")
