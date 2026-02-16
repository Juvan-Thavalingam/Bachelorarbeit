from whois import whois
from plugins.phone.utils import extract_phone_numbers, insert_data_in_phone_columns, generate_fallback_phone_entry
import logging
from datetime import date

logger = logging.getLogger(__name__)

def get_whois_phone_numbers(domain, columns):
    try:
        data = whois(domain)
        all_text = str(data)
        numbers = extract_phone_numbers(all_text)
        if numbers:
            logger.info(f"📞 WHOIS: {len(numbers)} Nummer(n) gefunden")
        whois_date = date.today().isoformat()
        structured_phone = [
            insert_data_in_phone_columns(columns, number, whois_date)
            for number in numbers
        ]
        return structured_phone if structured_phone else generate_fallback_phone_entry(columns)
    except Exception as e:
        logger.error(f"⚠️ Fehler bei WHOIS: {e}")
        return generate_fallback_phone_entry(columns)
