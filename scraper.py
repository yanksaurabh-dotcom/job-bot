import os
import json
import time
import html
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HISTORY_FILE = "posted_jobs.json"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Fast sites first
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
                content = json.load(f)
                return set(content)
        except Exception as e:
            print(f"Error loading history: {e}", flush=True)
    return set()

def save_posted_history(posted_links):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(posted_links), f, indent=2)

def detect_post_type(title, url):
    text = (title + " " + url).lower()
    if any(k in text for k in ["result", "merit list", "cut off", "score card"]):
        return "📊 RESULT / MERIT LIST", "#Result #MeritList"
    elif any(k in text for k in ["admit card", "hall ticket", "exam date", "city"]):
        return "🎟️ ADMIT CARD / EXAM NOTICE", "#AdmitCard #ExamDate"
    elif any(k in text for k in ["answer key", "omr"]):
        return "🔑 ANSWER KEY", "#AnswerKey"
    elif any(k in text for k in ["scholarship", "pms", "medhasoft"]):
        return "💰 SCHOLARSHIP UPDATE", "#Scholarship #BiharScholarship"
    elif any(k in text for k in ["admission", "counselling", "spot"]):
        return "🎓 ADMISSION NOTICE", "#Admission #Counselling"
    else:
        return "💼 LATEST JOB RECRUITMENT", "#BiharJob #SarkariNaukri"

def send_telegram_message(title, site_name, link):
    category, hashtags = detect_post_type(title, link)

    safe_title = html.escape(title)
    safe_site = html.escape(site_name)
    safe_link = html.escape(link)

    message = f"""<b>{category}</b>
📢 <b>{safe_title}</b>

🏢 <b>Source:</b> {safe_site}

🔗 <b>Direct Link:</b>
<a href="{safe_link}">Click Here for Details / Apply</a>

#BiharJobs {hashtags}"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 200:
            print(f"✅ Posted: {title[:40]}", flush=True)
            return True
        else:
            print(f"❌ Telegram Error ({res.status_code}): {res.text}", flush=True)
            return False
    except Exception as e:
        print(f"❌ Network Error: {e}", flush=True)
        return False

def run_scraper():
    posted_links = load_posted_history()
    print(f"Loaded {len(posted_links)} saved links.", flush=True)
    new_count = 0

    for site in SITES_CONFIG:
        print(f"🔍 Scanning: {site['name']}...", flush=True)
        try:
            # Fast 5s timeout so slow university servers skip quickly
            resp = requests.get(site["url"], headers=HEADERS, timeout=(3, 5))
            if resp.status_code != 200:
                print(f"⚠️ Could not open {site['name']}", flush=True)
                continue

            soup = BeautifulSoup(resp.content, "lxml")
            site_new_items = 0

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"].strip()

                if len(title) < 15 or len(title) > 160:
                    continue

                if any(junk in title.lower() for junk in JUNK_KEYWORDS):
                    continue

                full_url = urljoin(site["url"], href)

                if full_url not in posted_links:
                    success = send_telegram_message(title, site["name"], full_url)
                    if success:
                        posted_links.add(full_url)
                        new_count += 1
                        site_new_items += 1
                        time.sleep(1)
                        
                        if site_new_items >= 2:
                            break

        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout: {site['name']} is slow, skipping...", flush=True)
        except Exception as e:
            print(f"❌ Error scanning {site['name']}: {e}", flush=True)

    if new_count > 0:
        save_posted_history(posted_links)
        print(f"🎉 Done! Sent {new_count} posts.", flush=True)
    else:
        print("ℹ️ No new posts.", flush=True)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing BOT_TOKEN or CHAT_ID", flush=True)
    else:
        run_scraper()
