from scrapers.category import detect_category


LINE = "━━━━━━━━━━━━━━━━━━"


def section(title, rows):

    if not rows:
        return ""

    txt = f"{title}\n"

    for row in rows:

        if isinstance(row, dict):

            key = row.get("key", "").strip()

            value = row.get("value", "").strip()

            if key:

                txt += f"• <b>{key}</b>: {value}\n"

            else:

                txt += f"• {value}\n"

        else:

            txt += f"• {row}\n"

    txt += "\n"

    return txt


def link(name, url):

    if not url:
        return ""

    return f"{name}\n{url}\n\n"


def make_post(data):

    category = detect_category(data["title"])

    emoji = category["emoji"]

    msg = ""

    # ==========================
    # HEADER
    # ==========================

    msg += f"{emoji} <b>{data['title']}</b>\n\n"

    if data.get("description"):

        msg += f"{data['description']}\n\n"

    # ==========================
    # BODY
    # ==========================

    msg += section(
        "🔥 <b>Total Posts</b>",
        data.get("vacancy")
    )

    msg += section(
        "📅 <b>Important Dates</b>",
        data.get("important_dates")
    )

    msg += section(
        "💰 <b>Application Fee</b>",
        data.get("application_fee")
    )

    msg += section(
        "👤 <b>Age Limit</b>",
        data.get("age_limit")
    )

    msg += section(
        "🎓 <b>Eligibility</b>",
        data.get("eligibility")
    )

    msg += section(
        "📝 <b>Selection Process</b>",
        data.get("selection")
    )

    # ==========================
    # LINKS
    # ==========================

    msg += LINE + "\n\n"

    msg += link(
        "🟢 <b>Apply Online</b>",
        data.get("apply")
    )

    msg += link(
        "🏆 <b>Download Result</b>",
        data.get("result")
    )

    msg += link(
        "🎫 <b>Download Admit Card</b>",
        data.get("admit")
    )

    msg += link(
        "📄 <b>Download Answer Key</b>",
        data.get("answer_key")
    )

    msg += link(
        "📑 <b>Official Notification</b>",
        data.get("notification")
    )

    msg += link(
        "🌐 <b>Official Website</b>",
        data.get("official")
    )

    msg += LINE + "\n"

    msg += "🤖 <b>Auto Update</b>\n"

    msg += "📲 @jobupdatesbihar"

    return msg
