from urllib.parse import urlparse


def _find_section(sections, keywords):
    for name, rows in sections.items():
        name = name.lower()

        for key in keywords:
            if key in name:
                return rows

    return []


def _normalize(text):
    return text.lower().replace("-", " ").replace("_", " ").strip()


def _is_official(url):

    try:
        host = urlparse(url).netloc.lower()

        if host.endswith(".gov.in"):
            return True

        if host.endswith(".nic.in"):
            return True

        if host.endswith(".ac.in"):
            return True

        if host.endswith(".edu.in"):
            return True

    except:
        pass

    return False


def _extract_links(links):

    result = {
        "apply": "",
        "login": "",
        "notification": "",
        "official": "",
        "result": "",
        "admit": "",
        "answer_key": "",
        "syllabus": "",
        "objection": ""
    }

    for item in links:

        title = _normalize(item["title"])
        url = item["url"]

        # --------------------
        # Apply
        # --------------------

        if "apply online" in title or title == "apply":

            result["apply"] = url
            continue

        # --------------------
        # Login
        # --------------------

        if "candidate login" in title or "login" in title:

            result["login"] = url
            continue

        # --------------------
        # Notification
        # --------------------

        if (
            "notification" in title
            or "advertisement" in title
            or "official pdf" in title
        ):

            result["notification"] = url
            continue

        # --------------------
        # Result
        # --------------------

        if "result" in title:

            result["result"] = url
            continue

        # --------------------
        # Admit
        # --------------------

        if "admit" in title:

            result["admit"] = url
            continue

        # --------------------
        # Answer Key
        # --------------------

        if "answer key" in title:

            result["answer_key"] = url
            continue

        # --------------------
        # Syllabus
        # --------------------

        if "syllabus" in title:

            result["syllabus"] = url
            continue

        # --------------------
        # Objection
        # --------------------

        if "objection" in title:

            result["objection"] = url
            continue

        # --------------------
        # Official Website
        # --------------------

        if (
            "official website" in title
            or "official site" in title
            or _is_official(url)
        ):

            result["official"] = url

    return result


def parse(data):

    sections = data["sections"]

    links = _extract_links(data["links"])

    return {

        "title": data["title"],

        "description": data["description"],

        "important_dates":
            _find_section(
                sections,
                [
                    "important dates",
                    "important date",
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
                    "vacancy details",
                    "post",
                    "total post"
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

        "apply": links["apply"],

        "login": links["login"],

        "notification": links["notification"],

        "official": links["official"],

        "result": links["result"],

        "admit": links["admit"],

        "answer_key": links["answer_key"],

        "syllabus": links["syllabus"],

        "objection": links["objection"]

    }
