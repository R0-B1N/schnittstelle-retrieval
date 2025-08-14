# Description: Aufgabe 1: OAI Abfrage der neusten OPUS Dokumente
# Author: Leonie Giessler
# Created: 2025-08-12
# Version: 1.0
# Licence: GNU GPLv3

# benötigte Bibliotheken importieren
import xml.etree.ElementTree as ET
import requests
import datetime as dt
import json

# BasisURL definieren
BASE_URL = "https://opus4.kobv.de/opus4-th-wildau/oai"

# Namespaces definieren
NAMESPACES = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
}

# Globalen Merker für die Ergebnisse definieren
Ergebnisse = []

# Lese Datensätze aus Antwort
def lese_datensaetze(http_antwort):
    # Wurzel der xml-Antwort definieren
    Wurzel = ET.fromstring(http_antwort.content)
    # print(f"DEBUG: Antwort in Wurzel geparsed")

    # Durch einzelne records im Baum iterieren
    for ergebnis in Wurzel.findall(".//oai:ListRecords/oai:record", NAMESPACES):
        # leeres Datenarray definieren
        data = {
            "oai_identifier": "",
            "datestamp": "",
            "deleted": "",
            "title": "",
            "creator": "",
            "subject": "",
            "description": "",
            "publisher": "",
            "contributor": "",
            "date": "",
            "type": "",
            "format": "",
            "identifier": "",
            "source": "",
            "language": "",
            "relation": "",
            "coverage": "",
            "rights": "",
        }

        # die wesentlichen Header-Informationen analysieren
        header = ergebnis.find("oai:header", NAMESPACES)
        print(f"DEBUG: Header: {header}")
        identifier = header.findtext("oai:identifier", default = "", namespaces = NAMESPACES)
        print(f"DEBUG: identifier: {identifier}")
        datestamp = header.findtext("oai:datestamp", default = "", namespaces = NAMESPACES)
        print(f"DEBUG: datestamp: {datestamp}")
        deleted = header.attrib.get("status") == "deleted"
        print(f"DEBUG: deleted: {deleted}")

        # Wenn Eintrag gelöscht, dann überspringen (da bei gelöschten Einträgen nur noch OAI-ID existiert, crasht der metadaten-scrape)
        if not deleted:
            # Metadaten Stamm finden und direkt in den Dublin Core gehen
            metadata = ergebnis.find("oai:metadata/oai_dc:dc", NAMESPACES)

            # Routine zum Suchen der Textfelder
            def texts(tag):
                return [el.text.strip() for el in metadata.findall(f"dc:{tag}", NAMESPACES) if el.text]

            # Befüllen des temporären Data-Arrays
            data["oai_identifier"] = identifier
            data["datestamp"] = datestamp
            data["deleted"] = deleted
            data["title"] = '; '.join(texts("title"))
            data["creator"] = '; '.join(texts("creator"))
            data["subject"] = '; '.join(texts("subject"))
            data["description"] = '; '.join(texts("description"))
            data["publisher"] = '; '.join(texts("publisher"))
            data["contributor"] = '; '.join(texts("contributor"))
            data["date"] = '; '.join(texts("date"))
            data["type"] = '; '.join(texts("type"))
            data["format"] = '; '.join(texts("format"))
            data["identifier"] = '; '.join(texts("identifier"))
            data["source"] = '; '.join(texts("source"))
            data["language"] = '; '.join(texts("language"))
            data["relation"] = '; '.join(texts("relation"))
            data["coverage"] = '; '.join(texts("coverage"))
            data["rights"] = '; '.join(texts("rights"))
            # print(f"DEBUG: metadata done")

            # temporäres Array an Ergebnisarray anhängen
            Ergebnisse.append(data)
            # print(f"DEBUG: Ergebnis angehangen")

    # Resumption-Token für diesen Durchlauf auf leer setzen
    resumption_token = ""

    # Resumption-Token finden
    for res_element in Wurzel.findall(".//oai:ListRecords/oai:resumptionToken", NAMESPACES):
        # print(f"DEBUG: Resumption Element gesetzt")
        # wenn Element nicht leer oder existent ist, dann schreibe den Token
        if res_element is not None and (res_element.text or "").strip():
            print(f"DEBUG: Resumption Token gefunden")
            resumption_token = res_element.text.strip()
        else:
            print(f"DEBUG: Resumption Token leer")
            resumption_token = ""
    # Resumption-Token zurück geben
    return resumption_token

