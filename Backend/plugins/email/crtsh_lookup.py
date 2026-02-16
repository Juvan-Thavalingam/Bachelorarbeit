from config import NO_DATA_FOUND_TEXT
import requests
from plugins.email.utils import extract_emails_from_text, insert_data_in_email_columns, generate_empty_email_entry

CRT_SH_API = "https://crt.sh/?q=%25.{domain}&output=json"

def get_crtsh_emails(domain, columns):
    try:
        r = requests.get(CRT_SH_API.format(domain=domain), timeout=10)
        if r.status_code != 200:
            return []

        data = r.json()
        emails = []

        for entry in data:
            text = entry.get("name_value", "")
            valid_emails = extract_emails_from_text(text)
            crtsh_date =  entry.get("entry_timestamp", NO_DATA_FOUND_TEXT).split("T")[0]
            for valid_email in valid_emails:
                emails.append(insert_data_in_email_columns(columns, valid_email, crtsh_date))

        if not emails:
            emails.append(generate_empty_email_entry(columns))

        return emails
    except:
        return [generate_empty_email_entry(columns)]