import requests
import random
import logging
from datetime import datetime
from plugins.phone.utils import extract_phone_numbers, insert_data_in_phone_columns, generate_fallback_phone_entry

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F)..."
]

SKIP_SUFFIXES = (
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".zip", ".rar", ".7z",
    ".mp4", ".mp3", ".avi", ".mov",
    ".css", ".js", ".ico", ".exe", ".dmg"
)

def extract_phone_numbers_from_url(waybackmachine_timestamp, url, columns):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        if url.lower().endswith(SKIP_SUFFIXES):
            logger.info(f"⏩ URL übersprungen wegen Dateiendung: {url}")
            return []

        archive_url = f"http://web.archive.org/web/{waybackmachine_timestamp}/{url}"
        response = requests.get(archive_url, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.warning(f"⚠️ Fehler {response.status_code} bei {archive_url}")
            return []

        valid_phones = extract_phone_numbers(response.text)
        if valid_phones:
            logger.info(f"📞 {len(valid_phones)} Nummer(n) gefunden auf {archive_url}")

        phone_with_details = [
            insert_data_in_phone_columns(columns, valid_phone, datetime.strptime(waybackmachine_timestamp[:8], "%Y%m%d").date().isoformat())
            for valid_phone in valid_phones
        ]

        return phone_with_details if phone_with_details else generate_fallback_phone_entry(columns)

    except requests.exceptions.RequestException:
        logger.error(f"⚠️ Netzwerkfehler bei: {url}")
        return generate_fallback_phone_entry(columns)
