import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 900

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/139 Safari/537.36"
    )
}

SOURCES = [
    {
        "name": "Sarkari Result",
        "url": "https://www.sarkariresult.com/",
    },
    {
        "name": "FreeJobAlert",
        "url": "https://www.freejobalert.com/",
    },
    {
        "name": "Bihar Job Portal",
        "url": "https://biharjobportal.com/",
    },
    {
        "name": "National Scholarship Portal",
        "url": "https://scholarships.gov.in/",
    },
    {
        "name": "Bihar PMS",
        "url": "https://pmsonline.bihar.gov.in/",
    },
    {
        "name": "Buddy4Study",
        "url": "https://www.buddy4study.com/",
    },
]
