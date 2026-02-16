from whois import whois
from plugins.email.utils import insert_data_in_email_columns, generate_empty_email_entry
from datetime import date

def get_whois_emails(domain, columns):
    try:
        data = whois(domain)
        raw_emails = []
        structured_emails = []

        if isinstance(data.emails, list):
            raw_emails = set(data.emails)
        elif isinstance(data.emails, str):
            raw_emails = {data.emails}

        whois_date = date.today().isoformat()

        for email in raw_emails:
            structured_emails.append(insert_data_in_email_columns(columns, email, whois_date))

        if not structured_emails:
            return [generate_empty_email_entry(columns)]

        return structured_emails

    except:
        return [generate_empty_email_entry(columns)]

