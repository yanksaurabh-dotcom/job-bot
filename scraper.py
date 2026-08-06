import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HISTORY_FILE = "posted_jobs.json"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@jobupdatesbihar")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SITES_CONFIG = [
    {"name": "BSUSC / Govt Portal", "url": "https://bsusc.bihar.gov.in/", "icon": "🎓"},
    {"name": "Sarkari Result", "url": "https://sarkariresult.com.cm/", "icon": "💼"},
    {"name": "Bihar Job Portal", "url": "https://www.biharjobportal.com/", "icon": "📌"},
    {"name": "Free Job Portal", "url": "https://freejobportal.in/", "icon": "🎯"},
    {"name": "Scholarship Bihar", "url": "https://scholarshipbihar.in/", "icon": "💰"},
    {"name": "Magadh University", "url": "https://www.magadhuniversity.ac.in/", "icon": "🏛️"},
    {"name": "Patna University", "url": "https://www.pup.ac.in/", "icon": "🏛️"},
    {"name": "IGNOU", "url": "https://www.ignou.ac.in/", "icon": "📚"}
]

def load_posted_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Error loading history: {e}")
    return set()

def save_posted_history(posted_links):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(posted_links), f, indent=2)

def send_rich_telegram_post(title, site_name, icon, apply_link, posts_count="", dates="", fee="", age="", qual=""):
    """Creates and sends a rich formatted HTML post to Telegram."""
    
    # Build optional sections dynamically
    details_block = ""
    if dates:
        details_block += f"📅 <b>IMPORTANT DATES:</b>\n{dates}\n\n"
    if fee:
        details_block += f"💰 <b>APPLICATION FEE:</b> {fee}\n\n"
    if age:
        details_block += f"🎂 <b>AGE LIMIT:</b> {age}\n\n"
    if qual:
        details_block += f"🎓 <b>QUALIFICATION:</b>\n{qual}\n\n"

    message = f"""🔥 <b>{title.upper()}</b> 🔥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{f'🔢 <b>Total Vacancies:</b> {posts_count}' if posts_count else ''}
🏢 <b>Source / Authority:</b> {site_name}

{details_block}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>IMPORTANT LINKS:</b>

🔗 <b>Apply Online / Notice Details:</b>
<a href="{apply_link}">👉 Click Here to Apply / Read Details</a>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📢 <b>Daily Job Updates Ke Liye Join Karein:</b>
📲 <b>Join Channel:</b> {CHAT_ID}

#BiharJobs #SarkariNaukri #LatestJob #{site_name.replace(' ', '')}"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        res = requests.post(url, json=payload, timeout=12)
        if res.status_code == 200:
            print(f"Successfully posted: {title[:40]}")
            return True
        else:
            print(f"Telegram API Error: {res.text}")
            return False
    except Exception as e:
        print(f"Failed to send message: {e}")
        return False

def scrape_and_process():
    posted_links = load_posted_history()
    new_count = 0

    for site in SITES_CONFIG:
        print(f"Scanning {site['name']}...")
        try:
            resp = requests.get(site["url"], headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.content, "lxml")

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"].strip()

                if len(title) < 15 or len(title) > 150:
                    continue

                full_url = urljoin(site["url"], href)

                if full_url not in posted_links:
                    success = send_rich_telegram_post(
                        title=title,
                        site_name=site["name"],
                        icon=site["icon"],
                        apply_link=full_url
                    )
                    if success:
                        posted_links.add(full_url)
                        new_count += 1
                        time.sleep(2)
        except Exception as e:
            print(f"Error scraping {site['name']}: {e}")

    if new_count > 0:
        save_posted_history(posted_links)
        print(f"Done! Posted {new_count} new updates.")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN environment variable missing!")
    else:
        scrape_and_process()
