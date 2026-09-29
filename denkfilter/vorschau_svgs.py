#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vorschau: Startseite mit den SVGs aus svgs/ statt der eingebauten Visuals.
Die eigentliche denkfilter-startseite.html bleibt unverändert.

    python3 vorschau_svgs.py

Oben (Fall 01) steht denkfilter-04-meldekaskade.svg, unten (Fall 02)
denkfilter-03b-frueh-erkannt-spaet-gestoppt.svg.
"""
import os
import re
import sys

sys.dont_write_bytecode = True
import startseite_build as B

ORDNER = B.ORDNER
TAUSCH = {
    "tempo": "svgs/denkfilter-04-meldekaskade.svg",
    "vorfaelle": "svgs/denkfilter-03b-frueh-erkannt-spaet-gestoppt.svg",
}
ZIEL = os.path.join(ORDNER, "denkfilter-startseite-vorschau-svgs.html")


def scope_css(css, wurzel):
    """Stellt jeder Regel die Wurzelklasse der SVG voran, damit Klassen wie
    .date oder .tag nicht auf die Startseite durchschlagen."""
    aus, i = [], 0
    while i < len(css):
        j = css.find("{", i)
        if j < 0:
            aus.append(css[i:]); break
        sel = css[i:j].strip()
        tiefe, k = 1, j + 1
        while tiefe:
            tiefe += {"{": 1, "}": -1}.get(css[k], 0); k += 1
        rumpf = css[j + 1:k - 1]
        if sel.startswith("@media"):
            aus.append("%s{%s}" % (sel, scope_css(rumpf, wurzel)))
        elif sel.startswith("@") or wurzel in sel:
            aus.append("%s{%s}" % (sel, rumpf))
        else:
            teile = [s.strip() for s in sel.split(",")]
            aus.append("%s{%s}" % (",".join("%s %s" % (wurzel, s) for s in teile), rumpf))
        i = k
    return "\n".join(aus)


def lade(pfad):
    s = open(os.path.join(ORDNER, pfad), encoding="utf-8").read()
    s = re.sub(r"<\?xml[^>]*>\s*", "", s)
    s = re.sub(r'<style id="schriften".*?</style>\s*', "", s, flags=re.S)  # Seite hat die Schriften schon
    wurzel = "." + re.search(r'<svg[^>]*class="([^"]+)"', s).group(1).split()[0]
    def ersetze(m):
        return m.group(1) + scope_css(m.group(2), wurzel) + m.group(3)
    s = re.sub(r'(<style type="text/css"><!\[CDATA\[)(.*?)(\]\]></style>)', ersetze, s, flags=re.S)
    s = re.sub(r'\s(width|height)="\d+"', "", s, count=2)
    return s


B.visual = lambda g: lade(TAUSCH[g["anker"]])
B.ZIEL = ZIEL
# Die SVGs sind vollständige Tafeln mit eigenem Kopf und Fuß: Bildunterschrift
# ausblenden, Seitenverhältnis überall 760:900.
B.CSS += """
/* Vorschau mit Fremd-SVGs */
.visual figcaption{display:none}
.visual{aspect-ratio:760/900!important;height:auto}
.visual svg{height:100%;aspect-ratio:auto}
@media (max-width:1100px){.visual{max-width:640px;width:100%;margin:0 auto}}
"""
# Externe Quellen-Links in den SVGs (<a href="https://...">) sind Links, kein Abruf;
# die Prüfung wird für die Vorschau nur um diese Ausnahme gelockert.
_pruefe = B.pruefe
def pruefe(seite, schriften):
    links = re.findall(r'<a href="(https://[^"]+)"', seite)
    for l in links:
        print("HINWEIS: externer Link in SVG:", l)
    rest = re.sub(r'<a href="https://[^"]+"', '<a href="#fuss"', seite)
    rest = rest.replace('xmlns="http://www.w3.org/2000/svg"', "")
    _pruefe(rest, schriften)
B.pruefe = pruefe

if __name__ == "__main__":
    B.baue()
