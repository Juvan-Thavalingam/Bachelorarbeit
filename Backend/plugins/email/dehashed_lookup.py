import requests
import os
import json
from config import NO_API_CREDITS_TEXT

DEHASHED_API_KEY_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../keys/dehashed_key.txt"))
DEHASHED_API_URL = "https://api.dehashed.com/v2/search"

def load_dehashed_key() -> str:
    if not os.path.exists(DEHASHED_API_KEY_FILE):
        raise FileNotFoundError(f"{DEHASHED_API_KEY_FILE} nicht gefunden.")

    with open(DEHASHED_API_KEY_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def is_leaked(attribute: str) -> str:
    """
    Prüft, ob für die angegebene E-Mail ein Passwort im Klartext auf DeHashed zu finden ist.
    Gibt True zurück, wenn mindestens ein Klartext-Passwort gefunden wurde.
    """

    
    
    try:
        api_key = load_dehashed_key()
        headers = {
            "Content-Type": "application/json",
            "Dehashed-Api-Key": api_key
        }
        print(api_key)

        body = {
            "query": attribute,
            "page": 1,
            "size": 1000
        }

        response = requests.post(
            DEHASHED_API_URL,
            headers=headers,
            json=body
        )

        if response.status_code == 200:
            data = response.json()
            entries = data.get("entries", [])
            for entry in entries:
                print(json.dumps(entry, indent=2))
                if "password" in entry:
                    passwords = entry.get("password", [])
                    print(f"Gefundene Klartextpasswörter: {passwords}")
                    if any(p.strip() for p in passwords):
                        return "Ja"
        print(response.status_code)
        return "Nein"

    except Exception as e:
        print(f"⚠️ Fehler bei DeHashed für {attribute}: {e}")
        return NO_API_CREDITS_TEXT

def main():
    leaked = is_leaked("first@gmail.com")
    print(leaked)

if __name__ == "__main__":
    main()
