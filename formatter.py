def make_post(data, link):

    msg = f"📢 {data['title']}\n\n"

    if data["description"]:
        msg += f"📝 {data['description']}\n\n"

    if data["post"]:
        msg += "🔥 Total Posts\n"
        msg += data["post"] + "\n\n"

    if data["dates"]:
        msg += "📅 Important Dates\n"
        msg += data["dates"] + "\n\n"

    if data["fee"]:
        msg += "💰 Application Fee\n"
        msg += data["fee"] + "\n\n"

    if data["age"]:
        msg += "👤 Age Limit\n"
        msg += data["age"] + "\n\n"

    if data["eligibility"]:
        msg += "🎓 Eligibility\n"
        msg += data["eligibility"][:700] + "\n\n"

    if data["selection"]:
        msg += "📝 Selection Process\n"
        msg += data["selection"] + "\n\n"

    msg += "━━━━━━━━━━━━━━━━━━\n"
    msg += f"🔗 Read Full Details\n{link}\n\n"
    msg += "🤖 @jobupdatesbihar"

    return msg
