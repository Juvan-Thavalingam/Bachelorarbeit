import requests
import time
import random
from datetime import date
from config import NO_DATA_FOUND_TEXT

CRT_SH_API = "https://crt.sh/?q=%25.{domain}&output=json"


def generate_empty_certificate_entry(columns):
    """
    Gibt eine Platzhalter-Zertifikatszeile zurück mit NO_DATA_FOUND_TEXT.
    """
    return {
        columns[0]: NO_DATA_FOUND_TEXT,
        columns[1]: NO_DATA_FOUND_TEXT,
        columns[2]: NO_DATA_FOUND_TEXT,
        columns[3]: NO_DATA_FOUND_TEXT,
        columns[4]: NO_DATA_FOUND_TEXT,
        columns[5]: NO_DATA_FOUND_TEXT,
        columns[6]: date.today().isoformat()
    }


def get_certificates(domain, columns):
    """
    Ruft Zertifikate von crt.sh ab und bereitet sie strukturiert auf.

    Args:
        domain (str): Die zu prüfende Domain.
        columns (list[str]): Spaltennamen für die Ergebnisstruktur.

    Returns:
        list[dict]: Strukturierte Zertifikatsdaten oder Platzhalter.
    """
    url = CRT_SH_API.format(domain=domain)
    headers = {"User-Agent": "Mozilla/5.0"}
    time.sleep(random.randint(2, 4))

    try:
        res = requests.get(url, headers=headers, timeout=60)
        if res.status_code != 200:
            print(f"⚠️ crt.sh Fehler: {res.status_code}")
            return [generate_empty_certificate_entry(columns)]

        data = res.json()
        certs = []

        for entry in data:
            names = ""
            name_values = entry.get("name_value", "").splitlines()
            issuer_name = entry.get("issuer_name", NO_DATA_FOUND_TEXT)
            timestamp_entry = entry.get("entry_timestamp", NO_DATA_FOUND_TEXT).split("T")[0]
            timestamp_not_before = entry.get("not_before", NO_DATA_FOUND_TEXT).split("T")[0]
            timestamp_not_after = entry.get("not_after", NO_DATA_FOUND_TEXT).split("T")[0]
            is_wc = "Nein"
            first = True
            for domain_name in name_values:
                if not first:
                    names = names + ", "
                names = names + domain_name
                first = False
                if domain_name.startswith("*."):
                    is_wc = "Ja"

            timestamp_scanned = date.today().isoformat()
            cert_info = {
                columns[0]: names,
                columns[1]: issuer_name,
                columns[2]: timestamp_entry,
                columns[3]: timestamp_not_before,
                columns[4]: timestamp_not_after,
                columns[5]: is_wc,
                columns[6]: timestamp_scanned,
            }

            certs.append(cert_info)

        return certs if certs else [generate_empty_certificate_entry(columns)]

    except requests.exceptions.Timeout:
        print("⏱️ Timeout bei crt.sh – Server antwortet nicht schnell genug.")
        return [generate_empty_certificate_entry(columns)]
