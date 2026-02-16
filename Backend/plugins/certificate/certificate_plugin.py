from plugins.base_plugin import BasePlugin
from database import create_standard_table, insert_record, get_db_connection
from plugins.certificate.crtsh_lookup import get_certificates
from config import NO_DATA_SCANNED_TEXT
import json

class Plugin(BasePlugin):
    def __init__(self):
        self.name = "Zertifikat"
        self.description = (
            "Analysiert die SSL-Zertifikate von Subdomains einer angegebenen Domain.\n"
            "Zeigt, ob ein gültiges Zertifikat vorhanden ist, wer es ausgestellt hat, "
            "wann es in einer öffentlichen Datenbank erfasst wurde, und wie lange es gültig ist.\n"
            "Erkennt auch Wildcard-Zertifikate."
        )
        self.columns = ["Domain/Subdomain", "Ausgestellt von", "In öffentlicher Datenbank erfasst am",
                        "Gültig ab", "Gültig bis", "Wildcard-Zertifikat? (Ja/Nein)",
                        "Im Digitalen Zwilling gescannt am"]
        self.table = "certificate_record"

    def setup(self):
        create_standard_table(self.table)

    def scan(self, domain: str) -> list[dict]:
        """
        Führt die Zertifikatssuche via crt.sh durch, speichert Ergebnisse in der DB
        und gibt sie zurück.

        Args:
            domain (str): Die zu scannende Domain.

        Returns:
            list[dict]: Liste von Zertifikatsinformationen oder eine Fehlernachricht.
        """
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {self.table} WHERE domain = %s;", (domain,))
        conn.commit()
        cur.close()
        conn.close()
        certs = get_certificates(domain, self.columns)
        for cert in certs:
            if "error" in cert:
                return [cert]
            insert_record("certificate_record", domain, cert)
        return certs

    def get(self, domain: str) -> list:
        """
        Holt gespeicherte Zertifikatsdaten aus der Datenbank.

        Args:
            domain (str): Die Domain, zu der Daten abgerufen werden.

        Returns:
            list[dict]: Zertifikatsdaten oder ein Info-Text, falls nichts vorhanden.
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

