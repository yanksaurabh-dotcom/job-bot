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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# Full List of Category Sub-Pages for All Portals
TARGET_CATEGORIES = [
    # --- Sarkari Result ---
    {"site": "Sarkari Result", "url": "https://sarkariresult.com.cm/"},
    {"site": "Sarkari Result", "url": "https://sarkariresult.com.cm/latest-jobs/"},
    {"site": "Sarkari Result", "url": "https://sarkariresult.com.cm/result/"},
    {"site": "Sarkari Result", "url": "https://sarkariresult.com.cm/admit-card/"},
    {"site": "Sarkari Result", "url": "https://sarkariresult.com.cm/answer-key/"},
    {"site": "Sarkari Result", "url": "https://sarkariresult.com.cm/admission/"},

    # --- Bihar Job Portal ---
    {"site": "Bihar Job Portal", "url": "https://www.biharjobportal.com/"},
    {"site": "Bihar Job Portal", "url": "https://www.biharjobportal.com/category/bihar-job/"},
    {"site": "Bihar Job Portal", "url": "https://www.biharjobportal.com/category/result/"},
    {"site": "Bihar Job Portal", "url": "https://www.biharjobportal.com/category/admit-card/"},
    {"site": "Bihar Job Portal", "url": "https://www.biharjobportal.com/category/scholarship/"},
    {"site": "Bihar Job Portal", "url": "https://www.biharjobportal.com/category/admission/"},
    {"site": "Bihar Job Portal", "url": "https://www.biharjobportal.com/category/answer-key/"},

    # --- Free Job Portal ---
    {"site": "Free Job Portal", "url": "https://freejobportal.in/"},
    {"site": "Free Job Portal", "url": "https://freejobportal.in/category/latest-job/"},
    {"site": "Free Job Portal", "url": "https://freejobportal.in/category/results/"},
    {"site": "Free Job Portal", "url": "https://freejobportal.in/category/admit-cards/"},

    # --- Scholarship Bihar ---
    {"site": "Scholarship Bihar", "url": "https://scholarshipbihar.in/"},
    {"site": "Scholarship Bihar", "url": "https://scholarshipbihar.in/graduation-scholarship/"},
    {"site": "Scholarship Bihar", "url": "https://scholarshipbihar.in/10th-pass-scholarship/"},
    {"site": "Scholarship Bihar", "url": "https://scholarshipbihar.in/12th-pass-scholarship/"},

    # --- Universities ---
    {"site": "Magadh University", "url": "https://www.magadhuniversity.ac.in/"},
    {"site": "Patna University", "url": "https://www.pup.ac.in/"},
    {"site": "IGNOU", "url": "https://www.ignou.ac.in/"}
]

JUNK_KEYWORDS = [
    "forgot", "password", "voter", "selfi", "login", "register", "contact", 
    "privacy", "disclaimer", "home", "feedback", "faq", "sitemap", "terms", 
    "help", "admin", "sign in", "sign up", "whatsapp", "telegram", "twitter",
    "facebook", "instagram", "youtube", "about us", "copyright", "dmca"
]

def load_posted_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Error loading history file: {e}", flush=True)
    return set()

def save_posted_history(posted_links):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(list(posted_links), f, indent=2)
    except Exception as e:
        print(f"Error saving history file: {e}", flush=True)

def detect_category(title, url):
    text = (title + " " + url).lower()
    if any(k in text for k in ["result", "merit list", "cut off", "score card", "marks"]):
        return "RESULT", "📊 RESULT & MERIT LIST", "#Result #MeritList"
    elif any(k in text for k in ["admit card", "hall ticket", "exam date", "city intimation"]):
        return "ADMIT_CARD", "🎟️ ADMIT CARD & EXAM NOTICE", "#AdmitCard #ExamDate"
    elif any(k in text for k in ["answer key", "omr sheet", "objection"]):
        return "ANSWER_KEY", "🔑 ANSWER KEY & OMR", "#AnswerKey"
    elif any(k in text for k in ["scholarship", "pms", "medhasoft", "kanya utthan"]):
        return "SCHOLARSHIP", "💰 SCHOLARSHIP UPDATE", "#Scholarship #BiharScholarship"
    elif any(k in text for k in ["admission", "counselling", "spot", "allotment"]):
        return "ADMISSION", "🎓 ADMISSION & COUNSELLING", "#Admission #Counselling"
    else:
        return "JOB", "💼 LATEST JOB RECRUITMENT", "#BiharJob #SarkariNaukri"

