from scan_domains import scan_domains
#from generate_diagram import generate_attribute_bar_chart
from export_results import export_results
from pathlib import Path

def load_domains():
    with open(Path(__file__).parent / "domains_100_last.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
'''
ATTRIBUTES = [
    "A", "AAAA", "MX", "NS", "TXT", "SOA", "PTR",
    "subdomain", "certificate", "service",
]

'''
ATTRIBUTES = [
    "A", "AAAA", "MX", "NS", "TXT", "SOA", "PTR",
    "subdomain", "certificate", "endpoint", "email", "phone", "service"
]


BASE_URL = "http://localhost:8000"


def main():
    domains = load_domains()
    print("🚀 Starte Einzel-Scans und Exporte ...")

    for domain in domains:
        scan_domains(domain, ATTRIBUTES, BASE_URL)
        export_results(domain, ATTRIBUTES, BASE_URL)

    print("✅ Alle Domains verarbeitet.")


    #generate_attribute_bar_chart()

    #print("📊 Diagramm erstellt...")

if __name__ == "__main__":
    main()
