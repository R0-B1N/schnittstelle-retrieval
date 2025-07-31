# Description: Aufgabe 1: SRU Abfrage
# Author: Leonie Giessler
# Created: 2025-06-15
# Version: 1.0
# Licence: GNU GPLv3

# benoetigte Bibliotheken importieren
import xml.etree.ElementTree as ET
import requests

def Suche_SRU(Feld, Text, MaxErg):
    # abfrage nach Feld (Titel, Autor oder ISBN)
    # anschliessende Abfrage mit Suchtext und Query
    if Feld == 'titel':
        Antwort = requests.get(f"http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&recordSchema=marcxml&query=pica.tit%3D{Text}&maximumRecords={MaxErg}")
    elif Feld == 'autor':
        Antwort = requests.get(f"http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&recordSchema=marcxml&query=pica.per%3D{Text}&maximumRecords={MaxErg}")
    elif Feld == 'isbn':
        Antwort = requests.get(f"http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&recordSchema=marcxml&query=pica.isb%3D{Text}&maximumRecords={MaxErg}")
    else:
        raise ValueError("Fehlerhaftes Suchfeld angegeben. Erwartet: titel, autor, isbn")
    
    # mittels ElementTree xml-String in Tabellenformat konvertieren
    Wurzel = ET.fromstring(Antwort.content)
    
    # Ergebnisse ermitteln
    # leer initialisieren
    Ergebnisse = []
    # iterieren ueber Ergebiselemente im Baum
    for ergebnis in Wurzel.findall(".//marc:record", {"marc": "http://www.loc.gov/MARC21/slim"}):
        # Ergebnis pro Iteration ermitteln, leer initialisieren
        data = {
            "ISBN": [],
            "Autor": [],
            "Titel": "",
            "Schlagworte": []
        }
        
        # iterieren ueber datafield Objekte in einzelnen Ergebniselementen + subfields
        for datafield in ergebnis.findall("marc:datafield", {"marc": "http://www.loc.gov/MARC21/slim"}):
            tag = datafield.get('tag')
            subfields = []
            subfields = {sub.get('code'): sub.text for sub in datafield.findall("marc:subfield", {"marc": "http://www.loc.gov/MARC21/slim"})}
            
            # wenn Tags und subfields passen, Inhalt extrahieren und in data schreiben
            if tag == "245" and "a" in subfields:
                data["Titel"] = subfields["a"]
            elif tag in ("100", "700") and "a" in subfields:
                data["Autor"].append(subfields["a"])
            elif tag == "020" and "a" in subfields:
                data["ISBN"].append(subfields["a"])
            elif tag == "650" and "a" in subfields:
                data["Schlagworte"].append(subfields["a"])
            
        # erstellten data-Vektor an Ergebnismatrix anhaengen 
        Ergebnisse.append(data)
        
    # gesamte Ergebnismatrix zurueckgeben
    return Ergebnisse

# main
# Suchfeld angeben und danach den Suchbegriff, Ergebnismenge definieren
Suchfeld = input("Suchfeld (titel, autor oder isbn): ").strip().lower()
Suchbegriff = input("Suchbegriff: ").strip()
Menge = input("Anzuzeigende Ergebnisse: ").strip()

try:
    Liste = Suche_SRU(Suchfeld, Suchbegriff, Menge)
    
    # mit Ergebnismatrix ausgabe generieren (mit schoenheitsleerzeichen :D)
    for i, eintrag in enumerate(Liste, start=1):
        print(f"\nErgebnis Nr. {i}:")
        print(f"Titel:       {eintrag['Titel']}")
        print(f"Autor(en):   {'; '.join(eintrag['Autor'])}")
        print(f"ISBN(s):     {'; '.join(eintrag['ISBN'])}")
        print(f"Schlagworte: {'; '.join(eintrag['Schlagworte'])}")
        
# Fehlerbehandlung mit ausgabe Fehler
except Exception as e:
    print(f"Fehler: {e}")

# Suchqueries von unterschiedlichen Verbundszentralen
# https://verbundwiki.gbv.de/display/VZG/SRU/dnb?version=1.1&operation=searchRetrieve&query=WOE%3DGoethe&recordSchema=MARC21-xml
# https://sru.bsz-bw.de/swb?version=1.1&query=pica.all%3DGoethe&operation=searchRetrieve&recordSchema=marcxmlk10os&maximumRecords=10
# http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.all%3DGoethe&recordSchema=marcxml&maximumRecords=10
