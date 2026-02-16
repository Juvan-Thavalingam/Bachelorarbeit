from plugins.base_plugin import BasePlugin
from database import create_standard_table, insert_record, get_db_connection
from config import NO_DATA_SCANNED_TEXT
from plugins.service.shodan_lookup import search_services

import logging
import json

logger = logging.getLogger(__name__)

class Plugin(BasePlugin):
    def __init__(self):
        self.name = "Dienst"
        self.description = (
            "Überblick über offene Ports und identifizierte Dienste einer angegebenen Domain.\n"
            "Zeigt IP-Adresse, Port, Dienst, Version, Protokoll sowie erkannte Schwachstellen "
        )
        self.columns = ["IPv4-Adresse", "Port", "Dienst", "Version", "Protokoll", "Common Platform Enumeration (CPE)",
                        "Common Vulnerabilities and Exposures (CVE)", "Domain/Subdomain",
                        "Im Digitalen Zwilling gescannt am"]
        self.table = "shodan_services"

    def setup(self):
        create_standard_table(self.table)

    def scan(self, domain: str) -> list[dict]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {self.table} WHERE domain = %s;", (domain,))
        conn.commit()
        cur.close()
        conn.close()
        services = search_services(domain, self.columns)

        for service in services:
            insert_record(self.table, domain, service)

        logger.info(f"📦 Insgesamt {len(services)} Dienst-Einträge gespeichert")
        return services

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
