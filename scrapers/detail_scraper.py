import requests
from bs4 import BeautifulSoup
from config import HEADERS


def get_details(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")

    result = {
        "title": "",
        "description": "",
        "content": ""
    }

    # Title
    h1 = soup.find("h1")
    if h1:
        result["title"] = h1.get_text(" ", strip=True)

    # Meta Description
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        result["description"] = meta.get("content", "").strip()

    # Main Article
    article = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_="entry-content")
    )

    if article:
        text = article.get_text("\n", strip=True)
        result["content"] = text[:12000]

    return result
