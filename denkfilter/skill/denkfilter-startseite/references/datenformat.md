# Datenformat `startseite_daten.py`

Die Datei ist Python und enthält drei Namen. Texte sind HTML-Fragmente; erlaubt sind `<strong>`, `<b>`, `<em>` und `<a href="mailto:…">`. Zweisprachige Felder sind `{"de": "…", "en": "…"}`.

Platzhalter, die der Generator aus der Grafik füllt:
- `{stand}` / `{stand_en}`: Recherchestand der Grafik (25.09.2026 / 25 Sep 2026)
- `{vergleich}` / `{vergleich_en}`: Datum der Vorfassung aus „Fassungsvergleich · gegenüber der Fassung vom …“

## SEITE

Seitenrahmen, ändert sich selten: `title`, `description`, `kicker`, `hero`, `hero_stand`, `bruecke` (`titel`, `text`), `fuss`, `ui` (feste Beschriftungen).

## GRAFIKEN (Liste, Reihenfolge = Reihenfolge auf der Seite)

| Feld | Bedeutung | Bei jedem Lauf? |
|---|---|---|
| `anker` | HTML-Anker, z. B. `tempo` (auch Fußzeilen-Index) | nein |
| `nr` | Fallnummer auf der Startseite, `"01"` | nein |
| `datei` | Dateiname der Grafik im Arbeitsordner, Muster `name_JJJJ-MM-TT.html` | **ja** |
| `index` | Text im Fußzeilen-Index | nein |
| `label`, `titel`, `unter` | Kopf des Falls | selten |
| `bildunterschrift`, `bildmarke` | Zeile unter der Kennzahl-Tafel | selten |
| `leitfrage` | wörtlich aus der TL;DR-Zeile „Leitfrage:“ | wenn geändert |
| `kurztexte` | drei Abschnitte `{h, de, en, fokus?}`; `de` wörtlich aus den TL;DR-Zellen | **ja, prüfen** |
| `kasten` | `{de: {titel, zusatz, zeilen}, en: …}`; `zeilen` = Liste `(Label, Text)` | **ja** beim Fassungsvergleich |
| `tafel` | Kennzahl-Tafel, siehe unten | **ja** |
| `lesezeit` | Zeile neben dem Link | nein |

Beim Fall mit Fassungsvergleich ist `zusatz` = `"gegenüber {vergleich}"`. Beim Fall ohne Fassungsvergleich (z. B. Vorfälle) enthält der Kasten die Fortschreibungsregeln; `zusatz` ist fester Text.

## tafel

Gemeinsam: `typ`, `titel` (zweisprachig, Großbuchstaben), `belege` (Liste wörtlicher Sätze aus der Grafik).

Der Generator bricht ab, wenn
- ein Beleg nicht wörtlich (bei normalisierten Leerzeichen) im sichtbaren Text der Grafik steht,
- eine Zahl der Tafel in keinem Beleg vorkommt.

### typ "abstand"

Für einen Abstand zwischen zwei Werten und dessen Entwicklung.

```python
"tafel": {
    "typ": "abstand",
    "titel": {"de": "LEISTUNGSABSTAND IM INDEX", "en": "PERFORMANCE GAP IN THE INDEX"},
    "einheit": {"de": "PUNKTE", "en": "POINTS"},
    "erklaerung": {"de": ["zwischen US-Spitze", "und China-Spitze"],
                   "en": ["between the U.S. leader", "and China’s best"]},
    "links": ["GLM-5.3", 45],          # kleinerer Wert, türkiser Ring
    "rechts": ["Opus 5.5", 58],        # größerer Wert, weißer Punkt
    "achse": [40, 60, 5],              # von, bis, Schritt; beide Werte müssen hineinpassen
    "verlauf": [["17.09.", 8], ["25.09.", 13]],  # letzter Eintrag = große Zahl oben
    "fuss": {"de": "Abstand in Indexpunkten", "en": "Gap in index points"},
    "belege": ["Opus 5.5 erreicht 58 Punkte, GLM-5.3 45",
               "ein Abstand von 13 bzw. 14 Punkten (am 17.09.: 8)"],
}
```

Gezeigt werden die letzten zwei Einträge von `verlauf`. Beim neuen Lauf wird der bisher letzte Eintrag zum vorletzten: `[["25.09.", 13], ["02.10.", 11]]`.

### typ "kacheln"

Für eine Zählung von Fällen in Gruppen, höchstens 16 Kacheln (4 × 4).

```python
"tafel": {
    "typ": "kacheln",
    "titel": {"de": "16 FÄLLE · 01.06.–25.09.2026", "en": "16 INCIDENTS · 01.06.–25.09.2026"},
    "gruppen": [   # Fallnummern wie auf den Karten der Grafik; art a türkis, b warm, c Umriss
        {"von": 6, "bis": 13, "art": "a", "name": {"de": "Ausbruch aus Tests", "en": "Escape from tests"}},
        {"von": 14, "bis": 17, "art": "b", "name": {"de": "Werkzeug und Waffe", "en": "Tool and weapon"}},
        {"von": 18, "bis": 21, "art": "c", "name": {"de": "Fehlurteil, Klage, Ausfall, Sperre", "en": "…"}},
    ],
    "leer": {"wert": "0", "de": ["Ausbrüche", "aus dem", "Betrieb"], "en": ["escapes", "from", "production"]},
    "belege": ["16 Fälle, bekannt geworden 01.06.–25.09.2026",
               "Ausbruch aus Tests 8 · Werkzeug und Waffe 4 · Fehlurteil, Klage, Ausfall, Sperre 4",
               "Alle acht Ausbrüche stammen aus Evaluationen; kein Fall aus dem Produktivbetrieb."],
}
```

`leer` ist ein gestricheltes Feld neben den Kacheln für eine belegte Null oder eine andere Einzelzahl; mit `None` entfällt es. Die Beschriftung muss genau sagen, worauf sich die Zahl bezieht. Im Beispiel gilt die Null nur für Ausbrüche, nicht für alle Fälle.

Mehr als 16 Fälle passen nicht in die Kachel-Tafel. Dann `typ "abstand"` nutzen oder die Gruppen zusammenfassen und den Nutzer fragen.

## EINBLENDER und EINBLENDER_UI

Impressum, Datenschutz und Methodik als Liste `{id, link, de, en}`. Das sind Texte des Nutzers: wörtlich übernehmen, nie redigieren. Fehlt eine englische Fassung, `"en": None` setzen; die Seite zeigt dann den deutschen Text mit dem Hinweis aus `EINBLENDER_UI["nur_deutsch"]`.
