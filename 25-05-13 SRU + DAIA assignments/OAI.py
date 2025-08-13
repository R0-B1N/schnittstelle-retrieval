# Description: Aufgabe 1: SRU Abfrage
# Author: Leonie Giessler
# Created: 2025-06-15
# Version: 1.0
# Licence: GNU GPLv3

# benoetigte Bibliotheken importieren
import xml.etree.ElementTree as ET
import requests

def Suche_OAI(Suchtext):
    # abfrage nach Feld (Titel, Autor oder ISBN)
    # anschliessende Abfrage mit Suchtext und Query
    Antwort = requests.get(f"https://www.db-thueringen.de/servlets/OAIDataProvider?verb=ListRecords&metadataPrefix=marcxml&identifier=oai:www.db-thueringen.de:{Suchtext}")

    
    # mittels ElementTree xml-String in Tabellenformat konvertieren
    Wurzel = ET.fromstring(Antwort.content)
    
    # Ergebnisse ermitteln
    # leer initialisieren
    Ergebnisse = []
    # iterieren ueber Ergebiselemente im Baum
    for ergebnis in Wurzel.findall(".//marc21:record", {"marc21": "http://www.loc.gov/MARC21/slim"}):
        # Ergebnis pro Iteration ermitteln, leer initialisieren
        data = {
            "ISBN": [], #020
            "ISSN": [], #022
            "Sprache": "", #041
            "Autor": [], #100 / 700
            "Titel": "", #245
            "Jahr": "", #264$c
            "phyDesc": [], #300
            "Reihentitel": "", #490
            "Schlagworte": [] #650
        }
        
        # iterieren ueber datafield Objekte in einzelnen Ergebniselementen + subfields
        for datafield in ergebnis.findall("marc21:datafield", {"marc21": "http://www.loc.gov/MARC21/slim"}):
            tag = datafield.get('tag')
            subfields = []
            subfields = {sub.get('code'): sub.text for sub in datafield.findall("marc21:subfield", {"marc21": "http://www.loc.gov/MARC21/slim"})}
            
            # wenn Tags und subfields passen, Inhalt extrahieren und in data schreiben
            if tag == "020" and "a" in subfields:
                data["ISBN"].append(subfields["a"])
            elif tag == "022" and "a" in subfields:
                data["ISSN"].append(subfields["a"])
            elif tag == "041" and "a" in subfields:
                data["Sprache"] = subfields["a"]
            elif tag in ("100", "700") and "a" in subfields:
                data["Autor"].append(subfields["a"])
            elif tag == "245" and "a" in subfields:
                data["Titel"] = subfields["a"]
            elif tag == "264" and "c" in subfields:
                data["Jahr"].append(subfields["a"])
            elif tag == "300" and "a" in subfields:
                data["phyDesc"].append(subfields["a"])
            elif tag == "490" and "a" in subfields:
                data["Reihentitel"] = subfields["a"]
            elif tag == "650" and "a" in subfields:
                data["Schlagworte"].append(subfields["a"])
            
        # erstellten data-Vektor an Ergebnismatrix anhaengen 
        Ergebnisse.append(data)
        
    # gesamte Ergebnismatrix zurueckgeben
    return Ergebnisse

# main
# Suchfeld angeben und danach den Suchbegriff, Ergebnismenge definieren
Suchbegriff = input("Suchbegriff: ").strip()

try:
    Liste = Suche_OAI(Suchbegriff)
    
    # mit Ergebnismatrix ausgabe generieren (mit schoenheitsleerzeichen :D)
    for i, eintrag in enumerate(Liste, start=1):
        # TBD
        print(f"\nErgebnis Nr. {i}:")
        print(f"Titel:       {eintrag['Titel']}")
        print(f"Autor(en):   {'; '.join(eintrag['Autor'])}")
        print(f"ISBN(s):     {'; '.join(eintrag['ISBN'])}")
        print(f"Schlagworte: {'; '.join(eintrag['Schlagworte'])}")
        
# Fehlerbehandlung mit ausgabe Fehler
except Exception as e:
    print(f"Fehler: {e}")

    
# https://www.db-thueringen.de/servlets/OAIDataProvider?verb=GetRecord&metadataPrefix=marcxml&identifier=oai:www.db-thueringen.de:dbt_mods_00066190
    
# Suchqueries von unterschiedlichen Verbundszentralen
# https://verbundwiki.gbv.de/display/VZG/SRU/dnb?version=1.1&operation=searchRetrieve&query=WOE%3DGoethe&recordSchema=MARC21-xml
# https://sru.bsz-bw.de/swb?version=1.1&query=pica.all%3DGoethe&operation=searchRetrieve&recordSchema=marcxmlk10os&maximumRecords=10
# http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.all%3DGoethe&recordSchema=marcxml&maximumRecords=10


