import os
import re
import logging
from datetime import date
from config import NO_DATA_FOUND_TEXT

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_path = os.path.join(os.path.dirname(__file__), "tlds-alpha-by-domain.txt")

with open(file_path, "r") as f:
    VALID_TLDS = set(
        line.strip().lower() for line in f
        if line.strip() and not line.startswith("#")
    )

def is_valid_email_tld(email: str) -> bool:
    try:
        tld = email.split('.')[-1].lower()
        return tld in VALID_TLDS
    except Exception:
        return False

def extract_emails_from_text(text: str) -> set[str]:
    """
    Findet gültige E-Mails in einem gegebenen Text (Regex + TLD-Filter).
    """
    matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

    logger.info(f"📬 Gefundene Roh-E-Mails: {matches}")

    valid = {m for m in matches if is_valid_email_tld(m)}
    logger.info(f"✅ Gültige nach TLD: {valid}")
    return valid

def insert_data_in_email_columns(columns, email, date_database):
    if date_database and len(date_database) == 8:
        date_database = f"{date_database[:4]}-{date_database[4:6]}-{date_database[6:]}"
    email_detail = {
        columns[0]: email,
        columns[1]: NO_DATA_FOUND_TEXT,
        columns[2]: date_database,
        columns[3]: date.today().isoformat(),
    }
    return email_detail

def generate_empty_email_entry(columns):
    return {
        columns[0]: NO_DATA_FOUND_TEXT,
        columns[1]: NO_DATA_FOUND_TEXT,
        columns[2]: "0000-00-00",
        columns[3]: date.today().isoformat()
    }