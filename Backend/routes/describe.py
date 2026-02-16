from fastapi import APIRouter, Query
from plugins.plugin_manager import get_plugin

router = APIRouter()

@router.get("/describe")
def describe(attribute: str = Query(...)):
    """
    Liefert Metadaten zum gegebenen Attribut/Plugin, z.B. Beschreibung & Felder.

    Args:
        attribute (str): Name des Attributs (z.B. "A", "subdomain")

    Returns:
        dict: Plugin-Info oder Fehlermeldung.
    """
    plugin = get_plugin(attribute)
    if not plugin:
        return {"error": f"Kein Plugin für {attribute}"}

    return plugin.describe()