import subprocess
from config import NO_DATA_FOUND_TEXT

DEFAULT_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "PTR"]

def run_dig(query):
    try:
        result = subprocess.run(query, capture_output=True, text=True)
        return sorted(set(result.stdout.strip().split("\n"))) if result.stdout.strip() else []
    except Exception as e:
        print(f"❌ Fehler bei {query}: {e}")
        return []

def get_dns_records(domain, record_types=None):
    if record_types is None:
        record_types = DEFAULT_TYPES

    dns_records = {}

    # Normale DNS-Records
    for record in record_types:
        if record == "PTR":
            continue
        result = run_dig(["dig", domain, record, "+short"])
        dns_records[record] = result if result else [NO_DATA_FOUND_TEXT]

    # Sonderbehandlung für PTR
    if "PTR" in record_types:
        ip_addresses = []
        for ip in dns_records.get("A", []):
            if ip != NO_DATA_FOUND_TEXT:
                ip_addresses.append(ip)
        for ip in dns_records.get("AAAA", []):
            if ip != NO_DATA_FOUND_TEXT:
                ip_addresses.append(ip)

        if ip_addresses:
            ptr_records = {
                ip: run_dig(["dig", "-x", ip, "+short"]) or [NO_DATA_FOUND_TEXT]
                for ip in ip_addresses
            }
        else:
            ptr_records = {NO_DATA_FOUND_TEXT: [NO_DATA_FOUND_TEXT]}

        dns_records["PTR"] = ptr_records

    return dns_records

