import requests
import time
import random
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import date
from config import NO_DATA_FOUND_TEXT

SLEEP = random.randint(2, 4)
URL_REGEX = re.compile(r"(?:Disallow|Allow):\s*([^\s#]+)")
EXCLUDE_SUFFIXES = ('.js', '.css', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico')

def fetch_snapshots(domain, path="/*", limit=None):
    url = f"https://web.archive.org/cdx/search/cdx?url={domain}{path}&output=json&fl=timestamp,original"
    r = requests.get(url)
    if r.status_code != 200:
        return []
    data = sorted(r.json()[1:], key=lambda x: x[0], reverse=True)
    return data[:limit] if limit else data

def extract_from_cdx(domain, snapshot_date_text,url_text, scanned_at_text):
    seen = {}
    for ts, full in fetch_snapshots(domain, limit=None):
        parsed = urlparse(full)
        p = parsed.path.rstrip("/")
        if not p or p.lower().endswith(EXCLUDE_SUFFIXES):
            continue
        key = p.lower()
        date_time = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
        if key not in seen or seen[key][snapshot_date_text] < date_time:
            seen[key] = {snapshot_date_text: date_time, url_text: full, scanned_at_text: date.today().isoformat()}
    return seen

def extract_from_robots(domain, snapshot_date_text, url_text, scanned_at_text,limit):
    entries = {}
    snapshots = fetch_snapshots(domain, "/robots.txt", limit=limit)
    for t, u in snapshots:
        snap_url = f"https://web.archive.org/web/{t}/{u}"
        ts = t[:8]
        try:
            r = requests.get(snap_url, timeout=5)
            if r.status_code != 200:
                continue
            date_time = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
            for path in URL_REGEX.findall(r.text):
                p = path.strip().rstrip("/")
                key = p.lower()
                if not p or key in entries:
                    continue
                if "*" in p or "?" in p or "$" in p:
                    continue
                full_url = f"https://{domain}{p}"
                entries[key] = {snapshot_date_text: date_time, url_text: full_url, scanned_at_text: date.today().isoformat()}
        except:
            continue
        time.sleep(SLEEP)
    return entries

def extract_from_sitemap(domain,  snapshot_date_text, url_text,scanned_at_text,limit):
    entries = {}
    snapshots = fetch_snapshots(domain, "/sitemap.xml", limit=limit)
    for t, u in snapshots:
        snap_url = f"https://web.archive.org/web/{t}/{u}"
        try:
            r = requests.get(snap_url, timeout=5)
            ts_match = re.search(r"/web/(\d{8})", snap_url)
            date_time = f"{ts_match[1][:4]}-{ts_match[1][4:6]}-{ts_match[1][6:8]}" if ts_match else "0000-00-00"
            root = ET.fromstring(r.text)
            for loc in root.findall(".//{*}url/{*}loc"):
                url = loc.text.strip()
                p = urlparse(url).path.rstrip("/")
                key = p.lower()
                if not p or key in entries:
                    continue
                entries[key] = {
                    snapshot_date_text: date_time,
                    url_text: url,
                    scanned_at_text: date.today().isoformat()
                }
        except:
            continue
        time.sleep(SLEEP)
    return entries

def combine_all(domain: str, columns, robot_limit=2, sitemap_limit=2):
    url_text = columns[0]
    snapshot_date_text = columns[1]
    scanned_at_text = columns[2]

    combined = extract_from_cdx(domain, snapshot_date_text, url_text, scanned_at_text)
    robots = extract_from_robots(domain, snapshot_date_text, url_text, scanned_at_text, limit=robot_limit)
    sitemap = extract_from_sitemap(domain, snapshot_date_text, url_text, scanned_at_text, limit=sitemap_limit)

    for source in (robots, sitemap):
        for k, v in source.items():
            if k not in combined or combined[k][snapshot_date_text] < v[snapshot_date_text]:
                combined[k] = v

    all_entries = list(combined.values())

    if not all_entries:
        return [{
            url_text: NO_DATA_FOUND_TEXT,
            snapshot_date_text: "0000-00-00",
            scanned_at_text: date.today().isoformat()
        }]

    main_url = f"https://{domain}"
    main_entry = next((e for e in all_entries if e.get(url_text, "").rstrip("/") == main_url), None)
    rest = [e for e in all_entries if e[url_text].rstrip("/") != main_url]

    rest_sorted = sorted(
        rest,
        key=lambda x: (-int(x[snapshot_date_text].replace("-", "")), x[url_text].lower())
    )

    return [main_entry] + rest_sorted if main_entry else rest_sorted
