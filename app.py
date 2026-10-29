"""
Storico Meteo — web application Flask.
Versione v4 - Integrazione delle icone meteo ed eliminazione singola delle ricerche.
"""

from flask import Flask, render_template, request, redirect
from datetime import datetime
import requests
import database

app = Flask(__name__)

# ============================================================
# DATI — già pronti
# ============================================================
CITTA = {
    "Firenze":  (43.7696, 11.2558),
    "Roma":     (41.9028, 12.4964),
    "Milano":   (45.4654,  9.1859),
    "Napoli":   (40.8518, 14.2681),
    "Torino":   (45.0703,  7.6869),
    "Bologna":  (44.4949, 11.3426),
    "Venezia":  (45.4408, 12.3155),
    "Palermo":  (38.1157, 13.3615),
}

CODICI_METEO = {
    0: "Sereno", 1: "Prevalentemente sereno", 2: "Parzialmente nuvoloso",
    3: "Coperto", 45: "Nebbia", 51: "Pioggerella leggera",
    53: "Pioggerella moderata", 61: "Pioggia leggera", 63: "Pioggia moderata",
    65: "Pioggia intensa", 71: "Neve leggera", 75: "Neve intensa",
    80: "Rovesci leggeri", 95: "Temporale",
}

ICONE_METEO = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    51: "🌧️",
    53: "🌧️",
    61: "🌧️",
    63: "🌧️",
    65: "🌧️",
    71: "❄️",
    75: "❄️",
    80: "🌦️",
    95: "⛈️"
}

def arricchisci_ricerche(ricerche):
    """Arricchisce la lista di ricerche associando a ciascuna la corretta icona emoji."""
    for r in ricerche:
        code = r.get("codice_meteo")
        r["icona"] = ICONE_METEO.get(code, "🌡️") if code is not None else "🌡️"
    return ricerche

# ============================================================
# ROUTE
# ============================================================

@app.route("/")
def home():
    """Pagina principale: form di ricerca + storico."""
    ricerche = arricchisci_ricerche(database.leggi_ricerche())
    return render_template("index.html",
                           lista_citta=CITTA.keys(),
                           ricerche=ricerche,
                           risultato=None,
                           errore=None)

@app.route("/cerca", methods=["POST"])
def cerca():
    """Riceve la città dal form, chiama l'API meteo, salva e mostra il risultato."""
    citta = request.form["citta"]
    lat, lon = CITTA[citta]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,windspeed_10m,weather_code"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        cw = response.json()["current"]
        weather_code = cw["weather_code"]

        risultato = {
            "citta": citta,
            "temperatura": cw["temperature_2m"],
            "vento": cw["windspeed_10m"],
            "descrizione": CODICI_METEO.get(weather_code, f"Codice {weather_code}"),
            "icona": ICONE_METEO.get(weather_code, "🌡️")
        }

        database.salva_ricerca(
            citta,
            risultato["temperatura"],
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            codice_meteo=weather_code
        )
        errore = None

    except requests.exceptions.RequestException:
        risultato = None
        errore = "Servizio meteo non raggiungibile. Controlla la connessione."

    ricerche = arricchisci_ricerche(database.leggi_ricerche())
    return render_template("index.html",
                           lista_citta=CITTA.keys(),
                           ricerche=ricerche,
                           risultato=risultato,
                           errore=errore)

@app.route("/cancella", methods=["POST"])
def cancella():
    """Svuota la tabella delle ricerche dal database e reindirizza alla home."""
    database.cancella_ricerche()
    return redirect("/")

@app.route("/cancella/<int:id_ricerca>", methods=["POST"])
def cancella_singola(id_ricerca):
    """Cancella una singola ricerca in base all'ID e reindirizza alla home."""
    database.cancella_ricerca_singola(id_ricerca)
    return redirect("/")

if __name__ == "__main__":
    database.crea_tabella()
    app.run(debug=True, port=5000)