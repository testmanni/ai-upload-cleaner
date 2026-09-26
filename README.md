# AI Upload Cleaner

Schwärzen, bevor du hochlädst. Eine einzelne HTML-Datei, vollständig offline – der Text unter den schwarzen Flächen ist danach wirklich weg, nicht nur verdeckt.

**Live ausprobieren:** [ai-upload-cleaner.com](https://ai-upload-cleaner.com)

## Der Selbsttest (Warum dieses Werkzeug?)

Der schwarze Balken, den du in Word oder Acrobat über eine Stelle ziehst, **entfernt den Text nicht** – er liegt darunter im Klartext weiter und ist mit Kopieren-Einfügen wieder lesbar.

Mach den Test mit einem „geschwärzten" PDF:

1. Markiere die schwarze Stelle mit der Maus.
2. Drücke Strg+C.
3. Füge es irgendwo ein (Strg+V).

Kommt Text heraus? Dann war nie etwas geschützt.

Dieses Werkzeug rendert jede Seite zu einem Bild und brennt die schwarzen Flächen in die Pixel. Im Ergebnis existiert der überdeckte Text physisch nicht mehr.

## Benutzung

Datei `ai-upload-cleaner.html` herunterladen, doppelklicken, im Browser öffnen. Dokument oder Bild hineinziehen, Stellen markieren, geschwärzte Kopie exportieren. Kein Server, kein Account, keine Installation.

WLAN ausschalten und es trotzdem benutzen – das ist der Beweis, dass nichts hochgeladen wird.

## Grenzen (ehrlich)

- Das Werkzeug findet sensible Stellen **nicht** selbst. Es schwärzt nur, was du markierst. Die Prüfung bleibt bei dir – eine Checkliste vor dem Export erinnert an typische Stellen.
- Es garantiert keine vollständige Anonymisierung. Prüfe das Ergebnis nach dem Export selbst mit dem Strg+C-Test.

## Version 3.0 (Datei `ai-upload-cleaner3.0.html`)

Alles aus der 2.0, dazu:

- **Text markieren statt zeichnen.** Bei PDFs mit Textebene liegt eine unsichtbare Textschicht über der Seite. Text mit der Maus überstreichen oder am Handy ein Wort gedrückt halten, dann „Auswahl schwärzen". Die Boxen entstehen zeilengenau aus den echten Schriftmaßen, mit Sicherheitsrand. Umschalter „Box / Text" oben, Tasten B und T.
- **Suchen und schwärzen.** Begriff eingeben oder ein Muster wählen (IBAN, E-Mail-Adresse, Telefonnummer), Treffer über alle Seiten durchgehen, einzeln oder alle schwärzen. Muster sind Faustregeln, jeder Treffer wird bestätigt. Aus einer Textauswahl heraus: „Überall suchen". Strg+F öffnet die Suche.
- **Beschriftete Boxen.** Optional steht in Weiß auf der Fläche, was entfernt wurde: [Name], [IBAN], [Adresse] oder Freitext. Wird ins Bild gerechnet, keine Textebene. Die Prüfung nach dem Export kennt die Beschriftung und verlangt, dass der Rest der Fläche schwarz ist.
- **Box auf alle Seiten**, **Seite drehen**, **Seite ausschließen**, **nur Ausschnitt exportieren** (Rahmen ziehen, nur dieser Bereich landet im Export).
- **Seitenübersicht** mit Miniaturen, Boxenzahl, Suchtreffern und Markierung ausgeschlossener Seiten. Vor dem Export: „Seiten ohne Box: 2, 4".
- **Mehrere Dateien in einem Export.** PDFs und Bilder gemischt, in der gewählten Reihenfolge.
- **Boxen-Vorlage speichern und laden** (nur Koordinaten, nie Inhalte), **wählbarer Dateiname**, **Dunkelmodus** nach Systemeinstellung.

Text markieren und Suche funktionieren nur bei PDFs mit Textebene. Bei Scans und Fotos gibt es keine, dort bleibt es beim Zeichnen. Das Werkzeug zeigt beim Laden an, ob eine Textebene vorhanden ist. Nachprüfen der eingebetteten Bibliotheken: `python3 build/libs.py verify ai-upload-cleaner3.0.html`.

## Version 2.0 (Datei `ai-upload-cleaner2.0.html`)

Gleiche Idee, gleiche eine Datei, aber:

- **Vollbild-Editor fürs Handy.** Ein Finger zeichnet, zwei Finger zoomen und schieben, Doppeltipp zoomt, eine Lupe zeigt die Stelle unter dem Finger. Öffnet sich auf Touch-Geräten automatisch. Am Rechner: Button „Vollbild bearbeiten", Mausrad schiebt, Strg+Mausrad zoomt.
- **Eingebaute Prüfung nach jedem Export.** Das Werkzeug öffnet sein eigenes Ergebnis erneut und meldet Seiten, Textzeichen (muss 0 sein) und ob die Boxflächen im Ergebnis schwarz sind. Nur dann wird die Datei ausgeliefert.
- **Content-Security-Policy ohne Netz.** Die Datei verbietet sich selbst jede Verbindung (`connect-src 'none'`, keine externen Skripte, Bilder, Schriften). Der Browser setzt das durch, unabhängig vom Code.
- **Aktuelle Bibliotheken, nachprüfbar.** PDF.js 6.3.289 (Legacy-Build), jsPDF 4.2.1 und zwei WebAssembly-Decoder, byteidentisch mit den npm-Paketen. Prüfen ohne Netz: `python3 build/libs.py verify ai-upload-cleaner2.0.html`. Prüfsummen in `build/CHECKSUMS.txt`. PDF.js läuft ohne `eval`.
- **Rückgängig und Wiederholen** (Strg+Z, Strg+Y), Pfeiltasten zum Feinjustieren, Rückfrage beim Export ohne Box, Warnung beim Verlassen mit ungesicherten Boxen.
- **Metadaten des Originals** werden angezeigt (Autor, Programm, Datum, Formularfelder, Anhänge, bei Fotos EXIF und GPS) mit dem Hinweis, dass der Export nichts davon übernimmt.
- PDF-Seiten werden erst gerendert, wenn sie gebraucht werden. Lange PDFs öffnen sofort und belasten den Speicher nicht mehr.
- Boxränder werden beim Export auf ganze Pixel nach außen gerundet, keine Mischpixel am Rand.

Unterstützte Browser laut PDF.js-Legacy-Build: Chrome ab 125, Firefox ESR, Safari ab 18, jeweils die letzten zwei Versionen. Für Safari vor 18.4 rüstet die Datei zwei fehlende Funktionen selbst nach (Stream-Iteration und `bytes()`), sonst bricht die Prüfung nach dem Export ab.

## Aufbau des Repos

| Datei | Zweck |
|---|---|
| `ai-upload-cleaner.html` | das Werkzeug, Version 1.0 (einzelne Datei, offline) |
| `ai-upload-cleaner2.0.html` | das Werkzeug, Version 2.0 (siehe oben) |
| `ai-upload-cleaner3.0.html` | das Werkzeug, Version 3.0 (siehe oben) |
| `build/libs.py` | prüft oder erneuert die in 2.0 und 3.0 eingebetteten Bibliotheken |
| `build/CHECKSUMS.txt` | Herkunft und SHA-256-Prüfsummen der eingebetteten Bibliotheken und der Werkzeugdateien |
| `index.html` | Startseite mit interaktivem Selbsttest, verlinkt Werkzeug 3.0 und Anleitung |
| `anleitung.html` | kurze Bedienungsanleitung |
| `LICENSE` | MIT-Lizenz dieses Projekts |
| `NOTICE` | Übersicht der enthaltenen Drittanbieter-Software |
| `THIRD-PARTY-LICENSES.txt` | vollständige Lizenztexte von PDF.js und jsPDF |
| `licenses/` | unveränderte Original-Lizenzdateien der Bibliotheken |

## Lizenz

Dieses Werkzeug steht unter der MIT-Lizenz (siehe `LICENSE`).

Es bündelt zwei quelloffene Bibliotheken:
- **PDF.js** (Mozilla) – Apache License 2.0
- **jsPDF** (parallax / yWorks) – MIT License

Version 2.0 bettet zusätzlich zwei WebAssembly-Decoder aus dem PDF.js-Paket ein:
- **OpenJPEG** (JPEG 2000) – BSD 2-Clause
- **PDFium-JBIG2-Decoder** – BSD 3-Clause

Vollständige Lizenztexte in `THIRD-PARTY-LICENSES.txt` und im Ordner `licenses/`.
