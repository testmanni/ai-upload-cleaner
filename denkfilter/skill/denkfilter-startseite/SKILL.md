---
name: denkfilter-startseite
description: 'Baut und pflegt die DENKFILTER-Startseite (denkfilter-startseite.html), die auf die aktuellen DENKFILTER-Grafiken verlinkt. Nach jedem neuen Lauf der Grafiken zieht der Skill die Seite nach: liest Stand und Fassungsvergleich aus den Grafiken, setzt Dateinamen und Links, übernimmt die Kurztexte wörtlich aus dem TL;DR, baut die Kennzahl-Tafeln aus belegten Werten und fährt alle Prüfungen (keine externen Abrufe, kein JavaScript, eingebettete Schriften, sieben Breiten). Immer nutzen bei „Startseite nachziehen“, „Startseite aktualisieren“, „neue Grafiken auf die Startseite“, „Startseite neu bauen“, „Denkfilter-Startseite“, „Landingpage für die Denkfilter“, „Stand auf der Startseite“ und auch dann, wenn nur neue Grafik-Dateien hochgeladen werden und von der Startseite die Rede ist. NICHT für das Aktualisieren der Grafiken selbst (infografik-update) oder den Bau neuer Grafiken (responsive-infografik-thesen).'
---

# DENKFILTER-Startseite

Die Startseite stellt die DENKFILTER-Grafiken vor. Pro Grafik gibt es einen Fall:
- Kennzahl-Tafel
- Leitfrage
- drei Kurztexte
- Kasten (Fassungsvergleich oder Fortschreibungsregeln)
- Link auf die Grafik

Dazu kommen Hero, Brücke, Fuß mit Index und die Einblender Impressum, Datenschutz und Methodik.

Die Seite entsteht nicht von Hand, sondern aus `startseite_daten.py` mit dem Generator `scripts/startseite_build.py`. Die Arbeit besteht fast nur darin, die Datendatei richtig zu füllen. Den Rest erledigt der Generator, und er prüft dabei mehr, als man von Hand prüfen würde.

## Grundsätze

Diese Punkte hat der Nutzer ausdrücklich festgelegt. Sie sind der Grund, warum die Seite so gebaut ist:

- **Offline und überall gleich:** Die Schriften Archivo und Inter werden aus der Grafik eingebettet. Es gibt keinen externen Abruf, kein CDN und kein Google Fonts. Die Seite muss ohne Netz auf jedem Gerät gleich aussehen.
- **Kein JavaScript, keine Speicherung:** Sprache (Radio DE/EN), Farbschema (Checkbox, hell ist Standard) und Einblender (`:target`) laufen rein über CSS.
- **Belegt statt formuliert:** Jede Zahl und jede Aussage stammt wörtlich aus einer Grafik. Die Startseite ist Schaufenster, keine eigene Quelle. Abweichungen werden gemeldet, nicht still geglättet.
- **Deutsche Formate:**
  - Standarddeutsch mit Datumsformat 25.09.2026.
  - „und“ statt „&“.
  - Das Wort „Register“ kommt nicht vor.
  - Keine KI-Floskeln.

## Ablauf

### 1. Arbeitsordner einrichten

In einen Ordner gehören:
- die aktuellen Grafiken (`name_JJJJ-MM-TT.html`),
- `startseite_daten.py`,
- falls vorhanden die bisherige `denkfilter-startseite.html`.

Gibt es noch keine Datendatei, `assets/startseite_daten.py` aus dem Skill kopieren. Sie enthält den Stand vom 25.09.2026 als vollständiges Beispiel mit Impressum, Datenschutz und Methodik.

Den Generator nicht in den Arbeitsordner kopieren, sondern aus dem Skill aufrufen:

```bash
python3 <skill>/scripts/startseite_build.py <arbeitsordner>
```

### 2. Grafiken vollständig lesen

Jede Grafik ist rund 300 kB groß, davon rund 188 kB Base64-Schriften. Zum Lesen:

```bash
python3 <skill>/scripts/grafik_lesen.py <grafik.html>          # Kernfelder und Volltext
python3 <skill>/scripts/grafik_lesen.py <grafik.html> --kurz   # nur Kernfelder
```

Die Kernfelder sind Titel, Kopfzeile (Recherchestand), Leitfrage, die drei TL;DR-Zellen und der Fassungsvergleich. Den Volltext trotzdem lesen, denn Belege für die Tafel stehen oft auf den Bühnen (Kennzahlen, Verteilungen, Muster).

### 3. Datendatei nachziehen

Das Format steht in `references/datenformat.md`. Bei jedem Lauf zu tun:

1. **`datei`** auf den neuen Dateinamen setzen. Stand und Bezugsdatum („gegenüber …“) liest der Generator selbst aus der Grafik; nicht von Hand eintragen.
2. **`leitfrage`** mit der Grafik abgleichen und bei Änderung wörtlich übernehmen.
3. **`kurztexte`**:
   - DE wörtlich aus den TL;DR-Zellen übernehmen.
   - Kürzen ist erlaubt, aber nur durch Weglassen ganzer Sätze oder ganzer Glieder zwischen Semikolons, nie durch Umformulieren. Umformulieren erzeugt genau die Abweichungen, die im Erstlauf gefunden wurden: „Bedrohungsframing“ statt „Bedrohungsbild“, „tragfähige Quelle“ statt der genauen Aufnahmeregel.
   - Wenn die bisherigen Startseiten-Texte bewusst anders formuliert sind, nicht überschreiben, sondern den Nutzer fragen oder die Abweichung melden.
