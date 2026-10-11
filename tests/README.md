# Export-Test

Prüft, ob das Werkzeug nach einer Änderung noch richtig schwärzt. Der Test bedient die Werkzeugdatei im Browser wie ein Mensch, fängt die exportierten Dateien ab und prüft sie **mit anderen Programmen als das Werkzeug selbst**: Text mit pypdf und pdftotext, Pixel mit Poppler und Pillow, eine Zweit-Erkennung mit Tesseract. Die eingebaute Selbstprüfung des Werkzeugs läuft mit derselben Bibliothek (PDF.js) wie der Export; ein Fehler, der beide trifft, bliebe dort unbemerkt.

Der Test ist für die Entwicklung gedacht, nicht für Nutzerinnen und Nutzer. Er prüft Testdokumente mit bekannten Geheimnissen, nicht das eigene Dokument.

## Aufruf

```
pip install -r tests/requirements.txt
python3 -m playwright install chromium        # entfällt, wenn ein Chromium vorhanden ist
python3 tests/run.py ai-upload-cleaner6.0.html
```

- `--nur-schnell` lässt die Texterkennung weg.
- `CHROMIUM_PATH=/pfad/zu/chromium` nutzt einen vorhandenen Browser.
- Außerdem nötig: Poppler (`pdftotext`, `pdftoppm`). Tesseract mit deutschem Modell ist optional; fehlt es, entfallen die Zweit-Erkennungen.
- Ergebnis: Tabelle auf der Konsole, Bericht in `tests/out/bericht.md` mit SHA-256 der geprüften Datei, Exit-Code 1 bei einem Fehler. Die Exporte liegen in `tests/out/exporte/`.

Ein Lauf gegen die 6.0 dauert in Chromium rund 16 Sekunden (gemessen am 11.10.2026).

**Auf GitHub:** `.github/workflows/export-test.yml` führt den Test bei jeder Änderung an einer Werkzeugdatei oder an `tests/` aus, für die 6.0 und die 3.0. Der Bericht steht in der Zusammenfassung des Laufs (Reiter „Actions“), Bericht und Exporte hängen 30 Tage als Anhang am Lauf. Starten lässt er sich dort auch von Hand („Run workflow“).

## Was geprüft wird

| Szenario | Bedienung | Prüfungen am Export |
| --- | --- | --- |
| PDF mit Textebene, 3 Seiten | Suche „Alle Muster“ (in 3.0: IBAN, E-Mail, Telefon einzeln), Textsuche nach dem Namen, „Alle schwärzen“, Seite 3 ausschließen, PDF-Export | kein Text (pypdf, pdftotext), keine Textbefehle, keine eingebetteten Schriften, keine Geheimnisse in den Rohbytes, Metadaten ohne Namen, keine Anhänge, 2 Seiten, jedes Geheimnis zu mindestens 98 % schwarz, Kontrollzeile lesbar, Tesseract findet kein Geheimnis |
| Ausweis als Bild | Box über den Namen ziehen (die Seite darf dabei nicht verrutschen), Beschriftung [Name], Ausschnitt ziehen, PNG-Export | Seitenverhältnis wie der Ausschnitt, rote Nummer außerhalb fehlt, Name schwarz mit weißer Beschriftung, Kontrollzeile lesbar, keine PNG-Metadaten, Tesseract findet den Namen nicht |
| Foto mit GPS | laden, ohne Box exportieren | keine EXIF-Daten, Kamera und GPS nicht in den Rohbytes |
| Scan ohne Textebene | Texterkennung Deutsch, IBAN-Suche, PNG-Export | IBAN schwarz, Kontrollzeile lesbar, Tesseract findet die IBAN nicht |
| alle | | keine Netzwerkanfragen, keine Fehler in der Konsole, Download erst nach bestandener Selbstprüfung |

**Gegenprobe:** Vor den Szenarien laufen dieselben Prüfungen gegen die ungeschwärzten Originale und müssen dort anschlagen. Nur die Kontrollzeilen dürfen bestehen; sie sichern ab, dass nicht zu viel geschwärzt wird. Eine Prüfung, die am Original nicht anschlägt, beweist nichts.

**Nachweis der Wirksamkeit:** In einer Kopie der 6.0 wurden die Boxen auf Seite 2 beim Export weggelassen. Die Selbstprüfung des Werkzeugs meldete „Fertig und geprüft · 5 von 5 Boxflächen schwarz“, der Test schlug dreimal an (Name und IBAN auf Seite 2 lesbar, Tesseract fand beide).

## Grenzen

- Der Test deckt die Fälle ab, die er kennt. Er beweist nicht, dass es keine anderen Fehler gibt.
- Echte Scans aus der Praxis (schief, schwacher Kontrast, Handschrift) ersetzt er nicht.
- Geprüft wird nur in Chromium. Firefox und WebKit wären mit Playwright möglich, sind aber nicht eingerichtet.
- Bedient wird die Seitenansicht mit Maus, nicht der Vollbild-Editor und keine Touch-Gesten.

## Dateien

| Datei | Zweck |
| --- | --- |
| `make_fixtures.py` | erzeugt die Testdokumente und hält die Lage jedes Geheimnisses in `fixtures.json` fest |
| `checks.py` | die unabhängigen Prüfungen |
| `run.py` | Bedienung im Browser, Gegenprobe, Bericht |
| `requirements.txt` | Python-Abhängigkeiten in den getesteten Versionen |
