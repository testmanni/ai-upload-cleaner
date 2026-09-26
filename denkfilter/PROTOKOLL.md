# Protokoll: DENKFILTER-Startseite (26.09.2026)

Ergebnis: `denkfilter-startseite.html` (223.612 Byte, davon rund 188 kB Schriftblock), erzeugt von `startseite_build.py` aus `startseite_daten.py`. Die Vorlage `denkfilter-startseite-local-safe.html` ist unverändert (MD5 identisch mit dem Upload).

## Was geändert wurde

- **Schriften:** Der Block `<style id="schriften">` wird unverändert aus der Tempo-Grafik übernommen; in beiden Grafiken ist er identisch. Archivo steht für H1, Fall-Titel, Ziffern, Leitfragen, Brücke und die Fußzeilen-Marke, auch im SVG-Text. Inter setzt den Lauftext. Es gibt keinen Systemschrift-Stack mehr, kein Arial Narrow und kein Arial im SVG. Nur noch generisches `sans-serif` greift als letzte Rückfallstufe.
- **Zeichenumfang:** ☀, ◐ und ↗ liegen außerhalb der eingebetteten Teilmenge und wären aus Systemschriften gekommen. Sie sind durch Inline-SVG-Symbole ersetzt.
- **Titel und Kommentare:** Der Titel lautet „DENKFILTER · KI-Lagebild“. „Local-safe“ kommt nirgends mehr vor.
- **Hell als Standard:** Die Checkbox ist nicht vorbelegt. `html` und `body` sind hell; nur bei aktivem Dunkelmodus werden sie per `:has()` dunkel, samt `color-scheme`. Beim Überscrollen erscheint im hellen Modus daher kein dunkler Rand.
- **Scheinbar klickbare Chips:** „DE / EN“ und „Hell / Dunkel“ im Hero sind gestrichen, ebenso der gleichartige Hinweis im Fuß. Die echte Steuerung sitzt in der dauerhaft sichtbaren Kopfleiste. Der Stand-Chip ist als reine Angabe geblieben.
- **Fußzeilen-Index:** Die Einträge sind jetzt Links auf `#tempo` und `#vorfaelle`. Dank `scroll-margin-top` verdeckt die Kopfleiste die Anker nicht.
- **Theme-Umschalter:** Er ist ein Schalter mit Knopf, der zur Sonne bzw. zum Mond wandert, und zeigt dazu den Text „Hell/Dunkel“ bzw. „Light/Dark“. Unter 420 px bleibt nur der Schalter sichtbar.
- **Tastatur:** Die Radios und die Checkbox sind fokussierbar (nicht mehr `pointer-events:none`). Beim Fokus trägt das zugehörige Label einen 3-px-Ring; Links haben ebenfalls einen Fokusring. Sprachwahl mit Pfeiltasten, Farbschema mit Leertaste.
- **Stand und Links aus den Grafiken:** Der Generator liest das Datum aus Dateiname, `<title>` und Kopfzeile („Recherchestand“) und bricht bei Widerspruch ab. Das Bezugsdatum „gegenüber 17.09.2026“ liest er aus dem Fassungsvergleich der Tempo-Grafik. Die Links zeigen genau auf die Dateinamen aus `startseite_daten.py`.
- **Gestaltung:** Dunkelblau `#16294e` und Türkis `#0f9488`/`#096b62` stammen aus den Grafiken, als warmer Akzent dient `#f0b55d`. Die Kurztexte stehen nicht mehr vollständig fett. Beide Visuals sind neu gezeichnet und bleiben abstrakt:
  - 01: Tempo-Kurve gegen eine treppenförmige Regel-Linie.
  - 02: Netz in einer gestrichelten Testumgebung, drei Knoten liegen außerhalb.

  Die Beschriftungen der Visuals sind zweisprachig. Am Desktop ist das Visual sticky; das Seitenverhältnis entspricht der Grafik, sodass nichts beschnitten wird. Mobil steht die Bildunterschrift unter dem Bild. Bewegung entfällt bei `prefers-reduced-motion`.
- **Sprache für Screenreader:** Englische Elemente tragen `lang="en"`.
- **Inhalte:** Alle Texte sind wörtlich übernommen. Die englischen Datumsangaben bleiben wie in der Vorlage im Format „25 Sep 2026“.

## Pflegeweg: Generator

Ich habe mich für `startseite_build.py` mit `startseite_daten.py` entschieden. Gründe:

