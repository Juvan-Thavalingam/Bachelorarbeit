from database import get_db_connection, create_standard_table, insert_record
from plugins.dns.dig_lookup import get_dns_records
from config import NO_DATA_SCANNED_TEXT, NO_DATA_FOUND_TEXT
from plugins.base_plugin import BasePlugin
from datetime import date
import json

RECORD_DESCRIPTIONS = {
    "A": "Zeigt, unter welcher IPv4-Adresse die Domain direkt erreichbar ist.",
    "AAAA": "Zeigt, unter welcher IPv6-Adresse die Domain direkt erreichbar ist.",
    "MX": (
        "Listet die Mailserver (Mail Exchange) auf, die für den E-Mail-Empfang zuständig sind. "
        "Server mit einer niedrigeren Zahl (Priorität) werden bevorzugt genutzt."
    ),
    "NS": "Gi.bt an, welche Nameserver offiziell für die Verwaltung der Domain verantwortlich sind.",
    "TXT": (
        "Beinhaltet frei definierbare Texte, z.B. für Sicherheits- und Verifizierungszwecke. "
        "Häufig verwendet für SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail) "
        "oder die Google-Site-Verifizierung."
    ),
    "SOA": (
        "Der SOA-Eintrag (Start of Authority) liefert zentrale Verwaltungsdaten für eine DNS-Zone. "
        "Er enthält den primären autoritativen Nameserver (Primary Nameserver), den technischen Ansprechpartner "
        "in Form einer E-Mail-Adresse (Hostmaster), sowie einen sogenannten Serial-Wert, der die aktuelle Version "
        "der Zonendaten angibt. Zusätzlich werden Zeitangaben definiert: "
        "Refresh (Abfrageintervall für sekundäre Server), Retry (Wiederholungsintervall bei Fehlern), "
        "Expire (Ablaufzeit nach fehlgeschlagenen Abfragen) und Minimum TTL (Gültigkeitsdauer negativer Antworten)."
    ),
    "PTR": (
        "Ermöglicht die Rückwärtsauflösung von IP-Adressen zu Hostnamen mittels Reverse-DNS-Abfragen. "
        "Wird häufig bei Logging- oder E-Mail-Systemen zur Authentifizierung eingesetzt."
    ),
}



RECORD_COLUMNS = {
    "A": ["IPv4-Adresse", "Im Digitalen Zwilling gescannt am"],
    "AAAA": ["IPv6-Adresse", "Im Digitalen Zwilling gescannt am"],
    "MX": ["Mailserver", "Priorität", "Im Digitalen Zwilling gescannt am"],
    "NS": ["Name Server", "Im Digitalen Zwilling gescannt am"],
    "TXT": ["Text Record", "Im Digitalen Zwilling gescannt am"],
    "SOA": ["Primärer Nameserver", "Technischer Ansprechpartner", "Zonenversion (Serial)", "Aktualisierungsintervall", "Wiederholungsintervall", "Ablaufzeit", "Minimale Time To Live (TTL)", "Im Digitalen Zwilling gescannt am"],
    "PTR": ["IP-Adresse", "PTR-Domain", "Im Digitalen Zwilling gescannt am"]
}

