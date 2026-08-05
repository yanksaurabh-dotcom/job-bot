import requests
from bs4 import BeautifulSoup
from config import HEADERS

URL = "https://sarkariresult.com.cm/"


def get_latest():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")

    jobs = []

    for a in soup.select("a.wp-block-latest-posts__post-title"):
        title = a.get_text(strip=True)
        link = a["href"]

        jobs.append({
            "title": title,
            "link": link
        })

    return jobs
