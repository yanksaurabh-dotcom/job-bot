import requests
from bs4 import BeautifulSoup
from config import HEADERS


def clean(text):
    if not text:
        return ""

    return " ".join(text.replace("\xa0", " ").split())


def get_text(node):
    return clean(node.get_text(" ", strip=True))


def parse_table(table):

    rows = []

    for tr in table.find_all("tr"):

        cols = tr.find_all(["th", "td"])

        if len(cols) == 2:

            rows.append({
                "key": get_text(cols[0]),
                "value": get_text(cols[1])
            })

        elif len(cols) == 1:

            rows.append({
                "key": "",
                "value": get_text(cols[0])
            })

    return rows


def get_details(url):

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    soup = BeautifulSoup(r.text, "lxml")

    data = {
        "title": "",
        "description": "",
        "sections": {},
        "links": []
    }

    # ----------------------
    # TITLE
    # ----------------------

    h1 = soup.find("h1")

    if h1:
        data["title"] = get_text(h1)

    # ----------------------
    # META DESCRIPTION
    # ----------------------

    meta = soup.find(
        "meta",
        attrs={
            "name": "description"
        }
    )

    if meta:

        data["description"] = clean(
            meta.get("content", "")
        )

    # ----------------------
    # ARTICLE
    # ----------------------

    article = (
        soup.find("article")
        or soup.find("main")
        or soup.find(class_="entry-content")
    )

    if not article:
        return data

    # ----------------------
    # TABLES
    # ----------------------

    for table in article.find_all("table"):

        heading = table.find_previous(
            ["h2", "h3", "h4"]
        )

        if not heading:
            continue

        title = get_text(heading).lower()

        data["sections"][title] = parse_table(table)

    # ----------------------
    # IMPORTANT LINKS
    # ----------------------

    for a in article.find_all("a", href=True):

        text = get_text(a)

        href = a["href"]

        if len(text) < 2:
            continue

        data["links"].append({

            "title": text,

            "url": href

        })

    return data
