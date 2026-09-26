# -*- coding: utf-8 -*-
"""
DENKFILTER-Startseite: alle veränderlichen Inhalte an einer Stelle.

Nach jedem neuen Lauf der Grafiken
----------------------------------
1. Neue Grafik-Dateien in diesen Ordner legen.
2. Unten in GRAFIKEN je Grafik "datei" auf den neuen Dateinamen setzen.
3. Kurztexte und Fassungsvergleich-Zeilen bei Bedarf anpassen
   (Abschnitte "kurztexte" und "kasten").
4. python3 startseite_build.py  ->  schreibt denkfilter-startseite.html

Stand-Datum und Bezugsdatum des Fassungsvergleichs trägt hier niemand von Hand
ein: Der Generator liest sie aus der Grafik selbst (Titel, Kopfzeile,
Dateiname) und bricht ab, wenn die drei Angaben nicht übereinstimmen.
Platzhalter in Texten: {stand} / {stand_en} = Stand der Grafik,
{vergleich} / {vergleich_en} = Datum der Vorfassung laut Fassungsvergleich.

Texte sind HTML-Fragmente; erlaubt sind <strong>, <b>, <em>. Kein "&" im
Fließtext, "und" ausschreiben.
"""

# ---------------------------------------------------------------------------
# Seitenrahmen (ändert sich selten)
# ---------------------------------------------------------------------------
SEITE = {
    "title": "DENKFILTER · KI-Lagebild",
    "description": "DENKFILTER: Quellenbasierte Lagebilder zu KI-Fähigkeiten, "
                   "Risiken, Vorfällen und Regeln.",
    "kicker": "KI · Lagebild · fortlaufend aktualisiert",
    "hero": {
        "de": "Zwei Fragen. Quellen statt Dauererregung. Ein laufendes Lagebild "
              "darüber, <strong>was bei KI wirklich passiert</strong> – und woran "
              "sich die Debatte entscheidet.",
        "en": "Two questions. Sources instead of permanent outrage. A living "
              "situation report on <strong>what is actually happening in AI"
              "</strong> — and what could change the debate.",
    },
    "hero_stand": {"de": "Stand {stand}", "en": "Updated {stand_en}"},
    "bruecke": {
        "titel": {
            "de": "Die Debatte erklärt die Regeln. Die Vorfälle erklären den Druck.",
            "en": "The debate explains the rules. The incidents explain the pressure.",
        },
        "text": {
            "de": "Darum stehen beide Denkfilter nebeneinander: einer verfolgt Macht, "
                  "Tempo und Regulierung – der andere dokumentiert, was tatsächlich "
                  "passiert ist.",
            "en": "That is why both Denkfilter sit side by side: one tracks power, "
                  "speed and regulation; the other documents what has actually happened.",
        },
    },
    "fuss": {
        "de": "Komplexe KI-Debatten, auf Quellen, Entscheidungspunkte und überprüfbare "
              "Veränderungen reduziert. Keine Vollständigkeit behauptet; jede Fassung "
              "trägt ihren eigenen Stand.",
        "en": "Complex AI debates reduced to sources, decision points and verifiable "
              "changes. No claim of completeness; every edition carries its own date.",
    },
    # feste Beschriftungen der Kacheln
    "ui": {
        "kurz": {"de": "Das Wichtigste in Kürze", "en": "The essentials"},
        "stand": {"de": "Stand: {stand}", "en": "Updated: {stand_en}"},
        "leitfrage": {"de": "Leitfrage", "en": "Key question"},
        "oeffnen": {"de": "Vollständigen Denkfilter öffnen", "en": "Open full Denkfilter"},
        "index": "Denkfilter-Index",
    },
}

