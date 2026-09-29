#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vorschlag: Visuals als Kennzahl-Tafeln statt Dekoration.

    python3 vorschlag_svgs.py  ->  denkfilter-startseite-vorschlag-svgs.html

01 Tempo: Leistungsabstand USA–China im Index (Werte aus der Tempo-Grafik,
   Bühne 2 "Leistungsabstand" und Prüfpunkt 5).
02 Vorfälle: die 16 Fälle nach Fallnummer und Gruppe, dazu das leere Feld
   "aus dem Betrieb" (Werte aus der Vorfälle-Grafik, Bühne 1 und Bühne 7).
Die eigentliche denkfilter-startseite.html bleibt unverändert.
"""
import os
import sys

sys.dont_write_bytecode = True
import startseite_build as B
import startseite_daten as D

# Werte, wörtlich aus den Grafiken vom 25.09.2026
TEMPO = {
    "us": ("Opus 5.5", 58),      # Artificial Analysis v4.3.2
    "cn": ("GLM-5.3", 45),
    "abstand_neu": 13,           # Stand 25.09.2026
    "abstand_alt": 8,            # "am 17.09.: 8"
    "alt_datum": "17.09.",
    "neu_datum": "25.09.",
}
VORFAELLE = {
    # Fallnummern der Karten 6–21 und ihre Gruppe
    "gruppen": [
        (range(6, 14), "test", {"de": "Ausbruch aus Tests", "en": "Escape from tests"}),
        (range(14, 18), "waffe", {"de": "Werkzeug und Waffe", "en": "Tool and weapon"}),
        (range(18, 22), "rest", {"de": "Fehlurteil, Klage, Ausfall, Sperre",
                                 "en": "Misjudgement, lawsuit, outage, block"}),
    ],
}

NAVY, TEXT, MUTED, TEAL, WARM, LINE = "#16294e", "#eef4fb", "#b5c3d8", "#3fcfbe", "#f0b55d", "#3a5176"


def t(x, y, de, en, size, weight=700, fill=TEXT, anchor="start", family="Archivo", extra=""):
    """Zweisprachiger SVG-Text; bei gleichem Wortlaut nur ein Element."""
    a = ('x="%s" y="%s" font-family="%s, sans-serif" font-size="%s" font-weight="%s" fill="%s" '
         'text-anchor="%s"%s' % (x, y, family, size, weight, fill, anchor, extra))
    if de == en:
        return '<text %s>%s</text>' % (a, de)
    return '<text %s data-lang="de">%s</text><text %s data-lang="en">%s</text>' % (a, de, a, en)


def rahmen(inhalt):
    return ('<svg viewBox="0 0 760 900" preserveAspectRatio="xMidYMid meet" role="img" aria-hidden="true" focusable="false">'
            '<defs><linearGradient id="vb-%d" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#18305a"/>'
            '<stop offset="1" stop-color="#0f2040"/></linearGradient></defs>'
            '<rect width="760" height="900" fill="url(#vb-%d)"/>%s</svg>' % (id(inhalt), id(inhalt), inhalt))


def svg_tempo_kennzahl():
    d = TEMPO
    x0, x1, lo, hi = 90, 670, 40, 60
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    cx, ux = X(d["cn"][1]), X(d["us"][1])
    s = []
    s.append(t(80, 96, "LEISTUNGSABSTAND IM INDEX", "PERFORMANCE GAP IN THE INDEX", 28, 800, TEAL,
               extra=' letter-spacing="3"', family="Inter"))
    s.append(t(72, 262, str(d["abstand_neu"]), str(d["abstand_neu"]), 190, 900, TEXT, extra=' letter-spacing="-8"'))
    s.append(t(330, 196, "PUNKTE", "POINTS", 52, 900, TEXT, extra=' letter-spacing="-1"'))
    s.append(t(330, 246, "zwischen US-Spitze", "between the U.S. leader", 30, 500, MUTED, family="Inter"))
    s.append(t(330, 284, "und China-Spitze", "and China’s best", 30, 500, MUTED, family="Inter"))
    # Hantel: Stand heute mit Werten
    y = 440
    s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>' % (x0, y, x1, y, LINE))
    for v in range(lo, hi + 1, 5):
        s.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="%s" stroke-width="2"/>' % (X(v), y - 8, X(v), y + 8, LINE))
        s.append(t("%.0f" % X(v), y + 46, str(v), str(v), 28, 600, MUTED, "middle", "Inter"))
    s.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="%s" stroke-width="10" stroke-linecap="round"/>'
             % (cx, y, ux, y, WARM))
    s.append('<circle cx="%.0f" cy="%d" r="17" fill="%s" stroke="%s" stroke-width="5"/>' % (cx, y, NAVY, TEAL))
    s.append('<circle cx="%.0f" cy="%d" r="17" fill="%s"/>' % (ux, y, TEXT))
    s.append(t("%.0f" % cx, y - 40, "%s · %d" % d["cn"], "%s · %d" % d["cn"], 30, 800, TEAL, "middle"))
    s.append(t("%.0f" % ux, y - 40, "%s · %d" % d["us"], "%s · %d" % d["us"], 30, 800, TEXT, "end"))
    # Verlauf des Abstands: zwei Balken im selben Maßstab
    k = (x1 - x0) / (hi - lo)
    for i, (dat, wert, farbe) in enumerate([(d["alt_datum"], d["abstand_alt"], LINE), (d["neu_datum"], d["abstand_neu"], WARM)]):
        yy = 590 + i * 74
        s.append(t(x0, yy + 30, dat, dat, 30, 800, MUTED if i == 0 else TEXT, family="Archivo"))
        s.append('<rect x="200" y="%d" width="%.0f" height="40" rx="6" fill="%s"/>' % (yy, wert * k, farbe))
        s.append(t("%.0f" % (212 + wert * k), yy + 31, str(wert), str(wert), 32, 900, MUTED if i == 0 else WARM))
    s.append(t(x0, 758, "Abstand in Indexpunkten", "Gap in index points", 28, 500, MUTED, family="Inter"))
    return rahmen("".join(s))


def svg_vorfaelle_kennzahl():
    s = []
    s.append(t(80, 96, "16 FÄLLE · 01.06.–25.09.2026", "16 INCIDENTS · 01.06.–25.09.2026", 28, 800, TEAL,
               extra=' letter-spacing="2"', family="Inter"))
    kachel, luecke, gx, gy = 100, 14, 80, 136
    stil = {"test": ('fill="%s"' % TEAL, NAVY), "waffe": ('fill="%s"' % WARM, NAVY),
            "rest": ('fill="none" stroke="%s" stroke-width="3"' % MUTED, TEXT)}
    i = 0
    for nummern, art, _ in VORFAELLE["gruppen"]:
        for n in nummern:
            x, y = gx + (i % 4) * (kachel + luecke), gy + (i // 4) * (kachel + luecke)
            f, schrift = stil[art]
            s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="14" %s/>' % (x, y, kachel, kachel, f))
            s.append(t(x + kachel / 2, y + 62, "%02d" % n, "%02d" % n, 34, 800, schrift, "middle"))
            i += 1
    # das leere Feld: "Alle acht Ausbrüche stammen aus Evaluationen; kein Fall aus dem Produktivbetrieb." (Bühne 7)
    ex = gx + 4 * (kachel + luecke) + 30
    s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="10 8"/>'
             % (ex, gy, kachel + 34, kachel + 34, WARM))
    s.append(t(ex + (kachel + 34) / 2, gy + 90, "0", "0", 72, 900, WARM, "middle"))
    s.append(t(ex, gy + 182, "Ausbrüche", "escapes", 28, 700, TEXT, family="Inter"))
    s.append(t(ex, gy + 218, "aus dem", "from", 28, 700, TEXT, family="Inter"))
    s.append(t(ex, gy + 254, "Betrieb", "production", 28, 700, TEXT, family="Inter"))
    # Legende
    y = 640
    for j, (nummern, art, name) in enumerate(VORFAELLE["gruppen"]):
        yy = y + j * 46
        f, _ = stil[art]
        s.append('<rect x="80" y="%d" width="28" height="28" rx="6" %s/>' % (yy, f))
        s.append(t(124, yy + 24, "%d %s" % (len(nummern), name["de"]), "%d %s" % (len(nummern), name["en"]),
                   28, 600, TEXT, family="Inter"))
    return rahmen("".join(s))


ZIEL = os.path.join(B.ORDNER, "denkfilter-startseite-vorschlag-svgs.html")
B.VISUALS = {"tempo": svg_tempo_kennzahl, "vorfaelle": svg_vorfaelle_kennzahl}
B.ZIEL = ZIEL
B.CSS += """
/* Vorschlag: Kennzahl-Tafeln, auf allen Breiten ungeschnitten */
.visual{aspect-ratio:760/900!important;height:auto}
.visual svg{height:100%}
@media (max-width:1100px){.visual{max-width:560px;width:100%;margin:0 auto}}
@media (max-width:800px){.visual{max-width:none;aspect-ratio:auto!important}.visual svg{aspect-ratio:760/900;height:auto}}
"""

if __name__ == "__main__":
    B.baue()
