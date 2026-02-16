import re
from datetime import date
from config import NO_DATA_FOUND_TEXT

PHONE_REGEX = re.compile(
    r"(\+41\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}|\b0\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b|\b0041\d{2}\d{3}\d{2}\d{2}\b)"
)

def normalize_phone_number(phone: str) -> str:
    phone = phone.replace(" ", "").replace("-", "").replace("/", "").strip()
    if phone.startswith("0041"):
        phone = "+" + phone[2:]
    elif phone.startswith("0"):
        phone = "+41" + phone[1:]
    return phone

def is_valid_swiss_number(phone: str) -> bool:
    return phone.startswith("+41") and not phone.startswith("+4100")

def extract_phone_numbers(text: str) -> set[str]:
    raw = set(PHONE_REGEX.findall(text))
    return {
        normalize_phone_number(n)
        for n in raw
        if is_valid_swiss_number(normalize_phone_number(n))
    }


def insert_data_in_phone_columns(columns, phone, date_database):
    if date_database and len(date_database) == 8:
        date_database = f"{date_database[:4]}-{date_database[4:6]}-{date_database[6:]}"
    phone_detail = {
        columns[0]: phone,
        columns[1]: NO_DATA_FOUND_TEXT,
        columns[2]: date_database,
        columns[3]: date.today().isoformat(),
    }
    return phone_detail

def generate_fallback_phone_entry(columns):
    """
    Gibt einen Fallback-Eintrag zurück, wenn keine Telefonnummer gefunden wurde.
    """
    return [{
        columns[0]: NO_DATA_FOUND_TEXT,
        columns[1]: NO_DATA_FOUND_TEXT,
        columns[2]: "0000-00-00",
        columns[3]: date.today().isoformat()
    }]