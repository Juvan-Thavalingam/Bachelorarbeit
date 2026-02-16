import shodan
import logging
from config import NO_DATA_FOUND_TEXT
from datetime import date

logger = logging.getLogger(__name__)

def load_api_key(filepath="keys/shodan_key.txt") -> str:
    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error("❌ API-Key-Datei nicht gefunden.")
        raise

def search_services(domain, columns):
    api_key = load_api_key()
    api = shodan.Shodan(api_key)

    try:
        logger.info(f"🔍 Suche Dienste in Shodan für: {domain}")
        query = f'hostname:"{domain}"'
        results = api.search(query)

        services = []

        if not results.get("matches"):
            logger.info("ℹ️ Keine Ergebnisse bei Shodan gefunden.")

        else:
            for item in results["matches"]:
                ip = item.get("ip_str")
                host_info = {}
                try:
                    host_info = api.host(ip)
                except shodan.APIError as e:
                    logger.warning(f"⚠️ Details für IP {ip} konnten nicht geladen werden: {e}")

                cve_data = item.get("vulns", {})
                cves = [f"CVE-{cve}" for cve in cve_data.keys()] if cve_data else NO_DATA_FOUND_TEXT

                service = {
                    columns[0]: ip,
                    columns[1]: item.get("port", NO_DATA_FOUND_TEXT),
                    columns[2]: item.get("product", NO_DATA_FOUND_TEXT),
                    columns[3]: item.get("version", NO_DATA_FOUND_TEXT),
                    columns[4]: item.get("transport", NO_DATA_FOUND_TEXT),
                    columns[5]: ", ".join(item.get("cpe", [])) if item.get("cpe") else NO_DATA_FOUND_TEXT,
                    columns[6]: cves,
                    columns[7]: ", ".join(host_info.get("hostnames", [])) if host_info.get("hostnames") else NO_DATA_FOUND_TEXT,
                    columns[8]: date.today().isoformat(),
                }
                services.append(service)

        # ✅ Fallback-Datensatz, wenn Liste leer
        if not services:
            fallback = {
                col: NO_DATA_FOUND_TEXT for col in columns[:-1]
            }
            fallback[columns[-1]] = date.today().isoformat()
            services.append(fallback)

        logger.info(f"✅ {len(services)} Dienste gefunden (inkl. Fallback falls nötig)")
        return services

    except shodan.APIError as e:
        logger.error(f"❌ Shodan API-Fehler: {e}")
        return [{
            col: NO_DATA_FOUND_TEXT for col in columns[:-1]
        } | {columns[-1]: date.today().isoformat()}]
    except Exception as e:
        logger.error(f"❌ Allgemeiner Fehler bei Shodan-Suche: {e}")
        return [{
            col: NO_DATA_FOUND_TEXT for col in columns[:-1]
        } | {columns[-1]: date.today().isoformat()}]
