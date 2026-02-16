from plugins.base_plugin import BasePlugin
from database import create_standard_table, insert_record, get_db_connection
from plugins.endpoint.waybackmachine_lookup import combine_all
from config import NO_DATA_SCANNED_TEXT
import json

class Plugin(BasePlugin):
    """
    Plugin zur Analyse historischer §s über die Wayback Machine (robots.txt, sitemap.xml, CDX API).

    Dieses Plugin:
    - extrahiert historische URLs von archivierten Snapshots
    - speichert sie in der Datenbank
    - stellt sie für Anzeige/Export zur Verfügung
    """

    def __init__(self):
        """
        Initialisiert das Endpoint-Plugin.
        """
        self.name = "Endpunkt"
        self.description = "Überblick über historische URLs einer angegebenen Domain."
        self.columns = ["URL", "In öffentlicher Datenbank erfasst am", "Im Digitalen Zwilling gescannt am"]
        self.table = "endpoints"

    def setup(self):
        """
        Erstellt die Tabelle `endpoints_record` (falls nicht vorhanden).
        """
        create_standard_table(self.table)

    def scan(self, domain: str) -> list[dict]:
        """
        Führt die Extraktion der historischen Endpunkte für die angegebene Domain durch.

        Args:
            domain (str): Die zu scannende Domain

        Returns:
            list[dict]: Gefundene Endpunkte (URL + Snapshot-Datum)
        """
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {self.table} WHERE domain = %s;", (domain,))
        conn.commit()
        cur.close()
        conn.close()
        try:
            endpoints = combine_all(domain, self.columns, robot_limit=5, sitemap_limit=5)
            for entry in endpoints:
                insert_record(self.table, domain, entry)
            return endpoints
        except Exception as e:
            return [{"error": f"Fehler beim Wayback-Scan: {e}"}]

    def get(self, domain: str) -> list:
        """
        Holt gespeicherte Endpunkte aus der Datenbank für eine Domain.

        Args:
            domain (str): Ziel-Domain

        Returns:
            list[dict]: Ergebnisse aus der Datenbank oder Info-Hinweis
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