class Plugin(BasePlugin):
    def __init__(self, record_type: str):
        self.record_type = record_type.upper()
        self.name = self.record_type + "-Record"
        self.description = RECORD_DESCRIPTIONS.get(self.record_type, f"{self.record_type}-DNS-Record")
        self.columns = RECORD_COLUMNS.get(self.record_type, ["Wert", "Gescannt am"])

    def setup(self):
        table = f"{self.record_type.lower()}_record"
        create_standard_table(table)

    def scan(self, domain: str) -> list[dict]:
        table = f"{self.record_type.lower()}_record"
        scan_date = date.today().isoformat()
        results = []

        # Alte Einträge löschen
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE domain = %s;", (domain,))
        conn.commit()
        cur.close()
        conn.close()

        # Für PTR: A + AAAA + PTR auf einmal aufrufen
        if self.record_type == "PTR":
            dns_data = get_dns_records(domain, ["A", "AAAA", "PTR"])
            self._scan_ptr(dns_data, domain, scan_date, results, table)

        else:
            dns_data = get_dns_records(domain, [self.record_type])
            match self.record_type:
                case "SOA":
                    self._scan_soa(dns_data, domain, scan_date, results, table)
                case "MX":
                    self._scan_mx(dns_data, domain, scan_date, results, table)
                case _:
                    self._scan_simple(dns_data, domain, scan_date, results, table)

        return results

    def _scan_ptr(self, dns_data, domain, scan_date, results, table):
        ptr_data = dns_data.get("PTR", {})
        for ip, ptrs in ptr_data.items():
            for ptr in ptrs:
                if ptr in [NO_DATA_FOUND_TEXT, NO_DATA_SCANNED_TEXT]:
                    continue
                entry = {
                    "IP-Adresse": ip,
                    "PTR-Domain": ptr,
                    "Im Digitalen Zwilling gescannt am": scan_date
                }
                results.append(entry)
                insert_record(table, domain, entry)


        if not results:
            entry = {
                "IP-Adresse": NO_DATA_FOUND_TEXT,
                "PTR-Domain": NO_DATA_FOUND_TEXT,
                "Im Digitalen Zwilling gescannt am": scan_date
            }
            results.append(entry)
            insert_record(table, domain, entry)

    def _scan_soa(self, dns_data, domain, scan_date, results, table):
        for val in dns_data.get("SOA", []):
            parts = val.split()
            if len(parts) >= 7:
                entry = {
                    "Primary Nameserver": parts[0],
                    "Hostmaster": parts[1],
                    "Serial": parts[2],
                    "Refresh": parts[3],
                    "Retry": parts[4],
                    "Expire": parts[5],
                    "Minimum TTL": parts[6],
                    "Im Digitalen Zwilling gescannt am": scan_date
                }
                results.append(entry)
                insert_record(table, domain, entry)


        if not results:
            entry = {
                "Primary Nameserver": NO_DATA_FOUND_TEXT,
                "Hostmaster": NO_DATA_FOUND_TEXT,
                "Serial": NO_DATA_FOUND_TEXT,
                "Refresh": NO_DATA_FOUND_TEXT,
                "Retry": NO_DATA_FOUND_TEXT,
                "Expire": NO_DATA_FOUND_TEXT,
                "Minimum TTL": NO_DATA_FOUND_TEXT,
                "Im Digitalen Zwilling gescannt am": scan_date
            }
            results.append(entry)
            insert_record(table, domain, entry)

    def _scan_mx(self, dns_data, domain, scan_date, results, table):
        for val in dns_data.get("MX", []):
            try:
                preference, server = val.split()
            except ValueError:
                preference, server = NO_DATA_FOUND_TEXT, val
            entry = {
                "Mailserver (MX)": server,
                "Präferenz": preference,
                "Im Digitalen Zwilling gescannt am": scan_date
            }
            results.append(entry)
            insert_record(table, domain, entry)

    def _scan_simple(self, dns_data, domain, scan_date, results, table):
        for val in dns_data.get(self.record_type, []):
            if self.record_type in ["A", "AAAA"]:
                entry = {
                    self.columns[0]: val,
                    self.columns[1]: scan_date
                }
            else:
                entry = {
                    self.columns[0]: val,
                    self.columns[1]: scan_date
                }
            results.append(entry)
            insert_record(table, domain, entry)

    def get(self, domain: str) -> list:
        table = f"{self.record_type.lower()}_record"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT value FROM {table} WHERE domain = %s;", (domain,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return [{"info": NO_DATA_SCANNED_TEXT}]
        return [r[0] if isinstance(r[0], dict) else json.loads(r[0]) for r in rows]
