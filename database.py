"""
Modulo database — creazione tabella e funzioni di accesso ai dati.
Versione v4 - Supporto per le icone meteo e la cancellazione singola delle ricerche.
"""

import sqlite3

DB = "meteo.db"

def get_conn():
    """Apre una connessione al database e restituisce l'oggetto conn."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def crea_tabella():
    """Crea la tabella 'ricerche' se non esiste già."""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ricerche (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citta TEXT NOT NULL,
            temperatura REAL,
            data TEXT,
            codice_meteo INTEGER
        )
    """)
    
    # Migrazione per i database esistenti: tenta di aggiungere la colonna se non presente
    try:
        conn.execute("ALTER TABLE ricerche ADD COLUMN codice_meteo INTEGER")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def salva_ricerca(citta, temperatura, data, codice_meteo=None):
    """Inserisce una nuova riga nella tabella ricerche includendo il codice meteo."""
    conn = get_conn()
    conn.execute(
        "INSERT INTO ricerche (citta, temperatura, data, codice_meteo) VALUES (?, ?, ?, ?)",
        (citta, temperatura, data, codice_meteo)
    )
    conn.commit()
    conn.close()

def leggi_ricerche(limite=20):
    """Restituisce le ultime ricerche come lista di dizionari."""
    conn = get_conn()
    righe = conn.execute(
        "SELECT * FROM ricerche ORDER BY id DESC LIMIT ?",
        (limite,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in righe]

def cancella_ricerche():
    """Svuota completamente la tabella ricerche."""
    conn = get_conn()
    conn.execute("DELETE FROM ricerche")
    conn.commit()
    conn.close()

def cancella_ricerca_singola(id_ricerca):
    """Cancella una singola ricerca dal database in base al suo ID."""
    conn = get_conn()
    conn.execute("DELETE FROM ricerche WHERE id = ?", (id_ricerca,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    crea_tabella()
    print("Database configurato per la cancellazione singola.")