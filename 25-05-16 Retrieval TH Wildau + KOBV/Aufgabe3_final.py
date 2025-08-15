# Description: Aufgabe 3: COinS Abfrage aus KBOV Portal
# Author: Leonie Giessler
# Created: 2025-08-12
# Version: 1.0
# Licence: GNU GPLv3

import requests
import re
from urllib.parse import parse_qs, unquote_plus
from html import unescape


def parse_html(html):
  # suche nach dem folgenden Pattern
  pattern = r'<span[^>]*class="[^"]*\bZ3988\b[^"]*"[^>]*title="([^"]+)"'
  matches = re.findall(pattern, html)
  # gebe die Übereinstimmungen zurück
  return matches

def parse_werte(e_records):
  # die einzelnen Records "unescapen" (&amp; in & umwandeln)
  ue_records = unescape(e_records)
  # führendes "?" entfernen
  if ue_records.startswith('?'):
    ue_records = ue_records[1:]
  # den bearbeiteten records string parse_qs um die Attribute und ihre Werte aufzubereiten
  rohdaten = parse_qs(ue_records, keep_blank_values = True)
  # bearbeitete Rohdaten unquotiert (ohne Anführungszeichen) zurückgeben
  return {k: [unquote_plus(value) for value in values] for k, values in rohdaten.items()}

def ergebnisse_formatieren(rohdaten):
  # kleine Routinendefinition für "suche den ersten Eintrag"
  def first(attribute):
    for a in attribute:
      if a in rohdaten and rohdaten[a]:
        return rohdaten[a][0]
    return ""

  # kleine Routinendefinition für "suche alle Einträge und verbinde"
  def join(attribute):
    # leeres Array erstellen
    werte = []
    # Werte suchen
    for a in attribute:
      werte.extend(rohdaten.get(a, []))
    # Duplikate über dict entfernen und kombiniert ausgeben
    return " , ".join(dict.fromkeys(werte))

  # formatierten Vektor zurückgeben
  return {
    "author": join(["rft.au"]),
    "title": join(["rft.atitle", "rft.title", "rft.btitle", "rft.jtitle"]),
    "issn": join(["rft.issn"]),
    "isbn": join(["rft.isbn"]),
    "year": first(["rft.date"]),
    "volume": first(["rft.volume"]),
    "issue": first(["rft.issue"]),
    "pages": join(["rft.pages"]),
    "publisher": join(["rft.publisher", "rft.pub"]),
    "genre": first(["rft.genre"]),
  }

# main

## Abfrage der Funktionsweise
#print(f"\nMetadaten via COinS aus dem KOBV-Portal lesen.\n")
## Eingabe der Anfrage-URL (generierung der Anfrage-URL war nicht teil der Aufgabe)
#url = input("Bitte die URL angeben (OpenURL-Ergebnis- oder Detailseite): ").strip()

# Egal, wir machen es trotzdem, ab geht die wilde Fahrt
# URL für Abfragen zusammenbauen
print(f"\nMetadaten via COinS aus dem KOBV-Portal lesen.\n")
# Katalog abfragen
print(f"In welchem Katalog suchen? 1 = KOBV-Portal ; 2 = Fernleihindex")
katalog = input(f"Bitte jetzt den Katalog angeben: ").strip()

# Katalognummer auf Richtigkeit prüfen
if not katalog.isdigit() or int(katalog) not in (1, 2):
  print("Ungültige Katalognummer.")
  exit(1)

katalogurl = ["k2", "gvi"]

#if katalog == "1":
#  katalogurl = "k2"
#if katalog == "2":
#  katalogurl = "gvi"

print(f"Wonach soll gesucht werden?")
print(f"1 für Autor")
print(f"2 für Titel")
print(f"3 für ISBN")
print(f"4 für ISSN")
# Funktionsweise abfragen
funktionsweise = input(f"Bitte jetzt die Suchanfrage auswählen: ").strip()

# Funktionsweise auf Richtigkeit prüfen
if not funktionsweise.isdigit() or int(funktionsweise) not in range(1, 4):
  print("Ungültige Auswahl für Suchanfrage.")
  exit(1)

# Suchquery abfragen
query = input(f"Bitte jetzt die Suchanfrage eingeben: ").strip()

funktion = ["rft.au", "rft.title", "rft.isbn", "rft.issn"]

# Such URL zusammensetzen
url = f"https://openurl.kobv.de/{katalogurl[int(katalog) - 1]}?{funktion[int(funktionsweise) - 1]}={query}"

try:
  try:
    # html-Abfrage der URL
    antwort = requests.get(url, timeout = 30)
    antwort.raise_for_status()
  except requests.RequestException as e:
    print(f"Fehler bei der Anfrage: {e}")
    exit()
  # parsen der Antwort in einzelne records
  records = parse_html(antwort.text)
  # bekomme die einzelnen Werte aus den Schlüsseln Pro gefundenen Record, und schreibe sie Formatiert in den Ergebnisvektor
  ergebnisse = [ergebnisse_formatieren(parse_werte(ergebnis)) for ergebnis in records]



  # über die Ergebnisse iterieren
  for i, rec in enumerate(ergebnisse, 1):
    # Treffernummer ausgeben
    print(f"[Treffer {i}]")
    # einzelne Werte je Treffer mit Attributnamen ausgeben
    for j, wert in rec.items():
      if wert:
        # Einrückung vorne, ersten Buchstaben des Bezeichners groß schreiben
        print(f"  {j.capitalize():10s}: {wert}")
    # eine Leerzeile zum Schluss
    print()

# Fehlerbehandlung
except Exception as e:
  print(f"Fehler: {e}")