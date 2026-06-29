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

## Aufbau des Repos

| Datei | Zweck |
|---|---|
| `ai-upload-cleaner.html` | das Werkzeug (einzelne Datei, offline) |
| `landing.html` | Landingpage mit interaktivem Selbsttest |
| `LICENSE` | MIT-Lizenz dieses Projekts |
| `NOTICE` | Übersicht der enthaltenen Drittanbieter-Software |
| `THIRD-PARTY-LICENSES.txt` | vollständige Lizenztexte von PDF.js und jsPDF |
| `licenses/` | unveränderte Original-Lizenzdateien der Bibliotheken |

## Lizenz

Dieses Werkzeug steht unter der MIT-Lizenz (siehe `LICENSE`).

Es bündelt zwei quelloffene Bibliotheken:
- **PDF.js** (Mozilla) – Apache License 2.0
- **jsPDF** (parallax / yWorks) – MIT License

Vollständige Lizenztexte in `THIRD-PARTY-LICENSES.txt` und im Ordner `licenses/`.
