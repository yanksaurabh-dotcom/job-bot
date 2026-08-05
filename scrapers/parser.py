import re


def find(text, start, end_list):
    try:
        s = text.index(start) + len(start)

        e = len(text)

        for end in end_list:
            p = text.find(end, s)
            if p != -1 and p < e:
                e = p

        return text[s:e].strip()

    except ValueError:
        return ""


def parse(details):

    text = details["content"]

    return {
        "title": details["title"],

        "description": details["description"],

        "dates": find(
            text,
            "Important Dates",
            [
                "Application Fee",
                "Age Limit",
                "Total Post"
            ]
        ),

        "fee": find(
            text,
            "Application Fee",
            [
                "Age Limit",
                "Total Post"
            ]
        ),

        "age": find(
            text,
            "Age Limit",
            [
                "Total Post",
                "Vacancy Details",
                "Eligibility Criteria"
            ]
        ),

        "post": find(
            text,
            "Total Post",
            [
                "Vacancy Details",
                "Eligibility Criteria"
            ]
        ),

        "eligibility": find(
            text,
            "Eligibility Criteria",
            [
                "How To",
                "Mode Of Selection",
                "Important Links"
            ]
        ),

        "selection": find(
            text,
            "Mode Of Selection",
            [
                "Important Links"
            ]
        )
    }
