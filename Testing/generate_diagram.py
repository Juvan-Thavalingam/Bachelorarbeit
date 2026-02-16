import json
import os
import matplotlib.pyplot as plt

# ============== Konfiguration ==============
JSON_DIR   = "./exports/good"
OUTPUT_DIR = "./diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Puffer oberhalb der Balken (als Anteil an ymax)
TOP_MARGIN_PCT = 0.01

# Farbschema für die Leaked-Diagramme
LEAKED_COLORS = {"Nein": "green", "Ja": "red"}

# Schwellenwerte pro Attribut
attribute_custom_buckets = {
    "endpoint":    [0, 1, 10, 100, 1000, 10000],
    "AAAA":        [0, 1, 2, 3],
    "A":           [0, 1, 2, 5],
    "MX":          [0, 1, 2, 5],
    "NS":          [0, 1, 2, 5],
    "SOA":         [0, 1, 2],
    "TXT":         [0, 1, 2, 5, 10],
    "PTR":         [0, 1, 2, 5],
    "subdomain":   [0, 1, 2, 5, 50, 100],
    "service":     [0, 1, 2, 10, 50],
    "certificate": [0, 1, 2, 10, 100],
    "email":       [0, 1, 2, 5, 20],
    "phone":       [0, 1, 2, 5, 20],
}
default_thresholds = [0, 1, 5]

# Mapping für Anzeige-Namen
DISPLAY_NAMES = {
    "endpoint":    "Endpunkt",
    "AAAA":        "AAAA-Record",
    "A":           "A-Record",
    "MX":          "MX-Record",
    "NS":          "NS-Record",
    "SOA":         "SOA-Record",
    "TXT":         "TXT-Record",
    "PTR":         "PTR-Record",
    "subdomain":   "Subdomain",
    "service":     "Dienst",
    "certificate": "Zertifikat",
    "email":       "E-Mail",
    "phone":       "Telefonnummer",
}


def load_all_results(json_dir):
    """Lädt alle JSON-Dateien im Verzeichnis."""
    results = []
    for fname in os.listdir(json_dir):
        if fname.endswith(".json"):
            with open(os.path.join(json_dir, fname), "r", encoding="utf-8") as f:
                results.append(json.load(f))
    return results


def plot_bar(labels, values, title, ylabel, output_filename,
             colors=None, annotate_perc=None, xlabel=None,
             bar_width=0.8):
    fig_width = max(6, len(labels) * 1.0)
    fig, ax = plt.subplots(figsize=(fig_width, 4))

    bar_colors = [colors.get(lbl) for lbl in labels] if isinstance(colors, dict) else colors
    x = range(len(labels))
    ax.bar(x, values, width=bar_width, color=bar_colors)

    ax.margins(y=0.15)

    ax.set_xticks(x)
    if len(labels) > 2:
        ax.set_xticklabels(labels, rotation=45, ha="right")
    else:
        ax.set_xticklabels(labels, rotation=0, ha="center")

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)

    ymax = max(values or [0])
    for i, val in enumerate(values):
        txt = str(val)
        if annotate_perc and labels[i] in annotate_perc:
            txt += f" ({annotate_perc[labels[i]]}%)"
        ax.text(i, val + TOP_MARGIN_PCT * ymax, txt, ha="center", va="bottom")

    plt.tight_layout()
    bottom_margin = 0.30 if xlabel else 0.15
    plt.subplots_adjust(bottom=bottom_margin)

    out_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(out_path)
    plt.close(fig)
    print(f"✅ Diagramm gespeichert: {out_path}")


def analyse_leaked(datentyp, label):
    ja = nein = 0

    for res in all_results:
        entries = res.get(datentyp, [])
        if not entries:
            continue

        if datentyp == "service":
            # Prüfen, ob mindestens ein echter CVE-Eintrag vorhanden ist
            found_cve = any(
                e.get("Common Vulnerabilities and Exposures (CVE)") not in (None, "Keine Daten gefunden")
                for e in entries
            )
            if found_cve:
                ja += 1
            else:
                nein += 1
        else:
            # E-Mail/Phone: prüfen Passwort geleakt
            if any(e.get("Passwort geleakt (Ja/Nein)") == "Keine Abfrage möglich" for e in entries):
                continue
            if any(e.get("Passwort geleakt (Ja/Nein)") == "Ja" for e in entries):
                ja += 1
            else:
                nein += 1

    total = ja + nein
    pct = {"Ja": round(ja/total*100, 2), "Nein": round(nein/total*100, 2)} if total else {}
    display = DISPLAY_NAMES.get(datentyp, label)

    # Titel je nach Datentyp
    if datentyp == "service":
        title = f"{display} – CVE gefunden?"
    else:
        title = f"{display} – Passwort geleakt?"

    plot_bar(
        labels=["Nein", "Ja"],
        values=[nein, ja],
        title=title,
        ylabel="Anzahl Firmen",
        output_filename=f"{datentyp}_leaked.png",
        colors=LEAKED_COLORS,
        annotate_perc=pct
    )


def get_bucket_index(count, thresholds):
    N = len(thresholds) - 1
    if count == thresholds[0]:
        return 0
    for i in range(1, N):
        low, high = thresholds[i], thresholds[i+1]
        if low <= count < high:
            return i
    return N


def analyse_attribute_distribution():
    stats = {}
    for res in all_results:
        for attr, entries in res.items():
            if isinstance(entries, list) and len(entries) == 1:
                data_vals = [
                    v for k, v in entries[0].items()
                    if not (k.lower().endswith("gescannt am") or k.lower().endswith("erfasst am"))
                ]
                cnt = 0 if all(val == "Keine Daten gefunden" for val in data_vals) else 1
            else:
                cnt = len(entries) if isinstance(entries, list) else 1
            stats.setdefault(attr, []).append(cnt)

    for attr, counts in stats.items():
        thresholds = attribute_custom_buckets.get(attr, default_thresholds)
        buckets = [0] * len(thresholds)
        for c in counts:
            idx = get_bucket_index(c, thresholds)
            idx = min(idx, len(buckets)-1)
            buckets[idx] += 1

        labels = []
        for i in range(len(thresholds)):
            low = thresholds[i]
            if i == len(thresholds) - 1:
                labels.append(f"mehr als {low}")
            else:
                high = thresholds[i+1]
                span = high - low
                labels.append(f"{low}" if span <= 1 else f"{low} bis {high-1}")

        display = DISPLAY_NAMES.get(attr, attr.capitalize())
        plot_bar(
            labels=labels,
            values=buckets,
            title=f"{display} – Verteilung pro Firma",
            ylabel="Anzahl Firmen",
            output_filename=f"{attr}_verteilung.png",
            xlabel=f"Anzahl {display}-Einträge"
        )


# ========== Workflow starten ==========
all_results = load_all_results(JSON_DIR)

# Leaked- bzw. CVE-Diagramme
analyse_leaked("email", "E-Mail")
analyse_leaked("phone", "Telefonnummer")
analyse_leaked("service", "Dienst")

# Attribut-Verteilungen
analyse_attribute_distribution()
