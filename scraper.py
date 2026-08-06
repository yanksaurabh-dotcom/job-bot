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

# Targeted Sites
SITES_CONFIG = [
    {"name": "BSUSC", "url": "https://bsusc.bihar.gov.in/", "tag": "BSUSC"},
    {"name": "Sarkari Result", "url": "https://sarkariresult.com.cm/", "tag": "SarkariResult"},
    {"name": "Bihar Job Portal", "url": "https://www.biharjobportal.com/", "tag": "BiharJobPortal"},
    {"name": "Free Job Portal", "url": "https://freejobportal.in/", "tag": "FreeJobPortal"},
    {"name": "Scholarship Bihar", "url": "https://scholarshipbihar.in/", "tag": "ScholarshipBihar"},
    {"name": "Magadh University", "url": "https://www.magadhuniversity.ac.in/", "tag": "MagadhUniv"},
    {"name": "Patna University", "url": "https://www.pup.ac.in/", "tag": "PatnaUniv"},
    {"name": "IGNOU", "url": "https://www.ignou.ac.in/", "tag": "IGNOU"}
]

# Words to STRICTLY ignore
JUNK_KEYWORDS = [
    "forgot", "password", "voter", "selfi", "login", "register", "contact", 
    "privacy", "disclaimer", "home", "feedback", "faq", "sitemap", "search", 
    "terms", "help", "admin", "user", "sign in", "sign up", "download app",
    "whatsapp", "facebook", "twitter", "instagram", "youtube", "skip to content",
    "read more", "view more", "click here"
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

def send_compact_telegram_post(title, site_name, site_tag, link):
    """Sends a clean, compact and short Telegram post."""
    
    # Clean Compact Post Format
    message = f"""<b>📢 {title}</b>

🏢 <b>Source:</b> {site_name}
🔗 <b>Link:</b> <a href="{link}">Click Here for Details</a>

#BiharJobs #{site_tag}"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"Posted: {title}")
            return True
        else:
            print(f"Telegram API Error: {res.text}")
            return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def scrape_and_process():
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

                # Filter short or too long text
                if len(title) < 20 or len(title) > 160:
                    continue

                # Filter junk links
                title_lower = title.lower()
                if any(junk in title_lower for junk in JUNK_KEYWORDS):
                    continue

                full_url = urljoin(site["url"], href)

                if full_url not in posted_links:
                    success = send_compact_telegram_post(
                        title=title,
                        site_name=site["name"],
                        site_tag=site["tag"],
                        link=full_url
                    )
                    if success:
                        posted_links.add(full_url)
                        new_count += 1
                        time.sleep(1.5)
        except Exception as e:
            print(f"Error scraping {site['name']}: {e}")

    if new_count > 0:
        save_posted_history(posted_links)
        print(f"Done! Sent {new_count} clean posts.")
    else:
        print("No new updates found.")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing.")
    else:
        scrape_and_process()
