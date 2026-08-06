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

# 8 Target Websites
SITES_CONFIG = [
    {"name": "Sarkari Result", "url": "https://sarkariresult.com.cm/"},
    {"name": "Bihar Job Portal", "url": "https://www.biharjobportal.com/"},
    {"name": "Free Job Portal", "url": "https://freejobportal.in/"},
    {"name": "Scholarship Bihar", "url": "https://scholarshipbihar.in/"},
    {"name": "Magadh University", "url": "https://www.magadhuniversity.ac.in/"},
    {"name": "Patna University", "url": "https://www.pup.ac.in/"},
    {"name": "IGNOU", "url": "https://www.ignou.ac.in/"}
]

# Keywords to ignore (Junk/Navigation links)
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
            print(f"History load error: {e}", flush=True)
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

def send_telegram_post(title, site_name, link):
    category, hashtags = detect_post_type(title, link)

    # Safe HTML escaping
    safe_title = html.escape(title)
    safe_site = html.escape(site_name)
    safe_link = html.escape(link)

    message = f"""<b>{category}</b>
📢 <b>{safe_title}</b>

🏢 <b>Source:</b> {safe_site}

🔗 <b>Direct Link:</b>
<a href="{safe_link}">Click Here for Full Details / Apply</a>

#BiharJobs {hashtags}"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        res = requests.post(url, json=payload, timeout=8)
        if res.status_code == 200:
            print(f"✅ Successfully Posted: {title[:40]}", flush=True)
            return True
        else:
            print(f"❌ Telegram API Error ({res.status_code}): {res.text}", flush=True)
            return False
    except Exception as e:
        print(f"❌ Send Failed: {e}", flush=True)
        return False

def run_automation():
    posted_links = load_posted_history()
    print(f"Loaded {len(posted_links)} previously posted links.", flush=True)
    new_count = 0

    for site in SITES_CONFIG:
        print(f"🔍 Scanning: {site['name']}...", flush=True)
        try:
            resp = requests.get(site["url"], headers=HEADERS, timeout=(3, 5))
            if resp.status_code != 200:
                print(f"⚠️ Skip: {site['name']} status {resp.status_code}", flush=True)
                continue

            soup = BeautifulSoup(resp.content, "lxml")
            site_posted = 0

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"].strip()

                if len(title) < 18 or len(title) > 160:
                    continue

                if any(junk in title.lower() for junk in JUNK_KEYWORDS):
                    continue

                full_url = urljoin(site["url"], href)

                if full_url not in posted_links:
                    success = send_telegram_post(title, site["name"], full_url)
                    if success:
                        posted_links.add(full_url)
                        new_count += 1
                        site_posted += 1
                        time.sleep(1.5)
                        
                        # Har site se maximum 2 updates per run
                        if site_posted >= 2:
                            break

        except requests.exceptions.Timeout:
            print(f"⏱️ Skip: {site['name']} timeout", flush=True)
        except Exception as e:
            print(f"❌ Error scanning {site['name']}: {e}", flush=True)

    if new_count > 0:
        save_posted_history(posted_links)
        print(f"🎉 Completed! Posted {new_count} updates to Telegram.", flush=True)
    else:
        print("ℹ️ No new updates found in this run.", flush=True)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing BOT_TOKEN or CHAT_ID", flush=True)
    else:
        run_automation()
