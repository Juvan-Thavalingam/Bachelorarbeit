from plugins.base_plugin import BasePlugin
from plugins.email.utils import generate_empty_email_entry
from plugins.email.dehashed_lookup import is_leaked
from database import create_standard_table, insert_record, get_db_connection
from config import NO_DATA_SCANNED_TEXT
from plugins.email.waybackmachine_lookup import extract_emails_from_url
from plugins.email.whois_lookup import get_whois_emails
from plugins.email.crtsh_lookup import get_crtsh_emails
from plugins.endpoint.endpoint_plugin import Plugin as EndpointPlugin
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import json
import time
import random

SLEEP = random.randint(7, 15)
endpoint_columns = EndpointPlugin().columns
endpoint_url = endpoint_columns[0]
endpoint_snapshot = endpoint_columns[1]

class Plugin(BasePlugin):

    def __init__(self):
        self.name = "E-Mail"
        self.description = (
            "Überblick über E-Mail-Adressen, die mit einer angegebenen Domain verknüpft sind.\n"
            "Zeigt, ob damit verknüpfte Passwörter öffentlich geleakt wurden."
        )
        self.columns = ["E-Mail", "Passwort geleakt (Ja/Nein)", "In öffentlicher Datenbank erfasst am",
                        "Im Digitalen Zwilling gescannt am"]
        self.table = "emails"

    def setup(self):
        create_standard_table(self.table)

    def get_endpoints_from_db(self, domain):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT value FROM endpoints WHERE domain = %s;", (domain,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        endpoints = []
        for r in rows:
            entry = r[0] if isinstance(r[0], dict) else json.loads(r[0])
            if endpoint_url in entry and endpoint_snapshot in entry:
                endpoints.append(entry)

        endpoints.sort(key=lambda x: x[endpoint_snapshot], reverse=True)

        return endpoints

    def clean_email(self, email):
        return email.replace("%20", "").strip().lower()

    def deduplicate_emails(self, email_entries: list[dict], columns: list[str], clean_email_func) -> list[dict]:
        email_key = columns[0]
        date_key = columns[2]
        latest_entries = {}

        for entry in email_entries:
            raw_email = entry[email_key]
            cleaned_email = clean_email_func(raw_email) if clean_email_func else raw_email
            date_str = entry.get(date_key, "") or ""

            try:
                if len(date_str) >= 8:
                    new_date = datetime.strptime(date_str[:8], "%Y%m%d")
                else:
                    raise ValueError("Zu kurzes Datum")
            except Exception:
                new_date = datetime.min

            if cleaned_email not in latest_entries:
                latest_entries[cleaned_email] = entry
            else:
                existing_date_str = latest_entries[cleaned_email].get(date_key, "") or ""
                try:
                    if len(existing_date_str) >= 8:
                        existing_date = datetime.strptime(existing_date_str[:8], "%Y%m%d")
                    else:
                        raise ValueError("Zu kurzes Datum (bestehender Eintrag)")
                except Exception:
                    existing_date = datetime.min

                if new_date > existing_date:
                    latest_entries[cleaned_email] = entry

        return sorted(latest_entries.values(), key=lambda x: clean_email_func(x[email_key]))

    def scan(self, domain: str) -> list[dict]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {self.table} WHERE domain = %s;", (domain,))
        conn.commit()
        cur.close()
        conn.close()
        limit = 50
        urls = self.get_endpoints_from_db(domain)[:limit]
        logger.info(f"🔍 Anzahl gefundene URLs: {len(urls)}")
        all_emails = []
        for i, entry in enumerate(urls):
            url = entry[endpoint_url]
            snapshot_date = entry[endpoint_snapshot]
            timestamp = snapshot_date.replace("-", "") + "000000"
            logger.info(f"🌐 [{i + 1}/{len(urls)}] Scanne archivierte Seite: {timestamp}/{url}")
            emails = extract_emails_from_url(timestamp, url, self.columns)
            all_emails.extend(emails)
            time.sleep(SLEEP)

        all_emails.extend(get_whois_emails(domain, self.columns))
        all_emails.extend(get_crtsh_emails(domain, self.columns))

        results = self.deduplicate_emails(all_emails, self.columns, self.clean_email)

        # Leere oder Platzhalter-Einträge rausfiltern
        results = [
            entry for entry in results
            if entry.get(self.columns[0]) and "Keine Daten gefunden" not in entry.get(self.columns[0])
        ]

        # Leak-Status prüfen (nur bei gültigen Adressen)
        for entry in results:
            email = entry.get(self.columns[0])
            entry[self.columns[1]] = is_leaked(email)

        # Fallback, wenn wirklich nichts da ist
        if not results:
            results = [generate_empty_email_entry(self.columns)]

        # In DB schreiben
        for entry in results:
            insert_record(self.table, domain, entry)

        return results

    def get(self, domain: str) -> list:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT value FROM {self.table} WHERE domain = %s;", (domain,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return [{"info": NO_DATA_SCANNED_TEXT}]
        return [r[0] if isinstance(r[0], dict) else json.loads(r[0]) for r in rows]
