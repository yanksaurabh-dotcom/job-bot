from scrapers.category import detect_category


def _rows(rows):
    if not rows:
        return ""

    out = ""

    for row in rows:

        if isinstance(row, dict):

            k = row.get("key", "").strip()
            v = row.get("value", "").strip()

            if k:
                out += f"• {k}: {v}\n"
            else:
                out += f"• {v}\n"

        else:
            out += f"• {row}\n"

    return out.strip()


def _link(title, url):
    if not url:
        return ""
    return f"{title}\n{url}\n\n"


def make_post(data):

    cat = detect_category(data["title"])

    msg = f"{cat['emoji']} <b>{data['title']}</b>\n\n"

    if data.get("description"):
        msg += f"{data['description']}\n\n"

    if data.get("vacancy"):
        msg += "🔥 <b>Total Posts</b>\n"
        msg += _rows(data["vacancy"])
        msg += "\n\n"

    if data.get("important_dates"):
        msg += "📅 <b>Important Dates</b>\n"
        msg += _rows(data["important_dates"])
        msg += "\n\n"

    if data.get("application_fee"):
        msg += "💰 <b>Application Fee</b>\n"
        msg += _rows(data["application_fee"])
        msg += "\n\n"

    if data.get("age_limit"):
        msg += "👤 <b>Age Limit</b>\n"
        msg += _rows(data["age_limit"])
        msg += "\n\n"

    if data.get("eligibility"):
        msg += "🎓 <b>Eligibility</b>\n"
        msg += _rows(data["eligibility"])
        msg += "\n\n"

    if data.get("selection"):
        msg += "📝 <b>Selection Process</b>\n"
        msg += _rows(data["selection"])
        msg += "\n\n"

    msg += "━━━━━━━━━━━━━━━━━━\n\n"

    if data.get("apply"):
        msg += _link("🟢 Apply Online", data["apply"])

    if data.get("result"):
        msg += _link("🏆 Download Result", data["result"])

    if data.get("admit"):
        msg += _link("🎫 Download Admit Card", data["admit"])

    if data.get("answer_key"):
        msg += _link("📄 Download Answer Key", data["answer_key"])

    if data.get("notification"):
        msg += _link("📑 Official Notification", data["notification"])

    if data.get("official"):
        msg += _link("🌐 Official Website", data["official"])

    msg += "━━━━━━━━━━━━━━━━━━\n"
    msg += "🤖 Auto Update\n"
    msg += "📲 @jobupdatesbihar"

    return msg