# json schreiben
def drucke_ergebnisse():
    # aktuelle Zeit für Zeitstempel in Datei
    datetime = dt.datetime.now()
    # print(f"DEBUG: Starte Ausgabe in .json")
    # json Datei öffnen, w für write
    with open(f"OAIexport_{datetime}.json", "w", encoding = "utf-8") as f:
        # json Dump über Ergebnisvektor
        json.dump(Ergebnisse, f, ensure_ascii = False, indent = 2, sort_keys = False, separators = (",", ": "))
    print(f"OK: {len(Ergebnisse)} Datensätze gespeichert in OAIexport_{datetime}.json")

# main
# Abfrage der Funktionsweise
print(f"\nBitte Funktionsweise definieren\n")
print(f"1 = Abruf aller Datensätze der letzten Woche")
print(f"2 = Abruf aller Datensätze des letzten Monats")
print(f"3 = Eingabe einer benutzerdefinierten Zeitspanne")
Funktionsweise = input("Funktionsweise: ").strip()

# weiter als Resumption-Token speicher für Fortführung der Anfrage
weiter = ""

# Try um im Fehlerfall mit Meldung abzubrechen
try:
    if Funktionsweise == "1":
        # aktuelles Datum - 7 Tage rechnen, um auf Woche zu kommen
        dt_from = dt.date.today() - dt.timedelta(days=7)
        # Request für Abfrage
        Antwort = requests.get(f"{BASE_URL}?verb=ListRecords&metadataPrefix=oai_dc&from={dt_from}")
        print(f"DEBUG: {BASE_URL}?verb=ListRecords&metadataPrefix=oai_dc&from={dt_from}")
        # print(f"DEBUG: Antwort erhalten, Starte Routine")
        # Routine Starten mit dem Ergebnis
        weiter = lese_datensaetze(Antwort)
    elif Funktionsweise == "2":
        # aktuelles Datum - 30 Tage rechnen, um auf Monat zu kommen
        dt_from = dt.date.today() - dt.timedelta(days=30)
        # Request für Abfrage
        Antwort = requests.get(f"{BASE_URL}?verb=ListRecords&metadataPrefix=oai_dc&from={dt_from}")
        print(f"DEBUG: {BASE_URL}?verb=ListRecords&metadataPrefix=oai_dc&from={dt_from}")
        # print(f"DEBUG: Antwort erhalten, Starte Routine")
        # Routine Starten mit dem Ergebnis
        weiter = lese_datensaetze(Antwort)
    elif Funktionsweise == "3":
        print(f"Datumsformat 'YYYY-MM-DD'")
        # Datumsabfrage für von bis Funktion
        dt_from = input("Bitte Datum von angeben: ").strip()
        dt_until = input("Bitte Datum von angeben: ").strip()
        # Request für Abfrage
        Antwort = requests.get(f"{BASE_URL}?verb=ListRecords&metadataPrefix=oai_dc&from={dt_from}&until={dt_until}")
        print(f"DEBUG: {BASE_URL}?verb=ListRecords&metadataPrefix=oai_dc&from={dt_from}&until={dt_until}")
        # print(f"DEBUG: Antwort erhalten, Starte Routine")
        # Routine Starten mit dem Ergebnis
        weiter = lese_datensaetze(Antwort)
    else:
        # Im Fehlerfall der falschen Eingabe
        print("Bitte richtige Funktionsweise auswählen\n")

# Im Fehlerfall
except Exception as e:
    print(f"Fehler: {e}")

# Solange ein Resumption-Token in weiter zurückkommt, mache weiter
while weiter is not (None or ""):
    print(f"DEBUG: Weiter nach Resumption-Token")
    # Request für fortgeführte Anfrage
    Antwort = requests.get(f"{BASE_URL}?verb=ListRecords&resumptionToken={weiter}")
    # Routine Starten mit dem Ergebnis
    weiter = lese_datensaetze(Antwort)

# Ergebnisse ausgeben
drucke_ergebnisse()