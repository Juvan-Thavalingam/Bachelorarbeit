import requests
import json
from pathlib import Path


EXPORT_DIR = Path(__file__).parent / "exports"
EXPORT_DIR.mkdir(exist_ok=True)


def export_results(domain, attributes, base_url):
    print(f"\n📦 Exportiere Ergebnisse für {domain}")
    domain_results = {}

    for attribute in attributes:
        try:
            res = requests.get(f"{base_url}/get", params={"attribute": attribute, "domain": domain})
            res.raise_for_status()
            domain_results[attribute] = res.json()
        except Exception as e:
            domain_results[attribute] = {"error": str(e)}

    output_dir = Path("exports")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{domain.replace('.', '_')}_scan.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(domain_results, f, indent=2, ensure_ascii=False)
    print(f"✅ Gespeichert: {output_path}")

if __name__ == "__main__":
    with open(Path(__file__).parent / "domains.txt", "r", encoding="utf-8") as f:
        domain_list = [line.strip() for line in f if line.strip()]
    export_results(domain_list)
