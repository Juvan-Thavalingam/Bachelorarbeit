from datetime import datetime
from plugins.email.utils import extract_emails_from_text, insert_data_in_email_columns, generate_empty_email_entry
import requests
import random
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X...)",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F)..."
]

SKIP_SUFFIXES = (
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".zip", ".rar", ".7z",
    ".mp4", ".mp3", ".avi", ".mov",
    ".css", ".js", ".ico", ".exe", ".dmg"
)

def extract_emails_from_url(waybackmachine_timestamp, url, columns):
    archive_url = f"{waybackmachine_timestamp}/{url}"
    logger = logging.getLogger(__name__)
    if url.lower().endswith(SKIP_SUFFIXES):
        logger.info(f"⏩ URL übersprungen wegen Dateiendung: {url}")
        return []
    logger.info(f"🔎 Starte Extraktion für URL: {archive_url}")
    try:
        archive_url = f"http://web.archive.org/web/{archive_url}"
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(archive_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Fehler {response.status_code} bei {archive_url}")
            logger.info(f"🔎 Fehler und geht gar nicht text holen: {archive_url}")
            return []

        valid_emails = extract_emails_from_text(response.text)
        emails_with_details = []
        for valid_email in valid_emails:
            formatted_date = datetime.strptime(waybackmachine_timestamp[:8], "%Y%m%d").date().isoformat()
            emails_with_details.append(insert_data_in_email_columns(columns, valid_email, formatted_date))

        if not emails_with_details:
            return [generate_empty_email_entry(columns)]

        return emails_with_details
    except requests.exceptions.RequestException:
        print(f"⚠️ Netzwerkfehler bei: {archive_url}")
        return []
