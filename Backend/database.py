import time
import psycopg2
import os
import json

def get_db_connection(retries=5, delay=2):
    """
    Stellt eine Verbindung zur PostgreSQL-Datenbank her mit Retry-Mechanismus.

    Args:
        retries (int): Max. Anzahl der Verbindungsversuche.
        delay (int): Wartezeit zwischen Versuchen (Sekunden).

    Returns:
        connection: PostgreSQL-Verbindung.
    """
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT", 5432),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            return conn
        except psycopg2.OperationalError as e:
            time.sleep(delay)

    raise Exception("🚨 Konnte keine Verbindung zur Datenbank herstellen.")

def create_standard_table(table: str):
    """
    Erstellt eine Standardtabelle mit Spalten `domain` und `value` (JSONB).

    Args:
        table (str): Name der Tabelle.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            domain TEXT,
            value JSONB
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_record(table: str, domain: str, value):
    """
    Fügt einen Eintrag in eine beliebige Tabelle ein.

    Args:
        table (str): Tabellenname (z.B. "a_record").
        domain (str): Die zugehörige Domain.
        value (str oder dict): Der zu speichernde Wert.
    """
    if isinstance(value, dict):
        value = json.dumps(value)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f"INSERT INTO {table} (domain, value) VALUES (%s, %s);", (domain, value))
    conn.commit()
    cur.close()
    conn.close()
