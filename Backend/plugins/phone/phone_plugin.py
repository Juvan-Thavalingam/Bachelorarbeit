from plugins.base_plugin import BasePlugin
from plugins.phone.utils import generate_fallback_phone_entry
from plugins.email.dehashed_lookup import is_leaked
from database import create_standard_table, insert_record, get_db_connection
from config import NO_DATA_SCANNED_TEXT
from plugins.phone.waybackmachine_lookup import extract_phone_numbers_from_url
from plugins.phone.whois_lookup import get_whois_phone_numbers
from plugins.endpoint.endpoint_plugin import Plugin as EndpointPlugin
import logging
import json
import time
import random
from datetime import datetime

logger = logging.getLogger(__name__)
SLEEP = random.randint(7, 15)
endpoint_columns = EndpointPlugin().columns
endpoint_url = endpoint_columns[0]
endpoint_snapshot = endpoint_columns[1]

class Plugin(BasePlugin):
    def __init__(self):
        self.name = "Telefonnummer"
        self.description = (
            "Überblick über Telefonnummern, die mit einer angegebenen Domain in Verbindung stehen.\n"
            "Zeigt, ob damit verknüpfte Passwörter öffentlich geleakt wurden."
        )
        self.columns = ["Telefonnummern", "Passwort geleakt (Ja/Nein)", "In öffentlicher Datenbank erfasst am",
                        "Im Digitalen Zwilling gescannt am"]
        self.table = "phones"

    def setup(self):
        create_standard_table(self.table)

    def deduplicate_phone_numbers(self, phone_entries: list[dict], columns: list[str]) -> list[dict]:
        phone_key = columns[0]
        date_key = columns[2]
        latest_entries = {}

        for entry in phone_entries:
            phone = entry[phone_key]
            date_str = entry.get(date_key, "") or ""

            try:
                if len(date_str) >= 8:
                    new_date = datetime.strptime(date_str[:8], "%Y%m%d")
                else:
                    raise ValueError("Zu kurzes Datum")
            except Exception:
                new_date = datetime.min

            if phone not in latest_entries:
                latest_entries[phone] = entry
            else:
                existing_date_str = latest_entries[phone].get(date_key, "") or ""
                try:
                    if len(existing_date_str) >= 8:
                        existing_date = datetime.strptime(existing_date_str[:8], "%Y%m%d")
                    else:
                        raise ValueError("Zu kurzes Datum (bestehender Eintrag)")
                except Exception:
                    existing_date = datetime.min

                if new_date > existing_date:
                    latest_entries[phone] = entry

        return sorted(latest_entries.values(), key=lambda x: x[phone_key])

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

    def scan(self, domain: str) -> list[dict]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {self.table} WHERE domain = %s;", (domain,))
        conn.commit()
        cur.close()
        conn.close()
        limit = 50
        urls = self.get_endpoints_from_db(domain)[:limit]
        all_numbers = []

        for i, entry in enumerate(urls):
            url = entry[endpoint_url]
            snapshot = entry[endpoint_snapshot].replace("-", "") + "000000"
            archive_url = f"http://web.archive.org/web/{snapshot}/{url}"

            logger.info(f"🌐 [{i+1}/{len(urls)}] Scanne archivierte Seite: {archive_url}")
            phones = extract_phone_numbers_from_url(snapshot, url, self.columns)
            all_numbers.extend(phones)
            time.sleep(SLEEP)

        all_numbers.extend(get_whois_phone_numbers(domain, self.columns))

        results = self.deduplicate_phone_numbers(list(all_numbers), self.columns)

        # Deduplizieren
        results = self.deduplicate_phone_numbers(list(all_numbers), self.columns)

        # Nur "echte" Nummern behalten (nicht leer, kein Platzhaltertext)
        results = [
            entry for entry in results
            if entry.get(self.columns[0]) and "Keine Daten gefunden" not in entry.get(self.columns[0])
        ]

        for entry in results:
            phone = entry.get(self.columns[0])
            entry[self.columns[1]] = is_leaked(phone)

        # Fallback, wenn wirklich nichts da ist
        if not results:
            results = [generate_fallback_phone_entry(self.columns)]

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
