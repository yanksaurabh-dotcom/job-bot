import requests
from bs4 import BeautifulSoup
from config import HEADERS

URL = "https://sarkariresult.com.cm/"


def get_latest():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")

    links = []

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)

        if len(text) < 15:
            continue

        href = a["href"]

        if href.startswith("/"):
            href = URL.rstrip("/") + href

        links.append(
            {
                "title": text,
                "link": href
            }
        )

    return links[:20]
