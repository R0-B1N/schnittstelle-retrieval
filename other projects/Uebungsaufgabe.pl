# Description: Uebungsaufgabe: ISBN-10 in ISBN-13 konvertieren
# Author: Leonie Giessler
# Created: 2025-06-15
# Version: 1.0
# Licence: GNU GPLv3

#!/usr/bin/perl
use strict;
use warnings;

# Einlesen der ISBN-10 ueber Aufrufargument
# my $Isbn10 = shift or die "Keine Eingabe erfolgt\n";

# Einlesen der ISBN-10 ueber Eingabe
my $Isbn10 = <STDIN>;
if ($Isbn10 eq "\n") {
    die "Keine Eingabe erfolgt\n";
}

# Bindestriche entfernen
$Isbn10 =~ s/-//g;
#alle Buchstaben in Grossbuchstaben wandeln
$Isbn10 = uc($Isbn10);

# Pruefen auf gueltiges ISBN-10 Format (String beginnt mit 9 Zahlen und endet auf X oder Zahl)
unless ($Isbn10 =~ /^\d{9}[\dX]$/) {
    die "ISBN-10 im falschen Format: $Isbn10\n";
}

# Pruefziffer kontrollieren
# Initalisierung der Summe auf 0
my $Pruefsumme10 = 0;
# Schleife ueber 8 Ziffern zum Multiplizieren
for my $i (0..8) {
    # Aufaddierung der Summe mit den multiplizierten Zahlen (dabei $i + 1 da Schleife von 0 beginnend)
    $Pruefsumme10 += ($i + 1) * substr($Isbn10, $i, 1);
}
# Modulo von Summe mit 11
my $Check10 = $Pruefsumme10 % 11;
# wenn Modulo gleich 10, dann Pruefziffer = 'X'
if ($Check10 == 10) {
    $Check10 = 'X';
}
# Pruefziffer der eingegebenen ISBN-10 extrahieren
my $LetzeElement10 = substr($Isbn10, 9, 1);
# Pruefziffer und Ergebnis vergleichen
unless ($Check10 eq $LetzeElement10) {
    die "ISBN-10 Pruefziffer ungueltig: eingegeben '$LetzeElement10', errechnet '$Check10'!\n";
}

# Konvertierung in ISBN-13 durch voanstellen von '978' und berechnung neuer Pruefziffer
my $Isbn13_oP = '978' . substr($Isbn10, 0, 9);

# Berechnung neuer Pruefziffer
# Initalisierung der Summe auf 0
my $Pruefsumme13 = 0;
# Schleife ueber 12 Ziffern zum Multiplizieren
for my $i (0..11) {
    # Einzelne Ziffern abwechselnd mit 1 und 3 multiplizieren
    if ($i % 2 == 0) {
        $Pruefsumme13 += 1 * substr($Isbn13_oP, $i, 1);
    } else { 
        $Pruefsumme13 += 3 * substr($Isbn13_oP, $i, 1);
    }
}
# Pruefziffer errechnen (naechster Summand zu 10er Summe)
my $Check13 = 10 - ($Pruefsumme13 % 10);

# Ausgabe der ISBN-13
my $Isbn13 = $Isbn13_oP . $Check13;
print "ISBN-13: $Isbn13\n";
