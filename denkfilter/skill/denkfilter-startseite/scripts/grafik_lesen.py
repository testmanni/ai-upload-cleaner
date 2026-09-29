#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gibt den lesbaren Inhalt einer DENKFILTER-Grafik aus, ohne Base64-Schriften,
CSS und Skript. Damit lässt sich eine 300-kB-Grafik vollständig lesen.

    python3 grafik_lesen.py GRAFIK.html            # Kernfelder und Volltext
    python3 grafik_lesen.py GRAFIK.html --kurz     # nur Kernfelder
    python3 grafik_lesen.py NEU.html --vergleich ALT.html
                                                   # welche Kernfelder sich geändert haben

Kernfelder: Titel, Kopfzeile, TL;DR (Leitfrage und Zellen), Fassungsvergleich.
Nur Standardbibliothek.
"""
import html
import re
import sys


def text(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def abschnitt(quelle, id_):
    m = re.search(r'<section[^>]*id="%s"[^>]*>(.*?)</section>' % id_, quelle, re.S)
    return m.group(1) if m else ""


def kernfelder(quelle):
    felder = {}
    tldr = abschnitt(quelle, "tldr")
    m = re.search(r'class="tldr-topic"[^>]*>(.*?)</p>', tldr, re.S)
    felder["Leitfrage"] = text(m.group(1)) if m else ""
    for h, p in re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", tldr, re.S):
        felder["TL;DR " + text(h)] = text(p)
    regeln = abschnitt(quelle, "regeln")
    for h, p in re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", regeln, re.S):
        felder["Regel " + text(h)] = text(p)
    for zelle in re.findall(r"<div><b>(.*?)</b>(.*?)</div>", abschnitt(quelle, "fassung"), re.S):
        felder["Fassungsvergleich " + text(zelle[0])] = text(zelle[1])
    return felder


def vergleiche(neu, alt):
    a, n = kernfelder(alt), kernfelder(neu)
    for k in sorted(set(a) | set(n)):
        if a.get(k) == n.get(k):
            print("UNVERÄNDERT:", k)
        else:
            print("\nGEÄNDERT: %s\n  alt: %s\n  neu: %s" % (k, a.get(k, "–"), n.get(k, "–")))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    quelle = open(sys.argv[1], encoding="utf-8").read()
    if "--vergleich" in sys.argv:
        alt = open(sys.argv[sys.argv.index("--vergleich") + 1], encoding="utf-8").read()
        vergleiche(quelle, alt)
        return
    ohne = re.sub(r"<(style|script)\b.*?</\1>", " ", quelle, flags=re.S)

    m = re.search(r"<title>(.*?)</title>", quelle, re.S)
    print("TITEL:", text(m.group(1)) if m else "-")
    m = re.search(r'id="kopfzeile"[^>]*>(.*?)</div>', quelle, re.S)
    print("KOPFZEILE:", text(m.group(1)) if m else "-")

    tldr = abschnitt(quelle, "tldr")
    m = re.search(r'class="tldr-topic"[^>]*>(.*?)</p>', tldr, re.S)
    print("\nLEITFRAGE:", text(m.group(1)) if m else "-")
    for h, p in re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", tldr, re.S):
        print("\n[TL;DR] %s\n%s" % (text(h), text(p)))

    fass = abschnitt(quelle, "fassung")
    if fass:
        m = re.search(r"<h2[^>]*>(.*?)</h2>", fass, re.S)
        print("\nFASSUNGSVERGLEICH:", text(m.group(1)) if m else "")
        for zelle in re.findall(r"<div><b>.*?</div>", fass, re.S):
            print("-", text(zelle))
    else:
        print("\nFASSUNGSVERGLEICH: keiner in der Grafik (Erstfassung oder Grafik ohne Fassungsvergleich, "
              "z. B. Vorfälle mit Fortschreibungsregeln)")

    if "--kurz" not in sys.argv:
        print("\n==== VOLLTEXT ====")
        for block in re.split(r"(?=<(?:section|div class=\"stage|h2|h3))", ohne):
            t = text(block)
            if t:
                print(t)


if __name__ == "__main__":
    main()
