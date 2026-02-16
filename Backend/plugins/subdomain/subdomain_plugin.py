from database import get_db_connection, create_standard_table, insert_record
from plugins.subdomain.sublist3r_runner import get_subdomains
from plugins.base_plugin import BasePlugin
from config import NO_DATA_SCANNED_TEXT
import json

class Plugin(BasePlugin):
    """
    Plugin für Subdomain-Enumeration mit Sublist3r.
    """
    def __init__(self):
        self.name = "Subdomain"
        self.description = "Überblick über Subdomains einer angegebenen Domain."
        self.columns = ["Subdomainname", "In Digitalem Twin gescant am"]
        self.table = "subdomain_record"

    def setup(self):
        """
        Erstellt die Tabelle `subdomain_record` mit Standardstruktur.
        """
        create_standard_table(self.table)

    def scan(self, domain: str) -> list[dict]:
        """
        Führt die Subdomain-Enumeration durch.

        Args:
            domain (str): Die zu scannende Domain

        Returns:
            list[dict]: Liste von Subdomains als einzelne Zeilen
        """
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {self.table} WHERE domain = %s;", (domain,))
        conn.commit()
        cur.close()
        conn.close()

        subdomains = get_subdomains(domain, self.columns)
        entries = subdomains

        for entry in entries:
            insert_record(self.table, domain, entry)

        return entries

    def get(self, domain: str) -> list[str]:
        """
        Ruft gespeicherte Subdomains aus der Datenbank ab.

        Args:
            domain (str): Die Ziel-Domain.

        Returns:
            list[dict]: Liste der Subdomains oder Info, wenn leer.
        """
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT value FROM {self.table} WHERE domain = %s;", (domain,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            return [{"info": NO_DATA_SCANNED_TEXT}]

        return [r[0] if isinstance(r[0], dict) else json.loads(r[0]) for r in rows]