4. **`kasten`** (Fassungsvergleich): Zeilen „Hinzugekommen“, „Präziser geworden“, „Unverändert trotz Bewegung“ wörtlich aus der Grafik übernehmen, mit derselben Kürzungsregel.
5. **Englisch:**
   - EN-Texte sind Übersetzungen der DE-Texte, nah am Wortlaut.
   - Die Grafiken sind nur deutsch. EN lässt sich daher nicht gegen sie belegen; im Protokoll als Übersetzung kennzeichnen.
   - Englische Daten im Format „25 Sep 2026“.
6. **`tafel`**:
   - Die Kennzahl für die Tafel aus der Grafik wählen. Geeignet ist die Zahl, die den Kern des Falls am knappsten zeigt, z. B. ein Abstand und dessen Veränderung oder eine Zählung nach Gruppen.
   - Werte eintragen und in `belege` die Sätze der Grafik wörtlich hinterlegen, in denen die Zahlen stehen.
   - Beschriftungen so genau wie der Beleg. Gilt eine Null nur für eine Teilmenge, sagt die Beschriftung das.
7. **Einblender** (Impressum, Datenschutz, Methodik) sind Texte des Nutzers und bleiben unangetastet, außer er liefert neue.

### 4. Bauen

```bash
python3 <skill>/scripts/startseite_build.py <arbeitsordner>
```

Der Generator bricht mit `FEHLER:` ab, wenn:
- Dateiname, Titel und Kopfzeile einer Grafik unterschiedliche Daten tragen,
- ein Tafel-Beleg nicht wörtlich in der Grafik steht oder eine Tafel-Zahl in keinem Beleg,
- externe Abrufe, `<script>`, Storage, Cookies, „Register“ oder „ & “ im Ergebnis stehen,
- ein Link auf eine fehlende Datei oder einen fehlenden Anker zeigt,
- ein Zeichen außerhalb der eingebetteten Schriften liegt (z. B. ☀ ↗ →; stattdessen Inline-SVG oder ein Zeichen aus dem Latin-Umfang).

Bei einem Fehler die Daten korrigieren, nie die Prüfung lockern. Die Prüfungen sind die Zusicherungen, die der Nutzer verlangt hat.

Ein `HINWEIS:` (z. B. „im Ordner liegt eine neuere Fassung“) ist kein Abbruch, gehört aber in die Antwort.

### 5. Render-Prüfung

Wenn Node mit Playwright verfügbar ist:

```bash
node <skill>/scripts/render_pruefung.js <arbeitsordner>/denkfilter-startseite.html [screenshot-ordner]
```

Das Skript prüft sieben Breiten (1600 bis 320 px): Überlauf, Schriften, Lauftext mobil mindestens 16 px, Touchziele mindestens 24 px und externe Abrufe. Dazu testet es Sprach- und Schemawechsel per Klick, den Tastaturfokus und alle Einblender. Findet es ein Problem, endet es mit Exit-Code 1.

Danach mindestens den Screenshot bei 390 px und den dunklen bei 1366 px ansehen: Eine neue Tafel kann technisch sauber und trotzdem schief sein, etwa wenn ein langes Label an die Kante läuft.

Ohne Playwright: `npm i playwright` in einem Hilfsordner und `NODE_PATH` setzen. Wenn ein Chromium schon installiert ist, `playwright install` nicht ausführen. Ist die Prüfung gar nicht möglich, das in der Antwort sagen, statt sie zu übergehen.

### 6. Antwort an den Nutzer

Kurz und in dieser Reihenfolge:
1. Was ist neu: Stand je Grafik, geänderte Texte, neue Tafelwerte.
2. Prüfergebnis: Generator, Render-Prüfung mit Breiten, Dateigröße.
3. Abweichungen zwischen Startseite und Grafiken, die bewusst stehen blieben oder dem Nutzer auffallen sollten, jeweils mit beiden Wortlauten.
4. Nächster Schritt, falls etwas offen ist.

Alle Datumsangaben deutsch. Keine Floskeln.

## Wenn die Startseite noch nicht existiert oder sich stark ändert

- **Neue Grafik (dritter Fall):** Eintrag in `GRAFIKEN` ergänzen. Anker, Nummer und Index vergeben, eine Tafel wählen.
- **Tafel-Typ fehlt:** Passt keiner der beiden Typen (`abstand`, `kacheln`), im Generator eine neue Funktion `tafel_<typ>` nach dem Muster der vorhandenen schreiben und in `TAFELN` eintragen. Dabei gelten:
  - viewBox 760 × 900,
  - Schrift mindestens 28 Einheiten,
  - Farben aus den Konstanten `T_*`,
  - wesentliche Inhalte zwischen y = 60 und y = 790 (darunter liegt die Bildunterschrift).

  Die Prüfung „Zahl in Beleg“ in `visual()` für den neuen Typ ergänzen.
- **Fremde SVGs** (vom Nutzer geliefert) nicht direkt einsetzen. Sie bringen meist einen eigenen Schriftblock, globale CSS-Klassen und externe Links mit. Stattdessen den Inhalt als Tafel nachbauen oder, nur zur Ansicht, eine getrennte Vorschau-Datei erzeugen, die den Schriftblock entfernt und das CSS auf die Wurzelklasse der SVG begrenzt.