def deep_scrape_inner_page(post_url, post_type):
    """Deep scrapes inner job page for dates, fee, age limit, vacancies, and direct links."""
    data = {
        "dates": [],
        "fee": [],
        "age": [],
        "vacancies": "",
        "apply_link": "",
        "pdf_link": "",
        "official_site": ""
    }
    
    try:
        resp = requests.get(post_url, headers=HEADERS, timeout=(4, 7))
        if resp.status_code != 200:
            return data

        soup = BeautifulSoup(resp.content, "lxml")

        # Extract direct action links
        for a in soup.find_all("a", href=True):
            a_text = a.get_text(strip=True).lower()
            href = urljoin(post_url, a["href"].strip())

            if any(x in href.lower() for x in ["facebook", "telegram", "whatsapp", "twitter", "youtube", "instagram"]):
                continue

            if any(k in a_text for k in ["apply online", "online form", "click here to apply", "registration"]):
                if not data["apply_link"] and href != post_url:
                    data["apply_link"] = href
            elif any(k in a_text for k in ["download notification", "official notice", "notification pdf", "advertisement"]):
                if not data["pdf_link"] and href != post_url:
                    data["pdf_link"] = href
            elif any(k in a_text for k in ["official website", "official portal", "home page"]):
                if not data["official_site"]:
                    data["official_site"] = href

        # Extract structured details for Jobs, Scholarships & Admissions
        if post_type in ["JOB", "SCHOLARSHIP", "ADMISSION"]:
            for tr in soup.find_all("tr"):
                row_text = tr.get_text(" | ", strip=True)
                row_lower = row_text.lower()
                
                if "question:" in row_lower or "answer:" in row_lower:
                    continue

                if any(k in row_lower for k in ["start date", "last date", "apply date", "interview date", "merit list date"]):
                    if len(row_text) < 140 and row_text not in data["dates"]:
                        data["dates"].append(row_text)
                elif any(k in row_lower for k in ["fee", "rs.", "₹", "general", "obc", "sc/st"]):
                    if len(row_text) < 140 and row_text not in data["fee"]:
                        data["fee"].append(row_text)
                elif any(k in row_lower for k in ["age limit", "minimum age", "maximum age", "years"]):
                    if len(row_text) < 140 and row_text not in data["age"]:
                        data["age"].append(row_text)
                elif any(k in row_lower for k in ["total post", "total vacancy", "number of post"]):
                    if not data["vacancies"] and len(row_text) < 100:
                        data["vacancies"] = row_text

        if not data["apply_link"]:
            data["apply_link"] = post_url

    except Exception as e:
        print(f"Error deep scraping {post_url}: {e}", flush=True)

    return data

