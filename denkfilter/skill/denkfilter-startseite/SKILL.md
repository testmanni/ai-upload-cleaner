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

Einige Kurztexte darin weichen bewusst vom Wortlaut der Grafiken ab. Der Nutzer hatte die Startseiten-Texte vorgegeben; der Generator meldet diese Stellen als `HINWEIS`. Sie bleiben, bis der Nutzer sie angleichen lässt oder die zugehörige TL;DR-Zelle sich inhaltlich ändert.

Ältere Fassungen der Grafiken bleiben im Ordner: Sie sind die Datumsadressen früherer Fassungen und die Grundlage für den Vergleich in Schritt 2.

Vor dem Bearbeiten sichern:
- `startseite_daten.py` als `startseite_daten.vorher.py`,
- die bisherige Seite als `denkfilter-startseite.vorher.html`.

Der Generator überschreibt `denkfilter-startseite.html` ohne Rückfrage.

Andere Dateien im Ordner (z. B. Vorlagen für Einblender) nicht anfassen; der Generator liest nur die Datendatei und die dort genannten Grafiken.

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

Was sich seit der letzten Fassung geändert hat, zeigt:

```bash
python3 <skill>/scripts/grafik_lesen.py <neu.html> --vergleich <alt.html> --volltext
```

Die Ausgabe zeigt zuerst die Kernfelder (unverändert oder alt gegen neu), dann die neuen und entfallenen Sätze im Volltext.

**Nur neu datiert:** Hat sich außer Datumsangaben nichts geändert und ist die „jüngste berücksichtigte Quelle“ älter als der Stand der Vorfassung, ist die Grafik nur neu datiert. Trotzdem bauen, weil Stand und Links stimmen sollen. In der Antwort sagen, dass die Grafik keine neuen Inhalte hat.

**Widersprüche innerhalb einer Grafik** (Beispiel: TL;DR nennt 11 Punkte, eine Bühne noch 13; ein Stichtag liegt in der Vergangenheit, aber ohne Ergebnis):
- Nicht selbst auflösen. Die Startseite kann eine fehlerhafte Grafik nicht reparieren.
- Maßgeblich für die Startseite sind TL;DR und Fassungsvergleich, weil sie den Stand der Fassung zusammenfassen.
- Die Tafel nur auf Werte stützen, die in der Grafik mindestens an zwei Stellen übereinstimmen oder im TL;DR stehen.
- Jeden Widerspruch in der Antwort mit Fundstellen nennen und die Korrektur der Grafik mit infografik-update empfehlen.
- Nicht bauen, sondern melden, wenn ein Wert, den die Startseite selbst zeigt (Tafel, Kurztext, Kasten), an einer anderen Stelle derselben Grafik widersprochen wird und sich nicht klären lässt, welcher gilt. Widersprüche an Stellen, die die Startseite nicht übernimmt, nur melden.

### 3. Datendatei nachziehen

Das Format steht in `references/datenformat.md`. Bei jedem Lauf zu tun:

1. **`datei`** auf den neuen Dateinamen setzen. Stand und Bezugsdatum („gegenüber …“) liest der Generator selbst aus der Grafik; nicht von Hand eintragen.
2. **`leitfrage`** mit der Grafik abgleichen und bei Änderung wörtlich übernehmen.
3. **`kurztexte`**: Maßstab ist der Vergleich aus Schritt 2.
   - **TL;DR-Zelle hat sich inhaltlich geändert:** Die Kurztexte wörtlich aus der neuen Zelle übernehmen.
   - **Nur ein Datum hat sich geändert** (z. B. das Enddatum eines Zeitraums): Im bisherigen Text nur dieses Datum austauschen, falls es dort vorkommt; sonst den Text lassen.
   - **TL;DR-Zelle ist unverändert:** Den bisherigen Startseiten-Text stehen lassen, auch wenn er vom Wortlaut abweicht. Das kann eine bewusste Entscheidung des Nutzers sein. Die Abweichung meldet der Generator als `HINWEIS`; sie gehört in die Antwort.
   - **Kein Vergleich möglich**, weil die alte Grafik fehlt: Bestehende Texte lassen, Abweichungen melden, den Nutzer fragen.
   - **Kürzen** ist erlaubt, aber nur durch Weglassen ganzer Sätze oder ganzer Glieder zwischen Semikolons, nie durch Umformulieren. Umformulieren erzeugt genau die Abweichungen, die im Erstlauf gefunden wurden: „Bedrohungsframing“ statt „Bedrohungsbild“, „tragfähige Quelle“ statt der genauen Aufnahmeregel.
   - **Verweise auf Stellen innerhalb der Grafik** („auf Bühne 7“, „siehe unten“) zeigen auf der Startseite ins Leere. Das betroffene Glied oder den Satz weglassen; trägt er darüber hinaus Inhalt, stehen lassen und in der Antwort nennen. Diese Regel in Kurztexten und Kasten einheitlich anwenden.
