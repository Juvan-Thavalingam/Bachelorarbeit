from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """
    Abstrakte Basisklasse für alle Plugins.
    Jeder Plugin muss diese Methoden implementieren.
    """

    name: str
    description: str
    columns: list[str]

    @abstractmethod
    def setup(self):
        """Initialisiert ggf. Datenbankstruktur"""
        pass

    @abstractmethod
    def scan(self, domain: str) -> list[dict]:
        """Führt Scan durch und gibt Ergebnisse zurück"""
        pass

    @abstractmethod
    def get(self, domain: str) -> list[str]:
        """Liefert gespeicherte Daten aus der Datenbank"""
        pass

    def describe(self) -> dict:
        """
        Gibt Metadaten des Plugins zurück: Name, Beschreibung, Spalten
        """
        return {
            "name": self.name,
            "Beschreibung": self.description,
            "columns": self.columns
        }