def build_and_send_post(title, site_name, post_url):
    post_type, category_header, hashtags = detect_category(title, post_url)
    inner_data = deep_scrape_inner_page(post_url, post_type)

    safe_title = html.escape(title)
    safe_site = html.escape(site_name)

    # Dynamic Post Layout without fake placeholders
    if post_type in ["RESULT", "ADMIT_CARD", "ANSWER_KEY"]:
        message = f"""<b>{category_header}</b>
📢 <b>{safe_title.upper()}</b>

🏢 <b>Source:</b> {safe_site}

🔗 <b>Direct Link:</b>
<a href="{html.escape(inner_data['apply_link'])}">👉 Click Here to Check / Download</a>

#BiharJobs {hashtags}"""

    else:
        dynamic_blocks = ""
        
        if inner_data["vacancies"]:
            dynamic_blocks += f"\n🔢 <b>TOTAL VACANCIES:</b> {html.escape(inner_data['vacancies'])}\n"

        if inner_data["dates"]:
            dates_formatted = "\n".join([f"▪️ {html.escape(d)}" for d in inner_data["dates"][:3]])
            dynamic_blocks += f"\n📅 <b>IMPORTANT DATES:</b>\n{dates_formatted}\n"

        if inner_data["fee"]:
            fee_formatted = "\n".join([f"▪️ {html.escape(f)}" for f in inner_data["fee"][:2]])
            dynamic_blocks += f"\n💰 <b>APPLICATION FEE:</b>\n{fee_formatted}\n"

        if inner_data["age"]:
            age_formatted = "\n".join([f"▪️ {html.escape(a)}" for a in inner_data["age"][:2]])
            dynamic_blocks += f"\n🎂 <b>AGE LIMIT & ELIGIBILITY:</b>\n{age_formatted}\n"

        links_section = ""
        if inner_data["pdf_link"]:
            links_section += f"📄 <a href=\"{html.escape(inner_data['pdf_link'])}\">Download Official Notification PDF</a>\n"
        
        links_section += f"🔗 <a href=\"{html.escape(inner_data['apply_link'])}\">Click Here for Direct Apply / Details</a>\n"
        
        if inner_data["official_site"]:
            links_section += f"🌐 <a href=\"{html.escape(inner_data['official_site'])}\">Visit Official Portal</a>\n"

        message = f"""<b>{category_header}</b>
🔥 <b>{safe_title.upper()}</b> 🔥

🏢 <b>Source:</b> {safe_site}
{dynamic_blocks}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>DIRECT LINKS:</b>
{links_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
            print(f"  ✅ Posted: {title[:40]}", flush=True)
            return True
        else:
            print(f"  ❌ Telegram Error ({res.status_code}): {res.text}", flush=True)
            return False
    except Exception as e:
        print(f"  ❌ Error sending to Telegram: {e}", flush=True)
        return False

def run_scraper_engine():
    posted_links = load_posted_history()
    print(f"Loaded {len(posted_links)} previously posted links from {HISTORY_FILE}.", flush=True)
    total_new_posted = 0

    for category_item in TARGET_CATEGORIES:
        site_name = category_item["site"]
        site_url = category_item["url"]
        
        print(f"\n🔍 Scanning Category Page: {site_name} -> ({site_url})...", flush=True)
        try:
            resp = requests.get(site_url, headers=HEADERS, timeout=(4, 7))
            if resp.status_code != 200:
                print(f"  ⚠️ Skipping {site_url} (Status: {resp.status_code})", flush=True)
                continue

            soup = BeautifulSoup(resp.content, "lxml")
            site_new_count = 0
            links_checked = 0

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"].strip()

                if len(title) < 14 or len(title) > 170:
                    continue

                if any(junk in title.lower() for junk in JUNK_KEYWORDS):
                    continue

                full_url = urljoin(site_url, href)
                links_checked += 1

                if full_url not in posted_links:
                    success = build_and_send_post(title, site_name, full_url)
                    if success:
                        posted_links.add(full_url)
                        total_new_posted += 1
                        site_new_count += 1
                        time.sleep(1.5)
                        
                        # Max 2 posts per category sub-page per run
                        if site_new_count >= 2:
                            break

            print(f"  ℹ️ Evaluated {links_checked} links, {site_new_count} new posts sent from this section.", flush=True)

        except requests.exceptions.Timeout:
            print(f"  ⏱️ Skipped: {site_url} timed out.", flush=True)
        except Exception as e:
            print(f"  ❌ Error scanning {site_url}: {e}", flush=True)

    if total_new_posted > 0:
        save_posted_history(posted_links)
        print(f"\n🎉 Multi-Category Automation Completed! Total {total_new_posted} new posts delivered.", flush=True)
    else:
        print("\nℹ️ Automation Completed. No new posts found across all category sections.", flush=True)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing.", flush=True)
    else:
        run_scraper_engine()
