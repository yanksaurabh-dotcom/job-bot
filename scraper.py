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
    "help", "admin", "sign in", "sign up", "whatsapp", "telegram", "twitter", "question:"
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

def detect_post_type(title, url):
    """Detects type of post: JOB, RESULT, ADMIT_CARD, ANSWER_KEY, SCHOLARSHIP, ADMISSION"""
    text = (title + " " + url).lower()
    if any(k in text for k in ["result", "merit list", "cut off", "score card"]):
        return "RESULT", "📊 RESULT / MERIT LIST", "#Result #MeritList"
    elif any(k in text for k in ["admit card", "hall ticket", "exam date", "city"]):
        return "ADMIT_CARD", "🎟️ ADMIT CARD / EXAM NOTICE", "#AdmitCard #ExamDate"
    elif any(k in text for k in ["answer key", "omr"]):
        return "ANSWER_KEY", "🔑 ANSWER KEY", "#AnswerKey"
    elif any(k in text for k in ["scholarship", "pms", "medhasoft"]):
        return "SCHOLARSHIP", "💰 SCHOLARSHIP UPDATE", "#Scholarship #BiharScholarship"
    elif any(k in text for k in ["admission", "counselling", "spot"]):
        return "ADMISSION", "🎓 ADMISSION NOTICE", "#Admission #Counselling"
    else:
        return "JOB", "💼 LATEST JOB RECRUITMENT", "#BiharJob #SarkariNaukri"

def scrape_inner_details(post_url, post_type):
    """Scrapes inner page only if it is a JOB or SCHOLARSHIP."""
    details = {
        "dates": [],
        "fee": [],
        "age": [],
        "apply_link": "",
        "pdf_link": ""
    }
    
    try:
        resp = requests.get(post_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return details

        soup = BeautifulSoup(resp.content, "lxml")

        # Action links
        for a in soup.find_all("a", href=True):
            a_text = a.get_text(strip=True).lower()
            href = urljoin(post_url, a["href"].strip())

            if any(x in href.lower() for x in ["facebook", "telegram", "whatsapp", "twitter", "youtube"]):
                continue

            if any(k in a_text for k in ["apply online", "apply link", "registration", "click here to apply", "online form"]):
                if not details["apply_link"] and href != post_url:
                    details["apply_link"] = href
            elif any(k in a_text for k in ["notification", "notice", "pdf", "download notification"]):
                if not details["pdf_link"] and href != post_url:
                    details["pdf_link"] = href

        # Extract structured details for Jobs only
        if post_type in ["JOB", "SCHOLARSHIP"]:
            for tr in soup.find_all("tr"):
                row_text = tr.get_text(" | ", strip=True)
                row_lower = row_text.lower()
                
                if "question:" in row_lower or "answer:" in row_lower:
                    continue
                
                if any(k in row_lower for k in ["start date", "last date", "apply date"]):
                    if len(row_text) < 120 and row_text not in details["dates"]:
                        details["dates"].append(row_text)
                elif any(k in row_lower for k in ["fee", "rs.", "₹"]):
                    if len(row_text) < 120 and row_text not in details["fee"]:
                        details["fee"].append(row_text)
                elif any(k in row_lower for k in ["age limit", "minimum age", "maximum age"]):
                    if len(row_text) < 120 and row_text not in details["age"]:
                        details["age"].append(row_text)

        if not details["apply_link"]:
            details["apply_link"] = post_url

    except Exception as e:
        print(f"Error scraping inner page {post_url}: {e}")

    return details

def send_smart_telegram_post(title, site_name, post_url):
    post_type, category, hashtags = detect_post_type(title, post_url)
    inner = scrape_inner_details(post_url, post_type)

    # Clean channel handle formatting
    channel_branding = CHAT_ID if CHAT_ID.startswith("@") else "Telegram Channel"

    # BUILD MESSAGE DYNAMICALLY BASED ON TYPE
    if post_type in ["RESULT", "ADMIT_CARD", "ANSWER_KEY"]:
        # Clean & Minimal Layout for Results / Admit Cards / Answer Keys
        message = f"""<b>{category}</b>
📢 <b>{title.upper()}</b>

🏢 <b>Source:</b> {site_name}

🔗 <b>Direct Link:</b>
<a href="{inner['apply_link']}">👉 Click Here to Check / Download</a>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📲 <b>Join For Latest Updates:</b> {channel_branding}

{hashtags}"""

    else:
        # Detailed Layout for Jobs & Scholarships (ONLY IF REAL DATA EXISTS)
        dynamic_blocks = ""
        
        if inner["dates"]:
            dates_text = "\n".join([f"▪️ {d}" for d in inner["dates"][:3]])
            dynamic_blocks += f"\n📅 <b>IMPORTANT DATES:</b>\n{dates_text}\n"
            
        if inner["fee"]:
            fee_text = "\n".join([f"▪️ {f}" for f in inner["fee"][:2]])
            dynamic_blocks += f"\n💰 <b>APPLICATION FEE:</b>\n{fee_text}\n"
            
        if inner["age"]:
            age_text = "\n".join([f"▪️ {a}" for a in inner["age"][:2]])
            dynamic_blocks += f"\n🎂 <b>AGE LIMIT:</b>\n{age_text}\n"

        pdf_block = f"📄 <a href=\"{inner['pdf_link']}\">Download Notification PDF</a>\n" if inner["pdf_link"] else ""

        message = f"""<b>{category}</b>
🔥 <b>{title.upper()}</b> 🔥

🏢 <b>Source:</b> {site_name}
{dynamic_blocks}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>DIRECT LINKS:</b>
{pdf_block}🔗 <a href="{inner['apply_link']}">Click Here to Apply / Read Notice</a>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📲 <b>Join For Daily Updates:</b> {channel_branding}

{hashtags}"""

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
            print(f"Posted: {title[:40]}")
            return True
        else:
            print(f"Telegram API Error: {res.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_scraper():
    posted_links = load_posted_history()
    new_count = 0

    for site in SITES_CONFIG:
        print(f"Scanning: {site['name']}...")
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
                    success = send_smart_telegram_post(title, site["name"], full_url)
                    if success:
                        posted_links.add(full_url)
                        new_count += 1
                        time.sleep(2)
        except Exception as e:
            print(f"Error scanning {site['name']}: {e}")

    if new_count > 0:
        save_posted_history(posted_links)
        print(f"Completed! Sent {new_count} clean posts.")
    else:
        print("No new updates.")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing.")
    else:
        run_scraper()