- Das Stand-Datum muss niemand von Hand eintragen. Es kommt aus der Grafik, und der Abgleich von Dateiname, Titel und Kopfzeile fängt Tippfehler ab.
- Der rund 188 kB große Schriftblock wird bei jedem Lauf frisch aus der Grafik übernommen. Ändern sich die Schriften der Grafiken, zieht die Startseite automatisch nach.
- Die Prüfungen laufen bei jedem Bau mit; bei einem Verstoß bricht der Generator ab. Geprüft wird:
  - kein `http(s)://`, `@import`, Skript, Storage oder Cookie,
  - Linkziele und Anker existieren,
  - kein Zeichen außerhalb der Schriftteilmenge,
  - kein „Register“ und kein „ & “.
- Ein Block am HTML-Anfang hätte in einer 220-kB-Datei mit Base64 gestanden und die Datumsangaben nicht absichern können.

**Ablauf je Lauf:**

1. Neue Grafiken in den Ordner legen.
2. In `startseite_daten.py` je Grafik `datei` anpassen, bei Bedarf auch `kurztexte` und `kasten`.
3. `python3 startseite_build.py` ausführen.

Liegt eine neuere Fassung im Ordner als die eingetragene, gibt der Generator einen Hinweis aus. Er nutzt nur die Standardbibliothek (getestet mit Python 3).

## Prüfungen

Geprüft mit Chromium headless (Playwright). Externe Anfragen waren blockiert und wurden gezählt: 0.

| Breite | Horizontaler Überlauf | Archivo/Inter geladen | Min. Lauftext | Min. Touchziel |
|---|---|---|---|---|
| 1600 | nein | ja/ja | – | 30 px |
| 1366 | nein | ja/ja | – | 30 px |
| 1280 | nein | ja/ja | – | 30 px |
| 1024 | nein | ja/ja | – | 30 px |
| 768 | nein | ja/ja | 16 px | 30 px |
| 390 | nein | ja/ja | 16 px | 30 px |
| 320 | nein | ja/ja | 16 px | 30 px |

- **Abgeschnittene Elemente:** keine gefunden. Geprüft wurde, dass kein sichtbares Element aus dem Viewport ragt und kein Textblock breiter läuft als sein Container.
- **Sprachen und Farbschemata:** Geschaltet per Klick auf die echten Labels bei 1366 px, gerendert in DE hell, EN hell, EN dunkel und DE dunkel. Titel, Schema-Text und `html`-Hintergrund wechseln korrekt. Im hellen Modus ist `html` `rgb(246, 248, 251)`.
- **Tastatur:** Die Tab-Reihenfolge ist Sprachwahl, Farbschema, Wortmarke, beide Grafik-Links, Index-Links. Jedes Element zeigt einen 3-px-Fokusring. Der Anker `#vorfaelle` landet 64 px unter der Oberkante, also direkt unter der Kopfleiste.
- **grep** auf `http://`, `https://`, `//fonts`, `@import`: kein Treffer. Die einzigen `href` sind `#top`, `#tempo`, `#vorfaelle`, `ki-tempo-gegen-ki-risiko_2026-09-25.html` und `ki-vorfaelle_2026-09-25.html`.
- **Linkziele:** Beide Dateien existieren im Ordner (`test -f`).
- **Dateigröße:** 223.612 Byte.

## Abweichungen zwischen Kurztexten und Grafiken (nur gemeldet, nicht korrigiert)

Die Grafiken sind nur deutsch. Die englischen Texte lassen sich daher nur mittelbar prüfen.

**01 KI-Tempo gegen KI-Risiko**

1. **„Worum es geht“, echte Abweichung:** Die Startseite schreibt „China weist das Bedrohungs*framing aus der US-KI-Branche* zurück, *betont* aber eigene KI-Risiken“. In der Grafik steht „China weist das Bedrohungs*bild der US-Labore* zurück, *erkennt* aber eigene KI-Risiken *an*“. Akteur und Verb unterscheiden sich; der EN-Text folgt der Startseite („parts of the U.S. AI industry“, „emphasizing“).
2. **Fassungsvergleich „Präziser geworden“, verkürzt:** In der Grafik stehen zusätzlich Index v4.3.2 statt v4.3, „Kostenvergleich um Opus 5.5 ergänzt; im Diagramm ersetzt Opus 5.5 den Vorgänger Opus 5“, die neuen Termine 09.11.2026 und 10.01.2027 sowie zwei gestrichene Termine. Die Startseite („Kostenvergleich und Diagramm um Opus 5.5 aktualisiert“) ist davon gedeckt.
3. **Fassungsvergleich „Unverändert“, verkürzt:** Es fehlen „(kein neues Gesetz in Kraft)“, „keiner ist beantwortet“ und „Abweichungsbox zum TC260-Rahmen 3.0“. Keine Gegenaussage.
4. **Hinweis zum Stand:** Die Bühne „Sicherheitsregeln: China und USA“ trägt in der Grafik „Stand: 17.09.2026“. Die Startseite nennt den Gesamtstand 25.09.2026 laut Kopfzeile.