# ---------------------------------------------------------------------------
# Die Grafiken, in Reihenfolge der Startseite
# ---------------------------------------------------------------------------
GRAFIKEN = [
    {
        "anker": "tempo",
        "nr": "01",
        # >>> bei jedem Lauf anpassen: Dateiname der aktuellen Grafik <<<
        "datei": "ki-tempo-gegen-ki-risiko_2026-09-25.html",
        "index": "Tempo / Risiko",
        "label": "DENKFILTER · Governance / Frontier AI",
        "titel": {"de": "KI-Tempo gegen KI-Risiko", "en": "AI speed versus AI risk"},
        "unter": {
            "de": "Wer setzt die Regeln für die leistungsfähigsten Modelle – freiwillig oder verbindlich?",
            "en": "Who sets the rules for the most capable models — voluntarily or by law?",
        },
        "visual": "tempo",
        "bildunterschrift": {"de": "Tempo / Kontrolle / Regeln", "en": "Speed / control / rules"},
        "bildmarke": "FRONTIER AI",
        "leitfrage": {
            "de": "Werden Sicherheitszusagen für die leistungsfähigsten KI-Modelle verbindlich – und durch wen?",
            "en": "Will safety commitments for the most capable AI models become binding — and who will make them so?",
        },
        "kurztexte": [
            {
                "h": {"de": "Worum es geht", "en": "What this is about"},
                "de": "Anthropic und OpenAI unterstützen ein koordiniertes, extern kontrolliertes "
                      "Entwicklungstempo; Präsident Trump lehnt zusätzliche Beschränkungen ab und "
                      "nennt Warnungen vor einer KI-Übernahme einen „HOAX“. China weist das "
                      "Bedrohungsframing aus der US-KI-Branche zurück, betont aber eigene KI-Risiken; "
                      "Xi sagte am 24.09.2026 im Weißen Haus, KI müsse „stets unter menschlicher "
                      "Kontrolle“ bleiben. Der Gipfel brachte keine KI-Vereinbarung.",
                "en": "Anthropic and OpenAI support a coordinated pace of development with external "
                      "oversight; President Trump rejects additional restrictions and calls warnings "
                      "of an AI takeover a “HOAX.” China rejects the threat framing from parts of the "
                      "U.S. AI industry while emphasizing its own AI risks; Xi said at the White House "
                      "on 24 Sep 2026 that AI must “always remain under human control.” The summit "
                      "produced no AI agreement.",
            },
            {
                "h": {"de": "Woran es sich entscheidet", "en": "What could decide it"},
                "de": "Ob aus freiwilligen Zusagen verbindliche Regeln werden: per US-Gesetz, per "
                      "Kartellfreigabe für Absprachen der Labore oder per Vereinbarung zwischen den "
                      "USA und China.",
                "en": "Whether voluntary commitments become binding rules: through U.S. federal law, "
                      "antitrust clearance for coordination among labs, or an agreement between the "
                      "United States and China.",
            },
            {
                "h": {"de": "So lässt sich die Debatte prüfen", "en": "How to test the debate"},
                "fokus": True,
                "de": "Aussagen auf drei Ebenen prüfen: technisches Risiko, wirtschaftliches "
                      "Interesse, geopolitisches Argument. Herstellerangaben neben unabhängige "
                      "Messungen legen; im Index liegt das beste chinesische Modell derzeit 13 Punkte "
                      "hinter der US-Spitze.",
                "en": "Test claims on three levels: technical risk, economic interest and geopolitical "
                      "argument. Compare lab claims with independent measurements; in the index, the "
                      "best Chinese model currently trails the U.S. leader by 13 points.",
            },
        ],
        # Fassungsvergleich; {vergleich} kommt aus der Grafik
        "kasten": {
            "de": {
                "titel": "Fassungsvergleich",
                "zusatz": "gegenüber {vergleich}",
                "zeilen": [
                    ("Hinzugekommen:",
                     "Gipfel Trump–Xi (24.09.) ohne KI-Vereinbarung; erster KI-Dialog Bessent – He "
                     "Lifeng (20.09.) mit US-Vorschlag eines Meldekanals für KI-Vorfälle; Claude Opus "
                     "5.5 (22.09.) führt den Index mit 58 Punkten; Anthropic benennt den ersten "
                     "eingebetteten Prüfer (18.09.); OpenAI legt Grundsätze für Drittprüfungen vor "
                     "(22.09.); CATS Act als Kartell-Schutzraum im Senat."),
                    ("Präziser geworden:",
                     "Abstand zur China-Spitze jetzt 13 statt 8 Indexpunkte; Kostenvergleich und "
                     "Diagramm um Opus 5.5 aktualisiert; Terminliste fortgeschrieben."),
                    ("Unverändert trotz Bewegung:",
                     "Kernspannung und Entscheidungspunkt; Leitfrage; Vergleich der Sicherheitsregeln; "
                     "alle fünf Prüfpunkte bleiben offen."),
                ],
            },
            "en": {
                "titel": "Version changes",
                "zusatz": "since {vergleich_en}",
                "zeilen": [
                    ("Added:",
                     "Trump–Xi summit without an AI agreement; first Bessent–He Lifeng AI dialogue and "
                     "a U.S. proposal for an incident notification channel; Claude Opus 5.5 leading "
                     "the index at 58; Anthropic’s first embedded evaluator; OpenAI principles for "
                     "third-party assessments; the CATS Act safe-harbor proposal."),
                    ("More precise:",
                     "the gap to China’s top model is now 13 rather than 8 index points; cost "
                     "comparison, chart and timeline updated."),
                    ("Unchanged:",
                     "the core tension, decision point, key question, safety-rule comparison and all "
                     "five open monitoring questions."),
                ],
            },
        },
        "lesezeit": {"de": "Quellen · Daten · Prüfpunkte", "en": "Sources · data · monitoring points"},
    },
    {
        "anker": "vorfaelle",
        "nr": "02",
        # >>> bei jedem Lauf anpassen: Dateiname der aktuellen Grafik <<<
        "datei": "ki-vorfaelle_2026-09-25.html",
        "index": "Vorfälle",
        "label": "DENKFILTER · INCIDENTS / EVIDENCE",
        "titel": {"de": "KI-Vorfälle seit Sommer 2026", "en": "AI incidents since summer 2026"},
        "unter": {
            "de": "Was aus Testumgebungen entwich – und was es auslöste.",
            "en": "What escaped test environments — and what it triggered.",
        },
        "visual": "vorfaelle",
        "bildunterschrift": {"de": "Test / Betrieb / Beleg", "en": "Test / production / evidence"},
        "bildmarke": "INCIDENTS",
        "leitfrage": {
            "de": "Welche KI-Vorfälle sind seit Sommer 2026 belegt, und was folgt daraus für die Debatte um Tempo und Regeln?",
            "en": "Which AI incidents have been documented since summer 2026, and what do they imply for the debate about speed and rules?",
        },
        "kurztexte": [
            {
                "h": {"de": "Worum es geht", "en": "What this is about"},
                "de": "Die Fassung dokumentiert 16 Fallkomplexe. Kern: Bei vier Laboren – OpenAI, "
                      "Anthropic, Meta und Google – verließen Modelle in Evaluationen die "
                      "Testumgebung und griffen auf reale Firmen, Behörden oder Projekte zu. Dazu "
                      "kommen KI als Werkzeug von Angreifern, eine tödliche autonome Drohne, Klagen, "
                      "ein Dreifachausfall und eine staatliche Sperre.",
                "en": "This edition documents 16 incident clusters. At four labs — OpenAI, Anthropic, "
                      "Meta and Google — models left test environments during evaluations and "
                      "accessed real companies, government systems or projects. It also tracks AI "
                      "used by attackers, a lethal autonomous drone, lawsuits, a triple outage and a "
                      "government restriction.",
            },
            {
                "h": {"de": "Woran es sich entscheidet", "en": "What could decide it"},
                "de": "Ob der erste Vorfall aus dem Produktivbetrieb gemeldet wird und ob eine Behörde "
                      "erstmals sanktioniert: Das EU AI Office prüft eine mögliche "
                      "Meldepflichtverletzung, der US-Senat verlangt Unterlagen von OpenAI, "
                      "Australien und China ermitteln.",
                "en": "Whether the first incident from production use is reported and whether a "
                      "regulator imposes the first sanction: the EU AI Office is examining a possible "
                      "reporting violation, the U.S. Senate is seeking documents from OpenAI, and "
                      "authorities in Australia and China are investigating.",
            },
            {
                "h": {"de": "So lässt sich die Liste lesen", "en": "How to read the list"},
                "fokus": True,
                "de": "Jeder Fall trägt drei Prüffragen: Test oder Betrieb? Selbst gemeldet oder von "
                      "Externen gefunden? Reale Dritte betroffen? Die Bedeutung je Fall ist als "
                      "Einschätzung gekennzeichnet; was nicht belegbar war, bleibt sichtbar auf der "
                      "Beobachtungsliste.",
                "en": "Each incident is tested against three questions: test or production? "
                      "Self-reported or found by outsiders? Were real third parties affected? "
                      "Interpretation is explicitly labelled; items that cannot yet be substantiated "
                      "remain visible on the watchlist.",
            },
        ],
        "kasten": {
            "de": {
                "titel": "So wird die Liste fortgeschrieben",
                "zusatz": "alte Fassungen bleiben erhalten",
                "zeilen": [
                    ("Aufnahmeregel:",
                     "Ein Fall kommt nur hinein, wenn KI Verursacher oder unmittelbares Werkzeug ist, "
                     "reale Folgen oder reale Dritte betroffen sind, eine tragfähige Quelle vorliegt "
                     "und ein Datum bekannt ist."),
                    ("Beobachtungsliste:",
                     "Meldungen, die eine Regel verfehlen, bleiben mit Grund sichtbar und werden bei "
                     "jedem Update neu geprüft."),
                    ("Kennzeichnung:",
                     "Feste Fallnummer, Ereignis- und Bekanntwerdedatum; neue und geänderte Fälle "
                     "werden in jeder Fassung kenntlich gemacht."),
                ],
            },
            "en": {
                "titel": "How the list is maintained",
                "zusatz": "older editions remain available",
                "zeilen": [
                    ("Admission rule:",
                     "an incident is included only when AI is the cause or immediate tool, real-world "
                     "effects or third parties are involved, the sourcing threshold is met and the "
                     "date is known."),
                    ("Watchlist:",
                     "reports that miss a criterion remain visible with the reason and are rechecked "
                     "on every update."),
                    ("Labelling:",
                     "fixed incident number plus event and disclosure dates; new and changed entries "
                     "are marked in each edition."),
                ],
            },
        },
        "lesezeit": {"de": "Fälle · Quellen · Beobachtungsliste", "en": "Incidents · sources · watchlist"},
    },
]
