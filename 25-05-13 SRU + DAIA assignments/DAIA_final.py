# Description: Aufgabe 2: DAIA Verfuegbarkeitspruefung
# Author: Leonie Giessler
# Created: 2025-06-15
# Version: 1.0
# Licence: GNU GPLv3

# benoetigte Bibliotheken importieren
import xml.etree.ElementTree as ET
import requests

def query(ppn):
    try:
        # Abfrage mit PPN als Suchtext
        Antwort = requests.get(f"https://daia.gbv.de/isil/DE-7?id=ppn:{ppn}&format=xml", timeout=10)
        Antwort.raise_for_status()
    except requests.RequestException as e:
        print(f"Fehler bei der Anfrage: {e}")
        return []

    try:
        # mittels ElementTree xml-String in Tabellenformat konvertieren
        Wurzel = ET.fromstring(Antwort.content)
    except ET.ParseError as e:
        print(f"XML-Fehler: {e}")
        return []

    # Ergebnisse ermitteln
    # leer initialisieren
    ergebnis = []
    # iterieren ueber Ergebiselemente im Baum
    items = Wurzel.findall(".//daia:document/daia:item", {"daia": "http://ws.gbv.de/daia/"})

    for i, item in enumerate(items, start=1):
        # Einzelergebnisvektor leer initialisieren
        data = {
            "Item": "",
            "Ort": "",
            "available": [],
            "unavailable": []
        }
        
        # Labels suchen und in Variablen schreiben
        label = item.find("daia:label", {"daia": "http://ws.gbv.de/daia/"})
        ort = item.find("daia:department", {"daia": "http://ws.gbv.de/daia/"})
        av = item.findall("daia:available", {"daia": "http://ws.gbv.de/daia/"})
        unav = item.findall("daia:unavailable", {"daia": "http://ws.gbv.de/daia/"})
        
        # Datavektor beschreiben mit einzelnen Ergebnissen
        data["Item"] = label.text
        data["Ort"] = ort.text
        for avail in av:
            data["available"].append(avail.attrib.get("service"))
        for unavail in unav:
            data["unavailable"].append(unavail.attrib.get("service"))
        
        # Einzelergebnis an Gesamtergebnis anhaengen
        ergebnis.append(data)
    
    # zurueckgeben
    return ergebnis

# main
# PPN eingeben
Suchfeld = input("PPN: ").strip()
if not Suchfeld:
    print("Keine PPN eingegeben.")
    exit()

Ergebnisse = query(Suchfeld)

if len(Ergebnisse) == 0:
    print("Keine verfuegbaren Services gefunden")
else:
    for i, eintrag in enumerate(Ergebnisse, start=1):
        print(f"\nItem:                     {eintrag["Item"]}")
        print(f"Standort:                 {eintrag["Ort"]}")
        if len(eintrag["available"]) == 0:
            print("Verfügbare Dienste:       keine")
        else:
            print(f"Verfügbare Dienste:       {'; '.join(eintrag['available'])}")
        if len(eintrag["unavailable"]) == 0:
            print("Nicht verfügbare Dienste: keine")
        else:
            print(f"Nicht verfügbare Dienste: {'; '.join(eintrag['unavailable'])}")

# Test PPN: 253984971