4. **`kasten`**: Es gibt zwei Arten, für beide gelten die Regeln aus Punkt 3.
   - **Fassungsvergleich:** Die Zeilen „Hinzugekommen“, „Präziser geworden“ und „Unverändert trotz Bewegung“ bei jedem Lauf wörtlich aus der Grafik übernehmen, denn sie ändern sich immer.
   - **Fortschreibungsregeln** (Vorfälle): Nur nachziehen, wenn sich die Regeln in der Grafik geändert haben.
5. **Englisch:**
   - EN-Texte sind Übersetzungen der DE-Texte, eng am Wortlaut. Nur geänderte DE-Stellen neu übersetzen; unveränderte EN-Texte bleiben.
   - Die Grafiken sind nur deutsch. EN lässt sich daher nicht gegen sie belegen; im Protokoll als Übersetzung kennzeichnen.
   - Englische Daten im Format „25 Sep 2026“ bzw. „2 Oct 2026“, ohne führende Null, wie der Generator sie für `{stand_en}` erzeugt.
6. **`tafel`**:
   - Die Kennzahl für die Tafel aus der Grafik wählen. Geeignet ist die Zahl, die den Kern des Falls am knappsten zeigt, z. B. ein Abstand und dessen Veränderung oder eine Zählung nach Gruppen.
   - Werte eintragen und in `belege` die Sätze der Grafik wörtlich hinterlegen, in denen die Zahlen stehen.
   - Beschriftungen so genau wie der Beleg. Gilt eine Null nur für eine Teilmenge, sagt die Beschriftung das.
   - Die Datumsbeschriftungen im `verlauf` folgen aus den Ständen der jeweiligen Fassungen und brauchen keinen eigenen Beleg; die Zahlen daneben schon.
7. **Einblender** (Impressum, Datenschutz, Methodik) sind Texte des Nutzers und bleiben unangetastet, außer er liefert neue.

### 4. Bauen

```bash
python3 <skill>/scripts/startseite_build.py <arbeitsordner>
```

Der Generator bricht mit `FEHLER:` ab, wenn:
- Dateiname, Titel und Kopfzeile einer Grafik unterschiedliche Daten tragen,
- das Datum der Vorfassung im Fassungsvergleich nicht vor dem Stand liegt (ein Fehler in der Grafik),
- ein Tafel-Beleg nicht wörtlich in der Grafik steht oder eine Tafel-Zahl in keinem Beleg,
- externe Abrufe, `<script>`, Storage, Cookies, „Register“ oder „ & “ im Ergebnis stehen,
- ein Link auf eine fehlende Datei oder einen fehlenden Anker zeigt,
- ein Zeichen außerhalb der eingebetteten Schriften liegt (z. B. ☀ ↗ →; stattdessen Inline-SVG oder ein Zeichen aus dem Latin-Umfang).

Bei einem Fehler die Daten korrigieren, nie die Prüfung lockern. Die Prüfungen sind die Zusicherungen, die der Nutzer verlangt hat.

Ein `HINWEIS:` ist kein Abbruch, gehört aber in die Antwort. Die wichtigsten Arten:
- **„im Ordner liegt eine neuere Fassung“:** Möglicherweise wurde `datei` vergessen.
- **„nicht wörtlich in der Grafik“:** Ein Satz oder Glied der deutschen Leitfrage, Kurztexte oder Kastenzeilen steht so nicht in der Grafik. Jede dieser Stellen ist entweder bewusst so (siehe Punkt 3) oder ein Fehler, den du korrigierst.

### 5. Render-Prüfung

Wenn Node mit Playwright verfügbar ist:

```bash
node <skill>/scripts/render_pruefung.js <arbeitsordner>/denkfilter-startseite.html [screenshot-ordner]
```

Das Skript prüft sieben Breiten (1600 bis 320 px): Überlauf, Schriften, Lauftext mobil mindestens 16 px, Touchziele mindestens 24 px und externe Abrufe. Dazu testet es Sprach- und Schemawechsel per Klick, den Tastaturfokus und alle Einblender. Findet es ein Problem, endet es mit Exit-Code 1.

Danach die Nahaufnahmen `tafel-<n>-390.png` und `tafel-<n>-1366.png` sowie `de-dunkel-1366.png` ansehen. Eine neue Tafel kann technisch sauber und trotzdem schief sein, etwa wenn ein langes Label an die Kante läuft. Die ganzseitigen Screenshots sind zum Beurteilen der Tafeln zu klein.

Ohne Playwright: `npm i playwright` in einem Hilfsordner und `NODE_PATH` setzen. Wenn ein Chromium schon installiert ist, `playwright install` nicht ausführen. Ist die Prüfung gar nicht möglich, das in der Antwort sagen, statt sie zu übergehen.

### 6. Antwort an den Nutzer

Kurz und in dieser Reihenfolge:
1. Was ist neu: Stand je Grafik, geänderte Texte, neue Tafelwerte.
2. Prüfergebnis: Generator, Render-Prüfung mit Breiten, Dateigröße.
3. Abweichungen zwischen Startseite und Grafiken (die `HINWEIS`-Zeilen), jeweils mit beiden Wortlauten und ob sie bewusst stehen blieben. Außerdem Widersprüche innerhalb der Grafiken.
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
