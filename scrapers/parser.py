import re


def _find_section(sections, keywords):
    for name, value in sections.items():
        low = name.lower()

        for key in keywords:
            if key in low:
                return value

    return []


def _find_link(links, keywords):

    for link in links:

        title = link["title"].lower()

        for key in keywords:

            if key in title:
                return link["url"]

    return ""


def parse(data):

    sections = data["sections"]

    links = data["links"]

    return {

        "title": data["title"],

        "description": data["description"],

        "important_dates":
            _find_section(
                sections,
                [
                    "important dates",
                    "dates"
                ]
            ),

        "application_fee":
            _find_section(
                sections,
                [
                    "application fee",
                    "fee"
                ]
            ),

        "age_limit":
            _find_section(
                sections,
                [
                    "age limit"
                ]
            ),

        "vacancy":
            _find_section(
                sections,
                [
                    "vacancy",
                    "post"
                ]
            ),

        "eligibility":
            _find_section(
                sections,
                [
                    "eligibility"
                ]
            ),

        "selection":
            _find_section(
                sections,
                [
                    "selection"
                ]
            ),

        "apply":
            _find_link(
                links,
                [
                    "apply online",
                    "registration",
                    "apply"
                ]
            ),

        "notification":
            _find_link(
                links,
                [
                    "notification",
                    "download notification",
                    "official notification",
                    "pdf"
                ]
            ),

        "official":
            _find_link(
                links,
                [
                    "official website",
                    "official site",
                    "website"
                ]
            ),

        "result":
            _find_link(
                links,
                [
                    "download result",
                    "result"
                ]
            ),

        "admit":
            _find_link(
                links,
                [
                    "admit card"
                ]
            ),

        "answer_key":
            _find_link(
                links,
                [
                    "answer key"
                ]
            )

    }
