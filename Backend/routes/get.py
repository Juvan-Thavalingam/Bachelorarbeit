from fastapi import APIRouter, Query
from plugins.plugin_manager import get_plugin

router = APIRouter()

@router.get("/get")
def fetch_data(attribute: str = Query(...), domain: str = Query(...)):
    """
    Liefert bereits gescannte Daten eines Plugins (Attributs) für eine bestimmte Domain.

    Diese Route ruft die gespeicherten Werte eines bestimmten Attribut-Plugins ab,
    z.B. Zertifikate, DNS-Records oder Subdomains. Die Daten stammen aus der Datenbank,
    nicht von einem Live-Scan.

    Args:
        attribute (str): Name des Attributs/Plugins (z.B. "A", "PTR", "certificate").
        domain (str): Die zugehörige Domain.

    Returns:
        list | dict: Gespeicherte Daten oder Fehlernachricht.
    """
    plugin = get_plugin(attribute)
    if not plugin:
        return {"error": f"Kein Plugin für {attribute}"}

    return plugin.get(domain)
