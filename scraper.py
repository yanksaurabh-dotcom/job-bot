import os
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HISTORY_FILE = "posted_jobs.json"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SITES_CONFIG = [
    {"name": "Sarkari Result", "url": "https://sarkariresult.com.cm/"},
    {"name": "Bihar Job Portal", "url": "https://www.biharjobportal.com/"},
    {"name": "Free Job Portal", "url": "https://freejobportal.in/"},
    {"name": "Scholarship Bihar", "url": "https://scholarshipbihar.in/"},
    {"name": "Magadh University", "url": "https://www.magadhuniversity.ac.in/"},
    {"name": "Patna University", "url": "https://www.pup.ac.in/"},
    {"name": "IGNOU", "url": "https://www.ignou.ac.in/"}
]

JUNK_KEYWORDS = [
    "forgot", "password", "voter", "selfi", "login", "register", "contact", 
    "privacy", "disclaimer", "home", "feedback", "faq", "sitemap", "terms", 
    "help", "admin", "sign in", "sign up", "whatsapp", "telegram", "twitter"
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

def detect_category(title, url):
    """Categorizes the post type based on keywords."""
    text = (title + " " + url).lower()
    if "result" in text or "merit list" in text or "cut off" in text or "score" in text:
        return "📊 RESULT & MERIT LIST", "#Result #MeritList"
    elif "admit card" in text or "hall ticket" in text or "exam date" in text or "city" in text:
        return "🎟️ ADMIT CARD / EXAM DATE", "#AdmitCard #ExamNotice"
    elif "answer key" in text or "omr" in text:
        return "🔑 ANSWER KEY", "#AnswerKey"
    elif "scholarship" in text or "pms" in text or "medhasoft" in text:
        return "💰 SCHOLARSHIP UPDATE", "#Scholarship #BiharScholarship"
    elif "admission" in text or "counselling" in text or "spot" in text:
        return "🎓 ADMISSION & COUNSELLING", "#Admission #Counselling"
    else:
        return "💼 LATEST JOB RECRUITMENT", "#BiharJob #SarkariNaukri"

def deep_scrape_inner_page(post_url):
    """Visits the inner page to extract dates, fee, age limit, and direct links."""
    details = {
        "dates": [],
        "fee": [],
        "age": [],
        "apply_link": "",
        "pdf_link": "",
        "official_site": ""
    }
    
    try:
        resp = requests.get(post_url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return details

        soup = BeautifulSoup(resp.content, "lxml")

        # Extract direct action links
        for a in soup.find_all("a", href=True):
            a_text = a.get_text(strip=True).lower()
            href = urljoin(post_url, a["href"].strip())

            if any(x in href.lower() for x in ["facebook", "telegram", "whatsapp", "twitter", "youtube"]):
                continue

            if any(k in a_text for k in ["apply online", "apply link", "registration", "click here to apply", "online form"]):
                if not details["apply_link"] and href != post_url:
                    details["apply_link"] = href
            elif any(k in a_text for k in ["notification", "notice", "pdf", "download notification", "official notice"]):
                if not details["pdf_link"] and href != post_url:
                    details["pdf_link"] = href
            elif any(k in a_text for k in ["official website", "official portal", "home page"]):
                if not details["official_site"]:
                    details["official_site"] = href

        # Extract structured details from table rows
        for tr in soup.find_all("tr"):
            row_text = tr.get_text(" | ", strip=True)
            row_lower = row_text.lower()
            
            if any(k in row_lower for k in ["start date", "last date", "apply date", "exam date"]):
                if len(row_text) < 150 and row_text not in details["dates"]:
                    details["dates"].append(row_text)
            elif any(k in row_lower for k in ["fee", "rs.", "₹", "general", "sc/st"]):
                if len(row_text) < 150 and row_text not in details["fee"]:
                    details["fee"].append(row_text)
            elif any(k in row_lower for k in ["age limit", "minimum age", "maximum age"]):
                if len(row_text) < 150 and row_text not in details["age"]:
                    details["age"].append(row_text)

        if not details["apply_link"]:
            details["apply_link"] = post_url

    except Exception as e:
        print(f"Error deep scraping {post_url}: {e}")

    return details

def send_detailed_telegram_post(title, site_name, post_url):
    """Formats and sends a complete detailed card to Telegram."""
    category, hashtags = detect_category(title, post_url)
    
    # Deep scrape inner page
    inner = deep_scrape_inner_page(post_url)
    
    # Format optional sections
    dates_str = "\n".join([f"▪️ {d}" for d in inner["dates"][:3]]) if inner["dates"] else "▪️ Official Notice me check karein"
    fee_str = "\n".join([f"▪️ {f}" for f in inner["fee"][:2]]) if inner["fee"] else "▪️ Details for fee in official notice"
    age_str = "\n".join([f"▪️ {a}" for a in inner["age"][:2]]) if inner["age"] else "▪️ As per Notification Rules"

    # Direct Action Links Block
    links_block = ""
    if inner["pdf_link"]:
        links_block += f"📄 <b>Notification PDF Link:</b>\n<a href=\"{inner['pdf_link']}\">👉 Download Official Notification PDF</a>\n\n"
    
    links_block += f"🔗 <b>Direct Apply / Details Link:</b>\n<a href=\"{inner['apply_link']}\">👉 Click Here for Direct Link</a>\n\n"
    
    if inner["official_site"]:
        links_block += f"🌐 <b>Official Website:</b>\n<a href=\"{inner['official_site']}\">👉 Visit Official Portal</a>\n\n"

    # Full Message Payload
    message = f"""🔥 <b>{title.upper()}</b> 🔥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 <b>Category:</b> {category}
🏢 <b>Source:</b> {site_name}

📅 <b>IMPORTANT DATES / SCHEDULE:</b>
{dates_str}

💰 <b>APPLICATION FEE DETAILS:</b>
{fee_str}

🎂 <b>AGE LIMIT & ELIGIBILITY:</b>
{age_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>DIRECT ACTION LINKS:</b>

{links_block}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📢 <b>Daily Bihar Job Updates Ke Liye Join Karein:</b>
📲 <b>Join Channel:</b> {CHAT_ID}

{hashtags} #BiharUpdates"""

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
            print(f"Posted Detailed Card: {title[:40]}")
            return True
        else:
            print(f"Telegram API Error: {res.text}")
            return False
    except Exception as e:
        print(f"Failed to send: {e}")
        return False

def run_deep_scraper():
    posted_links = load_posted_history()
    new_count = 0

    for site in SITES_CONFIG:
        print(f"Scanning Homepage: {site['name']}...")
        try:
            resp = requests.get(site["url"], headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.content, "lxml")

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"].strip()

                if len(title) < 18 or len(title) > 160:
                    continue

                if any(junk in title.lower() for junk in JUNK_KEYWORDS):
                    continue

                full_url = urljoin(site["url"], href)

                if full_url not in posted_links:
                    success = send_detailed_telegram_post(title, site["name"], full_url)
                    if success:
                        posted_links.add(full_url)
                        new_count += 1
                        time.sleep(2) # Gap between posts
        except Exception as e:
            print(f"Error scanning {site['name']}: {e}")

    if new_count > 0:
        save_posted_history(posted_links)
        print(f"Success! Posted {new_count} detailed cards.")
    else:
        print("No new updates found.")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing.")
    else:
        run_deep_scraper()
