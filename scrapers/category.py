import re


CATEGORIES = [
    ("answer key", "answer_key", "📄"),
    ("admit card", "admit_card", "🎫"),
    ("exam city", "exam_city", "📍"),
    ("city intimation", "exam_city", "📍"),
    ("result", "result", "🏆"),
    ("merit list", "merit_list", "🏅"),
    ("selection list", "merit_list", "🏅"),
    ("online form", "online_form", "📝"),
    ("recruitment", "online_form", "📝"),
    ("vacancy", "online_form", "📝"),
    ("notification", "notification", "📢"),
    ("scholarship", "scholarship", "🎓"),
    ("admission", "admission", "🏫"),
    ("counselling", "admission", "🏫"),
    ("counseling", "admission", "🏫"),
    ("exam date", "exam_date", "📅"),
    ("syllabus", "syllabus", "📚"),
    ("correction", "correction", "✏️"),
]


def detect_category(title: str):

    text = re.sub(r"\s+", " ", title.lower()).strip()

    for keyword, key, emoji in CATEGORIES:
        if keyword in text:
            return {
                "key": key,
                "emoji": emoji
            }

    return {
        "key": "general",
        "emoji": "📌"
    }


def is_result(title):
    return detect_category(title)["key"] == "result"


def is_form(title):
    return detect_category(title)["key"] == "online_form"


def is_admit(title):
    return detect_category(title)["key"] == "admit_card"


def is_answer_key(title):
    return detect_category(title)["key"] == "answer_key"


def is_scholarship(title):
    return detect_category(title)["key"] == "scholarship"


def is_exam_date(title):
    return detect_category(title)["key"] == "exam_date"
