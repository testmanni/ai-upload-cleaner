# Offene Punkte

Stand: 18.10.2026. Neue Punkte unten im passenden Abschnitt ergänzen, Erledigtes abhaken und mit Datum nach „Erledigt“ verschieben.

Kennzeichnung: **entschieden** (wird gebaut), **offen** (Entscheidung steht aus), **Idee** (irgendwann).

## AI Upload Cleaner 6.0 (Beta)

### Funktionsprüfung von Hand (läuft)

Jede Funktion einmal von Hand durchgehen, Auffälligkeiten unten als eigenen Punkt eintragen.

- [ ] Laden: PDF, JPG, PNG, mehrere Dateien zu einem Export
- [ ] Texterkennung: Deutsch, Englisch, beide; Abbrechen; Textebene eines PDFs ersetzen
- [ ] Box ziehen, Größe ändern, verschieben, löschen, Pfeiltasten
- [ ] Text markieren und „Auswahl schwärzen“ (PDF-Text und OCR-Text)
- [ ] Suche: Text, IBAN, E-Mail, Telefon, SSN/NI, „Alle Muster“ mit Fundstellenliste
- [ ] Prüftext: Filter, „geschwärzte Wörter anzeigen“, „Fundstellen prüfen“, TXT speichern
- [ ] Beschriftung der Boxen ([Name], [IBAN] …)
- [ ] Ausschnitt exportieren
- [ ] Seite ausschließen
- [ ] Box auf alle Seiten
- [ ] Vorlagen speichern und anwenden
- [ ] Seite drehen, vor und nach der Texterkennung
- [ ] Rückgängig und Wiederholen
- [ ] Export PDF und PNG, Qualitätsstufen, Selbstprüfung vor dem Download
- [ ] Zwischenablage: Screenshot mit Strg+V, „In Zwischenablage kopieren“
- [ ] Handy: Vollbild-Editor, Gesten, Lupe, Menü ⋯ (echte Geräte, nicht nur Emulation)
- [ ] Hell, Dunkel, System; Sprache Englisch
- [ ] Impressum, Datenschutz, Link zur Startseite

### Gefundene Punkte

- [ ] **offen** – Prüftext zeichenweise statt wortweise: Ist nur ein Teil eines Wortes geschwärzt (Suche nach „178“ in „178.15.50.82“), zeigt der Prüftext das ganze Wort im Klartext, obwohl im Export nur „5.50.82“ lesbar ist. Vorschlag: dieselbe Schätzung der Zeichenlage wie die Suche nutzen, ein Zeichen nur dann als verdeckt zeigen, wenn es vollständig unter der Box liegt. Mit festem Testfall (mit und ohne Texterkennung). Gemeldet 18.10.2026.
- [ ] **Idee** – Randfall: Eine aufrechte Seite quer drehen und dann die Texterkennung starten führt bei der Suche zu zu großen Boxen (zu viel geschwärzt, nicht zu wenig). In der Praxis selten. Gefunden 18.10.2026.
- [ ] **Idee** – Im Werkzeug prüfen, ob die Zahl der Boxen im Ergebnis zur Zahl der gezeichneten passt.
- [ ] **Idee** – Englische Oberfläche: Größenangaben in MB mit Punkt statt Komma.
- [ ] Bekannt, unschädlich: Das Telefonmuster meldet einen Teil einer IBAN zusätzlich als Telefonnummer.

### Tests

- [ ] **Idee** – Export-Test auch in Firefox und WebKit (bisher nur Chromium).
- [ ] **Idee** – Touch-Gesten und Vollbild-Editor im Test bedienen (bisher nur Maus in der Seitenansicht).

### Übernahme in die 3.0

- [ ] **offen** – Was aus der 6.0 in die stabile 3.0 übernommen wird, wird nach der Funktionsprüfung entschieden.

## AI Text Cleaner (ungetestete Entwicklungsversion)

- [ ] Praxistest mit erfundenen Daten; Fehlalarme der Vornamen-Hinweise und übersehene Namen als Testfall melden
- [ ] **entschieden, später** – Passwortschutz für die Namensliste (Verschlüsselung im Browser, offline)
- [ ] **offen** – Auf der Startseite verlinken, sobald er taugt
- [ ] **Idee** – Englische Oberfläche
- [ ] **Idee** – Import aus der Kanzleisoftware (CSV); dafür werden echte Exportformate gebraucht

## Startseite, Upload, Werkzeuge im Repository

- [ ] **Idee** – Design System auf den aktuellen Stand bringen (Startseite hat inzwischen Hell und Dunkel)
- [ ] **Idee** – Doppelten Export-Test auf main abstellen (läuft bei Push und im Upload-Ablauf)
- [ ] **Idee** – GitHub-Actions-Bausteine aktualisieren (Warnung: Node.js 20 veraltet)

## Weitere Ideen

- [ ] **Idee** – Prüfstation: geschwärzte Datei laden und prüfen lassen, was noch lesbar ist
- [ ] **Idee** – Ausweiskopie-Modus

## Erledigt

- [x] 12.10.2026 – AI Text Cleaner 0.2 online: Namensliste und eingebaute Vornamen
- [x] 12.10.2026 – AI Text Cleaner 0.1 online mit Hinweis „ungetestete Version“
