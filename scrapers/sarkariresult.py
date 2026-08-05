import requests
from bs4 import BeautifulSoup
from config import HEADERS

URL = "https://sarkariresult.com.cm/"


def get_latest():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")

    links = []

    for a in soup.select("a[href]"):
        title = a.get_text(" ", strip=True)

if len(title) < 20:
    continue

bad = [
    "Skip to content",
    "Home",
    "Menu",
    "Login",
    "Register",
    "Privacy",
    "Contact",
    "About"
]

if title in bad:
    continue

href = a.get("href")
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
