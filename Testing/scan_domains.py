import requests
import time

def scan_attribute(domain, attribute, BASE_URL):
    print(f"🔍 Scanne {attribute} für {domain}")
    try:
        res = requests.get(f"{BASE_URL}/scan", params={"attribute": attribute, "domain": domain})
        return res.status_code == 200
    except Exception as e:
        print(f"❌ Fehler bei {attribute}: {e}")
        return False

def scan_domains(domain, attributes, base_url):
    print(f"\n🌐 ----- Starte Scan für Domain: {domain} -----")
    for attribute in attributes:
        try:
            print(f"🔍 Scanne {attribute} für {domain} ...")
            res = requests.get(f"{base_url}/scan", params={"attribute": attribute, "domain": domain})
            res.raise_for_status()
            time.sleep(1)
        except Exception as e:
            print(f"❌ Fehler bei Scan {attribute} für {domain}: {e}")

if __name__ == "__main__":
    from pathlib import Path
    with open(Path(__file__).parent / "domains.txt", "r", encoding="utf-8") as f:
        domain_list = [line.strip() for line in f if line.strip()]
    scan_domains(domain_list)
