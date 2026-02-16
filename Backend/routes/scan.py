from fastapi import APIRouter, Query
from plugins.plugin_manager import get_plugin

router = APIRouter()

@router.get("/scan")
def scan(attribute: str = Query(...), domain: str = Query(...)):
    """
    Führt einen Scan für das gegebene Attribut (Plugin) durch.

    Args:
        attribute (str): Das Attribut (z.B. "A", "subdomain").
        domain (str): Domain, die gescannt werden soll.

    Returns:
        dict: Statusmeldung oder Fehler.
    """
    plugin = get_plugin(attribute)
    if not plugin:
        return {"error": f"Kein Plugin für {attribute}"}

    try:
        result = plugin.scan(domain)
        if isinstance(result, list) and result and isinstance(result[0], dict) and "error" in result[0]:
            return {"error": result[0]["error"]}

        return {"status": f"Scan für {attribute} abgeschlossen"}
    except Exception as e:
        return {"error": str(e)}
