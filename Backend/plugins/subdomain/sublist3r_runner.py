import subprocess
import os
from config import NO_DATA_FOUND_TEXT
from datetime import date

def get_subdomains(domain, columns):
    base_dir = os.path.dirname(__file__)
    output_path = os.path.join(base_dir, "subdomains.txt")
    sublist3r_path = os.path.join(base_dir, "sublist3r", "sublist3r.py")

    command = f"python3 {sublist3r_path} -d {domain} -o {output_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    print("📦 Sublist3r STDOUT:", result.stdout)
    print("⚠️ Sublist3r STDERR:", result.stderr)

    if not os.path.exists(output_path):
        return [{
            columns[0]: NO_DATA_FOUND_TEXT,
            columns[1]: date.today().isoformat()
        }]

    with open(output_path, "r") as f:
        subdomains = f.read().splitlines()
        subdomains_cleand = []
        for subdomain in subdomains:
            if subdomain.startswith("www."):
                subdomain = subdomain[4:]
            timestamp_scanned = date.today().isoformat()
            subdomain_info = {
                columns[0]: subdomain,
                columns[1]: timestamp_scanned
            }
            subdomains_cleand.append(subdomain_info)

    os.remove(output_path)


    if not subdomains_cleand:
        return [{
            columns[0]: NO_DATA_FOUND_TEXT,
            columns[1]: date.today().isoformat()
        }]

    return subdomains_cleand