**02 KI-Vorfälle seit Sommer 2026**

5. **„16 Fallkomplexe“:** In der Grafik steht „16 belegte Fälle“ (ein Fall bündelt teils mehrere Vorfälle). Das Wort „Fallkomplexe“ kommt dort nicht vor; der Zeitraum „bekannt geworden 01.06.–25.09.2026“ fehlt auf der Startseite.
6. **Wortlaut:** Startseite „reale Firmen, Behörden *oder* Projekte“, Grafik „… *und* Projekte“.
7. **„Der US-Senat verlangt Unterlagen von OpenAI“:** Das ist gedeckt. Die Grafik nennt zusätzlich die Frist 01.10.2026; die Startseite nennt sie nicht, und sie läuft in fünf Tagen ab.
8. **„prüft eine mögliche Meldepflichtverletzung“:** Das TL;DR der Grafik sagt „prüft eine Meldepflichtverletzung“, Fallkarte 8 sagt „prüft, ob der Fall … meldepflichtig war“. Gedeckt.
9. **Aufnahmeregel, unschärfer als die Grafik:** Die Startseite schreibt „eine tragfähige Quelle vorliegt“. Die Grafik verlangt „eine Primärquelle des Verursachers, einer Behörde oder Prüfstelle, ersatzweise zwei unabhängige Leitmedien“ und dass „alle vier Punkte erfüllt sind“.
10. **Kennzeichnung:** Die Startseite sagt, neue und geänderte Fälle würden „in jeder Fassung kenntlich gemacht“. Die Grafik beschreibt dafür den Chip „Neu“ und einen Fassungsvergleich. Die vorliegende Vorfälle-Grafik enthält aber weder einen „Neu“-Chip noch einen Fassungsvergleich (vermutlich Erstfassung); die Aussage ist daran derzeit nicht überprüfbar.
11. **Unterzeile:** Startseite „Was aus Testumgebungen entwich“, Grafik „Was aus *den* Testumgebungen entwich“.

## Nachtrag 26.09.2026: Impressum, Datenschutz, Methodik

- **Quelle:** `denkfilter-methodik-einblender.html`, im Ordner abgelegt. Die Texte wurden per Skript aus dem Objekt `L` der Vorlage übernommen und automatisch auf Wortgleichheit geprüft. Sie stehen in `startseite_daten.py` unter `EINBLENDER`.
- **Ohne JavaScript:** Die Vorlage öffnet die Einblender per Skript. Das widerspricht der Vorgabe „kein JavaScript“. Umgesetzt ist deshalb eine reine CSS-Lösung über `:target`:
  - Die Fußlinks zeigen auf `#impressum`, `#datenschutz` und `#methodik`.
  - Schließen geht über das ×, die Schaltfläche „Schließen“, einen Klick auf den abgedunkelten Hintergrund oder die Zurück-Taste des Browsers.
  - Die Escape-Taste schließt ohne Skript nicht.
  - Solange ein Einblender offen ist, scrollt die Seite dahinter nicht.
- **Sprache:** Die Einblender folgen der DE/EN-Umschaltung. `methodik` hat noch keine englische Fassung. Im EN-Modus erscheint deshalb der deutsche Text mit dem Hinweis „This text is currently available in German only.“
  - Neu formuliert habe ich nur diesen Hinweis sowie die EN-Linktexte „How a DENKFILTER is made“ und „Close“. „Legal Notice“ und „Privacy Policy“ stammen aus der Vorlage.
- **Prüfungen:**
  - Bei 1366, 390 und 320 px lässt sich jeder der drei Einblender öffnen und schließen; es gibt keinen horizontalen Überlauf, das Panel bleibt im Viewport, der Schließen-Knopf misst 44 × 44 px und externe Abrufe gibt es nicht.
  - Die Tab-Taste führt nach dem Öffnen zuerst auf das ×.
  - Die Gesamtprüfung bei allen sieben Breiten zeigt 0 Probleme.
  - Außer den zwei Grafik-Links gibt es als neue Ziele nur `mailto:info@just-support.de` (6×). Das ist kein Abruf; der Generator lässt `mailto:` zu.
- **Dateigröße:** jetzt 244.553 Byte.
- **Inhaltlicher Hinweis:**
  - Die Methodik wiederholt die Aufnahmeregel mit „eine tragfähige Quelle vorliegt“. Die Vorfälle-Grafik ist hier strenger (Primärquelle, ersatzweise zwei unabhängige Leitmedien), siehe Abweichung 9.
  - Das Impressum spricht von „Links zu externen Websites Dritter“. Die Startseite selbst verlinkt nur auf die beiden Grafiken; deren Quellenlinks sind extern.
