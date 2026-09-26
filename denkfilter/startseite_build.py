#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt denkfilter-startseite.html aus startseite_daten.py.

    python3 startseite_build.py

Nur Standardbibliothek. Der Generator
  - übernimmt den Block <style id="schriften"> unverändert aus der ersten Grafik,
  - liest Stand-Datum und Bezugsdatum des Fassungsvergleichs aus jeder Grafik
    (Titel, Kopfzeile, Dateiname) und bricht bei Widerspruch ab,
  - prüft das Ergebnis: keine externen Abrufe, kein Skript, keine Speicherung,
    alle Links zeigen auf vorhandene Dateien oder Anker, alle Zeichen liegen
    im Zeichenumfang der eingebetteten Schriften.
"""
import glob
import html
import os
import re
import sys

sys.dont_write_bytecode = True  # kein __pycache__ neben den Dateien
import startseite_daten as D

ORDNER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(ORDNER, "denkfilter-startseite.html")
MONATE_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fehler(text):
    sys.exit("FEHLER: " + text)


# ---------------------------------------------------------------------------
# Daten aus den Grafiken lesen
# ---------------------------------------------------------------------------
def datum_en(de):
    t, m, j = de.split(".")
    return "%d %s %s" % (int(t), MONATE_EN[int(m) - 1], j)


def lies_grafik(g):
    datei = g["datei"]
    pfad = os.path.join(ORDNER, datei)
    if not os.path.isfile(pfad):
        fehler("Grafik %s nicht gefunden (GRAFIKEN[%s]['datei'])." % (datei, g["anker"]))
    quelle = open(pfad, encoding="utf-8").read()

    m = re.search(r"_(\d{4})-(\d{2})-(\d{2})\.html$", datei)
    if not m:
        fehler("Dateiname %s enthält kein Datum JJJJ-MM-TT." % datei)
    aus_name = "%s.%s.%s" % (m.group(3), m.group(2), m.group(1))
    m = re.search(r"<title>[^<]*Stand (\d\d\.\d\d\.\d{4})\s*</title>", quelle)
    aus_titel = m.group(1) if m else None
    m = re.search(r"Recherchestand:\s*(\d\d\.\d\d\.\d{4})", quelle)
    aus_kopf = m.group(1) if m else None
    if not aus_kopf:
        fehler("%s: keine Kopfzeile mit 'Recherchestand' gefunden." % datei)
    abweichend = {x for x in (aus_name, aus_titel, aus_kopf) if x}
    if len(abweichend) != 1:
        fehler("%s: Datum widersprüchlich (Dateiname %s, Titel %s, Kopfzeile %s)."
               % (datei, aus_name, aus_titel, aus_kopf))

    m = re.search(r"Fassungsvergleich\s*·\s*gegenüber der Fassung vom (\d\d\.\d\d\.\d{4})", quelle)
    vergleich = m.group(1) if m else None

    m = re.search(r'<style id="schriften">.*?</style>', quelle, re.S)
    schriften = m.group(0) if m else None

    # Hinweis, falls im Ordner eine neuere Fassung derselben Grafik liegt
    praefix = re.sub(r"_\d{4}-\d{2}-\d{2}\.html$", "", datei)
    alle = sorted(glob.glob(os.path.join(ORDNER, praefix + "_????-??-??.html")))
    if alle and os.path.basename(alle[-1]) != datei:
        print("HINWEIS: Im Ordner liegt eine neuere Fassung: %s" % os.path.basename(alle[-1]))

    return {"stand": aus_kopf, "stand_en": datum_en(aus_kopf),
            "vergleich": vergleich, "vergleich_en": datum_en(vergleich) if vergleich else None,
            "schriften": schriften}


def fuelle(text, werte):
    def ersetze(m):
        schluessel = m.group(1)
        if werte.get(schluessel) is None:
            fehler("Platzhalter {%s} verwendet, aber nicht aus der Grafik lesbar." % schluessel)
        return werte[schluessel]
    return re.sub(r"\{(\w+)\}", ersetze, text)


# ---------------------------------------------------------------------------
# HTML-Bausteine
# ---------------------------------------------------------------------------
def zwei(obj, werte=None, tag="span", attr=""):
    """Zweisprachiges Element: DE und EN, per CSS umgeschaltet."""
    werte = werte or {}
    return ('<%s data-lang="de"%s>%s</%s><%s data-lang="en" lang="en"%s>%s</%s>'
            % (tag, attr, fuelle(obj["de"], werte), tag,
               tag, attr, fuelle(obj["en"], werte), tag))


PFEIL = ('<svg class="pfeil" viewBox="0 0 20 20" width="18" height="18" aria-hidden="true">'
         '<path d="M6 14L14 6M7.5 6H14v6.5" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')
SONNE = ('<svg class="ico-sonne" viewBox="0 0 20 20" width="14" height="14" aria-hidden="true">'
         '<circle cx="10" cy="10" r="3.6" fill="currentColor"/><path d="M10 1.8v2.4M10 15.8v2.4M1.8 10h2.4'
         'M15.8 10h2.4M4.2 4.2l1.7 1.7M14.1 14.1l1.7 1.7M4.2 15.8l1.7-1.7M14.1 5.9l1.7-1.7" '
         'stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>')
MOND = ('<svg class="ico-mond" viewBox="0 0 20 20" width="14" height="14" aria-hidden="true">'
        '<path d="M15.8 12.6A6.6 6.6 0 0 1 7.4 4.2a6.6 6.6 0 1 0 8.4 8.4z" fill="currentColor"/></svg>')


def svg_tempo():
    # Abstrakt: steil steigende Tempo-Kurve, darunter treppenförmige Regel-Linie,
    # dazwischen die offene Lücke. Wesentliches liegt im Band y 150-760.
    return '''<svg viewBox="0 0 760 900" preserveAspectRatio="xMidYMid slice" role="img" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="t-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16294e"/><stop offset="1" stop-color="#0c1a33"/></linearGradient>
    <linearGradient id="t-gap" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0f9488" stop-opacity="0"/><stop offset="1" stop-color="#0f9488" stop-opacity=".28"/></linearGradient>
  </defs>
  <rect width="760" height="900" fill="url(#t-bg)"/>
  <g stroke="#9fb3d1" stroke-opacity=".13" stroke-width="1">
    <path d="M0 150H760M0 250H760M0 350H760M0 450H760M0 550H760M0 650H760M0 750H760"/>
    <path d="M95 0V900M190 0V900M285 0V900M380 0V900M475 0V900M570 0V900M665 0V900"/>
  </g>
  <circle cx="560" cy="330" r="170" fill="none" stroke="#3fcfbe" stroke-opacity=".5" stroke-width="2" stroke-dasharray="2 12"/>
  <circle cx="560" cy="330" r="100" fill="none" stroke="#dfeaf6" stroke-opacity=".25"/>
  <path d="M70 620C260 610 390 540 480 420S610 230 700 200V560H560V600H420V620Z" fill="url(#t-gap)"/>
  <path d="M70 620C260 610 390 540 480 420S610 230 700 200" fill="none" stroke="#3fcfbe" stroke-width="5" stroke-linecap="round"/>
  <path d="M70 640H280V620H420V600H560V560H700" fill="none" stroke="#f0b55d" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>
  <g fill="#f0b55d"><circle cx="280" cy="620" r="6"/><circle cx="420" cy="600" r="6"/><circle cx="560" cy="560" r="6"/></g>
  <circle cx="700" cy="200" r="9" fill="#3fcfbe"/>
  <circle cx="700" cy="200" r="22" fill="#3fcfbe" fill-opacity=".18"/>
  <path d="M640 240V560" stroke="#dfeaf6" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="4 6"/>
  <g font-family="Archivo, sans-serif" fill="#eef4fb">
    <text x="70" y="300" font-size="96" font-weight="900" letter-spacing="-3" data-lang="de">TEMPO</text>
    <text x="70" y="300" font-size="96" font-weight="900" letter-spacing="-3" data-lang="en">PACE</text>
    <text x="70" y="400" font-size="96" font-weight="900" letter-spacing="-3" fill="none" stroke="#eef4fb" stroke-width="2" data-lang="de">REGELN</text>
    <text x="70" y="400" font-size="96" font-weight="900" letter-spacing="-3" fill="none" stroke="#eef4fb" stroke-width="2" data-lang="en">RULES</text>
    <text x="72" y="444" font-size="17" font-weight="700" letter-spacing="4" fill-opacity=".62" data-lang="de">FRONTIER-MODELLE / KONTROLLE</text>
    <text x="72" y="444" font-size="17" font-weight="700" letter-spacing="4" fill-opacity=".62" data-lang="en">FRONTIER MODELS / CONTROL</text>
  </g>
</svg>'''


def svg_vorfaelle():
    # Abstrakt: Netz in einer gestrichelten Testumgebung; drei Knoten liegen
    # außerhalb, ihre Verbindungen kreuzen die Grenze.
    return '''<svg viewBox="0 0 760 900" preserveAspectRatio="xMidYMid slice" role="img" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="v-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16294e"/><stop offset="1" stop-color="#0b1830"/></linearGradient>
  </defs>
  <rect width="760" height="900" fill="url(#v-bg)"/>
  <g stroke="#9fb3d1" stroke-opacity=".12"><path d="M0 180H760M0 270H760M0 360H760M0 450H760M0 540H760M0 630H760M0 720H760"/><path d="M76 0V900M152 0V900M228 0V900M304 0V900M380 0V900M456 0V900M532 0V900M608 0V900M684 0V900"/></g>
  <rect x="70" y="180" width="420" height="360" rx="26" fill="#0f9488" fill-opacity=".08" stroke="#3fcfbe" stroke-width="2.5" stroke-dasharray="10 9"/>
  <g stroke="#3fcfbe" stroke-width="2" stroke-opacity=".7" fill="none">
    <path d="M150 260L260 330L380 260L420 420L300 480L170 440L150 260"/>
    <path d="M260 330L300 480M260 330L170 440M380 260L300 480" stroke-opacity=".35"/>
  </g>
  <g stroke="#f0b55d" stroke-width="2.5" fill="none" stroke-linecap="round">
    <path d="M380 260C480 210 560 190 640 210"/>
    <path d="M420 420C520 440 590 470 640 520"/>
    <path d="M300 480C320 540 380 590 470 610"/>
  </g>
  <g fill="#0c1a33" stroke="#3fcfbe" stroke-width="3">
    <circle cx="150" cy="260" r="14"/><circle cx="260" cy="330" r="22"/><circle cx="380" cy="260" r="13"/>
    <circle cx="420" cy="420" r="20"/><circle cx="300" cy="480" r="16"/><circle cx="170" cy="440" r="11"/>
  </g>
  <g fill="#0c1a33" stroke="#f0b55d" stroke-width="3">
    <circle cx="640" cy="210" r="18"/><circle cx="640" cy="520" r="24"/><circle cx="470" cy="610" r="15"/>
  </g>
  <g fill="#f0b55d"><circle cx="640" cy="210" r="6"/><circle cx="640" cy="520" r="8"/><circle cx="470" cy="610" r="5"/></g>
  <g font-family="Archivo, sans-serif" font-weight="800" letter-spacing="3" font-size="16">
    <text x="92" y="212" fill="#3fcfbe" data-lang="de">TESTUMGEBUNG</text>
    <text x="92" y="212" fill="#3fcfbe" data-lang="en">TEST ENVIRONMENT</text>
    <text x="444" y="672" fill="#f0b55d" data-lang="de">REALE DRITTE</text>
    <text x="444" y="672" fill="#f0b55d" data-lang="en">REAL THIRD PARTIES</text>
  </g>
  <g font-family="Archivo, sans-serif" fill="#eef4fb">
    <text x="70" y="690" font-size="80" font-weight="900" letter-spacing="-2" data-lang="de">SPUREN</text>
    <text x="70" y="690" font-size="80" font-weight="900" letter-spacing="-2" data-lang="en">TRACE</text>
  </g>
</svg>'''


VISUALS = {"tempo": svg_tempo, "vorfaelle": svg_vorfaelle}


def fall(g, werte):
    kurz = []
    for k in g["kurztexte"]:
        klasse = "abschnitt fokus" if k.get("fokus") else "abschnitt"
        kurz.append('''      <div class="%s">
        <h4>%s</h4>
        %s
      </div>''' % (klasse, zwei(k["h"]), zwei({"de": k["de"], "en": k["en"]}, werte, tag="p")))

    kasten = []
    for sprache in ("de", "en"):
        k = g["kasten"][sprache]
        zeilen = "".join('<li><b>%s</b> %s</li>' % (fuelle(a, werte), fuelle(b, werte))
                         for a, b in k["zeilen"])
        lang = ' lang="en"' if sprache == "en" else ""
        kasten.append('''        <div data-lang="%s"%s>
          <div class="kasten-kopf"><h4>%s</h4><span>%s</span></div>
          <ul>%s</ul>
        </div>''' % (sprache, lang, fuelle(k["titel"], werte), fuelle(k["zusatz"], werte), zeilen))

    ui = D.SEITE["ui"]
    return '''
<!-- Fall %(nr)s · Quelle: %(datei)s -->
<section class="fall" id="%(anker)s" aria-labelledby="%(anker)s-titel">
  <div class="fall-kopf">
    <div class="fall-nr" aria-hidden="true">%(nr)s</div>
    <div>
      <div class="fall-label">%(label)s</div>
      <h2 class="fall-titel" id="%(anker)s-titel">%(titel)s</h2>
      <p class="fall-unter">%(unter)s</p>
    </div>
  </div>
  <div class="fall-raster">
    <figure class="visual">
      %(svg)s
      <figcaption><span><b>%(nr)s</b> · %(bildmarke)s</span>%(bild)s</figcaption>
    </figure>
    <article class="karte">
      <div class="karte-kopf"><h3>%(kurz_titel)s</h3><span class="datum">%(stand)s</span></div>
      <div class="leitfrage">
        <small>%(lf_label)s</small>
        %(leitfrage)s
      </div>
%(kurz)s
      <div class="kasten">
%(kasten)s
      </div>
      <div class="cta">
        <a href="%(datei)s">%(oeffnen)s %(pfeil)s</a>
        <span class="cta-info">%(lesezeit)s</span>
      </div>
    </article>
  </div>
</section>''' % {
        "nr": g["nr"], "datei": html.escape(g["datei"], quote=True), "anker": g["anker"],
        "label": g["label"], "titel": zwei(g["titel"]), "unter": zwei(g["unter"]),
        "svg": VISUALS[g["visual"]](), "bildmarke": g["bildmarke"],
        "bild": zwei(g["bildunterschrift"]), "kurz_titel": zwei(ui["kurz"]),
        "stand": zwei(ui["stand"], werte), "lf_label": zwei(ui["leitfrage"]),
        "leitfrage": zwei(g["leitfrage"], tag="p"), "kurz": "\n".join(kurz),
        "kasten": "\n".join(kasten), "oeffnen": zwei(ui["oeffnen"]), "pfeil": PFEIL,
        "lesezeit": zwei(g["lesezeit"]),
    }


SCHLIESSEN = ('<svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true"><path d="M5 5l10 10M15 5L5 15" '
              'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>')


def einblender(e):
    """Impressum, Datenschutz, Methodik: öffnen über #id (:target), schließen über #fuss.
    Fehlt die englische Fassung, erscheint der deutsche Text mit Hinweis."""
    ui = D.EINBLENDER_UI
    if e["en"]:
        en = '<div class="einblender-text" data-lang="en" lang="en">%s</div>' % e["en"]
    else:
        en = ('<div class="einblender-text" data-lang="en" lang="de"><p class="nur-deutsch" lang="en">%s</p>%s</div>'
              % (ui["nur_deutsch"], e["de"]))
    return '''<section class="einblender" id="%(id)s" aria-label="%(name)s">
  <a class="einblender-hinter" href="#fuss" tabindex="-1" aria-hidden="true"></a>
  <div class="einblender-panel">
    <a class="einblender-zu" href="#fuss">%(x)s<span class="sr">%(zu)s</span></a>
    <div class="einblender-text" data-lang="de">%(de)s</div>
    %(en)s
    <a class="einblender-knopf" href="#fuss">%(zu)s</a>
  </div>
</section>''' % {"id": e["id"], "name": e["link"]["de"], "x": SCHLIESSEN, "de": e["de"], "en": en,
                  "zu": zwei(ui["schliessen"])}


CSS = r'''
/* ==== Farben: Dunkelblau und Türkis aus den Grafiken, warmer Akzent ==== */
:root{
  --navy:#16294e; --navy-soft:#3a4f78; --teal:#0f9488; --teal-dark:#096b62; --teal-tint:#e9f6f3;
  --display:'Archivo',sans-serif; --sans:'Inter',sans-serif;
  --max:1440px; --radius:22px; --gutter:32px;
}
*{box-sizing:border-box}
html{background:#f6f8fb;color-scheme:light;scroll-behavior:smooth;-webkit-text-size-adjust:100%;text-size-adjust:100%}
html:has(#theme-dark:checked){background:#0a1424;color-scheme:dark}
body{margin:0;background:inherit;font-family:var(--sans);font-size:17px;line-height:1.55;
  font-feature-settings:"kern","liga","calt";-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
h1,h2,h3,h4,p,ul,figure{margin:0}
a{color:inherit}
b,strong{font-weight:700}

/* ==== Schaltzustände ohne Skript: Radio (Sprache), Checkbox (Farbschema) ==== */
.ui-toggle{position:fixed;top:0;left:0;width:1px;height:1px;margin:0;opacity:0;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%)}
.site{
  --bg:#f6f8fb; --paper:#ffffff; --ink:#16294e; --muted:#46597f; --line:#c9d2df;
  --accent:#0f9488; --accent-ink:#096b62; --tint:#e9f6f3; --warm:#d98a1c; --focus:#096b62;
  --shadow:0 18px 50px rgba(22,41,78,.10);
  min-height:100vh;background:var(--bg);color:var(--ink);transition:background-color .25s,color .25s;
}
#theme-dark:checked ~ .site{
  --bg:#0a1424; --paper:#0f1e36; --ink:#eef4fb; --muted:#a9b8cd; --line:#26405f;
  --accent:#3fcfbe; --accent-ink:#5fe0d0; --tint:#10303a; --warm:#f0b55d; --focus:#5fe0d0;
  --shadow:0 18px 60px rgba(0,0,0,.35);
}
::selection{background:var(--accent);color:#fff}
.site [data-lang]{display:none!important}
#lang-de:checked ~ .site [data-lang="de"]{display:revert!important}
#lang-en:checked ~ .site [data-lang="en"]{display:revert!important}

/* Fokus: für Tastatur deutlich sichtbar */
a:focus-visible{outline:3px solid var(--focus);outline-offset:3px;border-radius:6px}
#lang-de:focus-visible ~ .site label[for="lang-de"],
#lang-en:focus-visible ~ .site label[for="lang-en"],
#theme-dark:focus-visible ~ .site label[for="theme-dark"]{outline:3px solid var(--focus);outline-offset:3px}

/* ==== Kopfleiste ==== */
.topbar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 86%,transparent);
  -webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}
.topbar-inner{max-width:var(--max);margin:auto;padding:12px var(--gutter);display:flex;align-items:center;justify-content:space-between;gap:14px}
.wortmarke{display:flex;align-items:center;gap:12px;text-decoration:none;font-family:var(--display);font-weight:900;letter-spacing:.06em;font-size:16px;min-height:32px}
.marke{width:30px;height:30px;border:2px solid var(--ink);border-radius:50%;position:relative;flex:0 0 30px}
.marke:before,.marke:after{content:"";position:absolute;left:7px;top:12px;width:12px;height:2.5px;border-radius:2px;background:var(--accent)}
.marke:before{transform:rotate(45deg)}.marke:after{transform:rotate(-45deg)}
.steuerung{display:flex;align-items:center;gap:8px}
.sprachwahl{display:flex;border:1px solid var(--line);border-radius:999px;padding:3px;background:var(--paper)}
.pill{display:inline-flex;align-items:center;justify-content:center;min-height:30px;min-width:38px;padding:0 11px;border-radius:999px;
  cursor:pointer;user-select:none;-webkit-user-select:none;font-size:13px;font-weight:700;letter-spacing:.05em;color:var(--muted);transition:background-color .2s,color .2s}
.pill:hover{color:var(--ink)}
#lang-de:checked ~ .site label[for="lang-de"],
#lang-en:checked ~ .site label[for="lang-en"]{background:var(--ink);color:var(--bg)}
.schema{display:inline-flex;align-items:center;gap:9px;min-height:38px;padding:3px 12px 3px 4px;border:1px solid var(--line);border-radius:999px;
  background:var(--paper);cursor:pointer;user-select:none;-webkit-user-select:none;font-size:13px;font-weight:600;color:var(--ink)}
.schema:hover{border-color:var(--accent)}
.schalter{position:relative;display:block;width:54px;height:30px;border-radius:999px;background:var(--tint);border:1px solid var(--line)}
.schalter .knopf{position:absolute;top:2px;left:2px;width:24px;height:24px;border-radius:50%;background:var(--ink);transition:transform .22s ease}
.schalter svg{position:absolute;top:7px;transition:color .22s}
.schalter .ico-sonne{left:7px;color:var(--bg)}
.schalter .ico-mond{right:7px;color:var(--muted)}
#theme-dark:checked ~ .site .schalter .knopf{transform:translateX(24px)}
#theme-dark:checked ~ .site .schalter .ico-sonne{color:var(--muted)}
#theme-dark:checked ~ .site .schalter .ico-mond{color:var(--bg)}
.zustand-dunkel{display:none}
#theme-dark:checked ~ .site .zustand-hell{display:none}
#theme-dark:checked ~ .site .zustand-dunkel{display:inline}

/* ==== Kopfbereich ==== */
main{display:block}
.hero{max-width:var(--max);margin:auto;padding:88px var(--gutter) 64px}
.hero-raster{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(300px,.7fr);gap:56px;align-items:end}
.kicker{font-size:13px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:var(--accent-ink);margin-bottom:22px}
.hero h1{font-family:var(--display);font-weight:900;font-size:clamp(64px,10.4vw,164px);line-height:.84;letter-spacing:-.045em;text-transform:uppercase}
.hero h1 span{display:block}
.hero h1 .kontur{color:transparent;-webkit-text-stroke:2px var(--ink)}
.hero-text p{font-size:clamp(20px,1.7vw,26px);line-height:1.3;font-weight:500;letter-spacing:-.012em;margin-bottom:26px;text-wrap:pretty}
.hero-text strong{font-weight:700;background:linear-gradient(transparent 62%,color-mix(in srgb,var(--accent) 28%,transparent) 62%)}
.stand-chip{display:inline-flex;align-items:center;gap:10px;border:1px solid var(--line);border-radius:999px;padding:8px 14px;font-size:14px;font-weight:600;color:var(--muted);background:var(--paper)}
.live{width:8px;height:8px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 5px color-mix(in srgb,var(--accent) 18%,transparent)}
.linie{max-width:calc(var(--max) - 2*var(--gutter));margin:0 auto;border:0;border-top:1px solid var(--line)}

/* ==== Fälle ==== */
.fall{max-width:var(--max);margin:auto;padding:80px var(--gutter) 88px;scroll-margin-top:64px}
.fall-kopf{display:grid;grid-template-columns:150px minmax(0,1fr);gap:28px;align-items:start;margin-bottom:36px}
.fall-nr{font-family:var(--display);font-size:68px;font-weight:900;letter-spacing:-.05em;line-height:.85;color:var(--accent)}
.fall-label{font-size:12px;letter-spacing:.15em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:12px}
.fall-titel{font-family:var(--display);font-weight:800;font-size:clamp(38px,4.8vw,76px);line-height:1.02;letter-spacing:-.022em;word-spacing:.04em;max-width:1100px;text-wrap:balance}
.fall-unter{font-size:19px;color:var(--muted);margin-top:16px;max-width:860px;text-wrap:pretty}
.fall-raster{display:grid;grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr);gap:28px;align-items:start}

.visual{position:sticky;top:84px;aspect-ratio:760/900;border-radius:var(--radius);overflow:hidden;background:#16294e;box-shadow:var(--shadow)}
.visual svg{display:block;width:100%;height:100%}
.visual figcaption{position:absolute;left:24px;right:24px;bottom:20px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;
  color:#d4e0ef;font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase}
.visual figcaption b{font-family:var(--display);color:#fff}

.karte{border:1px solid var(--line);border-radius:var(--radius);background:var(--paper);box-shadow:var(--shadow);overflow:hidden}
.karte-kopf{padding:24px 32px;border-bottom:1px solid var(--line);display:flex;gap:16px;justify-content:space-between;align-items:baseline;flex-wrap:wrap}
.karte-kopf h3{font-family:var(--display);font-weight:800;font-size:15px;letter-spacing:.12em;text-transform:uppercase}
.datum{font-size:14px;font-weight:600;color:var(--muted);white-space:nowrap}
.leitfrage{padding:28px 32px;border-bottom:1px solid var(--line)}
.leitfrage small{display:block;font-size:12px;text-transform:uppercase;letter-spacing:.15em;color:var(--accent-ink);margin-bottom:10px;font-weight:700}
.leitfrage p{font-family:var(--display);font-weight:800;font-size:clamp(21px,1.75vw,27px);line-height:1.24;letter-spacing:-.004em;word-spacing:.03em;text-wrap:pretty}
.abschnitt{display:grid;grid-template-columns:180px minmax(0,1fr);gap:24px;padding:26px 32px;border-bottom:1px solid var(--line)}
.abschnitt h4{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);padding-top:5px;font-weight:700;line-height:1.4}
.abschnitt p{font-size:17px;line-height:1.6;text-wrap:pretty}
.abschnitt.fokus{background:var(--tint)}
.abschnitt.fokus h4{color:var(--accent-ink)}

.kasten{margin:28px 32px;border:1px solid var(--line);border-radius:16px;overflow:hidden}
.kasten-kopf{padding:14px 20px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;align-items:baseline;flex-wrap:wrap;background:color-mix(in srgb,var(--bg) 60%,var(--paper))}
.kasten-kopf h4{font-family:var(--display);font-weight:800;font-size:14px;letter-spacing:.08em;text-transform:uppercase}
.kasten-kopf span{font-size:13px;font-weight:600;color:var(--muted)}
.kasten ul{list-style:none;padding:0}
.kasten li{padding:15px 20px;border-bottom:1px dashed var(--line);font-size:15px;line-height:1.55}
.kasten li:last-child{border-bottom:0}
.kasten li b{color:var(--accent-ink)}

.cta{display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap;padding:0 32px 32px}
.cta a{display:inline-flex;align-items:center;gap:10px;min-height:48px;padding:0 20px 0 22px;border-radius:999px;background:var(--ink);color:var(--bg);
  text-decoration:none;font-size:15px;font-weight:700;transition:transform .2s ease,background-color .2s ease,color .2s ease}
.cta a:hover{transform:translateY(-2px);background:var(--accent-ink);color:#fff}
.cta a .pfeil{transition:transform .2s ease}
.cta a:hover .pfeil{transform:translate(2px,-2px)}
.cta-info{font-size:14px;color:var(--muted)}

/* ==== Brücke ==== */
.bruecke{max-width:var(--max);margin:auto;padding:0 var(--gutter)}
.bruecke-box{border-radius:var(--radius);border:1px solid var(--line);padding:34px 38px;display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;
  background:linear-gradient(120deg,var(--tint),var(--paper) 70%)}
.bruecke-box h2{font-family:var(--display);font-weight:800;font-size:clamp(26px,2.4vw,36px);letter-spacing:-.015em;word-spacing:.03em;line-height:1.1;text-wrap:balance}
.bruecke-box p{color:var(--muted);font-size:17px;max-width:650px}

/* ==== Fuß ==== */
.fuss{max-width:var(--max);margin:80px auto 0;padding:36px var(--gutter) 64px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:32px;align-items:flex-end;color:var(--muted)}
.fuss-marke{font-family:var(--display);font-size:32px;letter-spacing:-.03em;font-weight:900;color:var(--ink)}
.fuss p{margin-top:8px;font-size:15px;max-width:680px}
.fuss-index{display:flex;gap:6px 22px;flex-wrap:wrap;justify-content:flex-end;list-style:none;padding:0}
.fuss-index a{display:inline-flex;align-items:center;gap:8px;min-height:36px;font-size:15px;font-weight:600;color:var(--ink);text-decoration:none;
  border-bottom:2px solid transparent;transition:border-color .2s,color .2s}
.fuss-index a b{font-family:var(--display);color:var(--accent-ink)}
.fuss-index a:hover{border-color:var(--accent)}

/* ==== Umbrüche ==== */
@media (max-width:1100px){
  .hero-raster,.fall-raster{grid-template-columns:1fr}
  .visual{position:relative;top:auto;aspect-ratio:4/3}
  .fall-kopf{grid-template-columns:100px minmax(0,1fr)}
  .abschnitt{grid-template-columns:150px minmax(0,1fr)}
}
@media (max-width:800px){
  :root{--gutter:16px;--radius:18px}
  body{font-size:16px}
  .hero{padding:48px var(--gutter) 40px}
  .hero-raster{gap:28px}
  .hero h1{font-size:clamp(48px,17.5vw,112px)}
  .hero-text p{font-size:20px}
  .fall{padding:52px var(--gutter) 60px;scroll-margin-top:60px}
  .fall-kopf{grid-template-columns:1fr;gap:10px;margin-bottom:24px}
  .fall-nr{font-size:46px}
  .fall-titel{font-size:clamp(32px,9vw,46px)}
  .fall-unter{font-size:17px}
  .fall-raster{gap:16px}
  .visual{aspect-ratio:auto}
  .visual svg{height:auto;aspect-ratio:1/1}
  .visual figcaption{position:static;padding:14px 18px 16px}
  .karte-kopf,.leitfrage,.abschnitt{padding-left:20px;padding-right:20px}
  .abschnitt{grid-template-columns:1fr;gap:8px}
  .abschnitt p,.kasten li{font-size:16px}
  .kasten{margin:22px 20px}
  .kasten-kopf,.kasten li{padding-left:16px;padding-right:16px}
  .cta{padding:0 20px 24px;flex-direction:column;align-items:stretch}
  .cta a{justify-content:space-between}
  .bruecke-box{grid-template-columns:1fr;padding:24px 22px;gap:14px}
  .bruecke-box p{font-size:16px}
  .fuss{margin-top:56px;padding:28px var(--gutter) 48px;flex-direction:column;align-items:flex-start}
  .fuss p{font-size:16px}
  .fuss-index{justify-content:flex-start}
}
@media (max-width:420px){
  .topbar-inner{gap:8px}
  .wortmarke{font-size:14px;gap:9px;letter-spacing:.04em}
  .marke{width:26px;height:26px;flex-basis:26px}
  .marke:before,.marke:after{left:5px;top:10px}
  .schema{padding-right:4px}
  .schema-text{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
  .pill{min-width:34px;padding:0 8px}
}
/* ==== Einblender: Impressum, Datenschutz, Methodik (ohne Skript, über :target) ==== */
.fuss-recht{display:flex;flex-wrap:wrap;gap:4px 20px;list-style:none;padding:0;margin-top:18px}
.fuss-recht a{display:inline-flex;align-items:center;min-height:32px;font-size:14px;font-weight:600;color:var(--muted);text-decoration:underline;
  text-decoration-color:color-mix(in srgb,var(--muted) 45%,transparent);text-underline-offset:3px}
.fuss-recht a:hover{color:var(--ink);text-decoration-color:var(--accent)}
.einblender{display:none;position:fixed;inset:0;z-index:50;overflow-y:auto;overscroll-behavior:contain;padding:48px 20px}
.einblender:target{display:block;animation:einblenden .2s ease}
html:has(.einblender:target){overflow:hidden}
.einblender-hinter{position:fixed;inset:0;background:rgba(10,20,36,.62);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);cursor:default}
.einblender-panel{position:relative;max-width:760px;margin:0 auto;background:var(--paper);color:var(--ink);border:1px solid var(--line);
  border-radius:var(--radius);box-shadow:0 30px 80px rgba(0,0,0,.35);padding:40px 44px 34px}
.einblender-zu{position:absolute;top:14px;right:14px;display:grid;place-items:center;width:44px;height:44px;border-radius:50%;color:var(--ink);
  border:1px solid var(--line);background:var(--paper)}
.einblender-zu:hover{border-color:var(--accent);color:var(--accent-ink)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
.einblender-text{font-size:16px;line-height:1.62;padding-right:36px}
.einblender-text h2{font-family:var(--display);font-weight:800;font-size:clamp(26px,3vw,34px);line-height:1.1;letter-spacing:-.015em;margin:0 0 18px}
.einblender-text h3{font-family:var(--display);font-weight:800;font-size:14px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-ink);margin:26px 0 8px}
.einblender-text p{margin:0 0 12px}
.einblender-text ul{margin:0 0 12px 20px;padding:0}
.einblender-text li{margin:0 0 7px;padding-left:2px}
.einblender-text strong{font-weight:700}
.einblender-text a{color:var(--accent-ink);font-weight:600;text-underline-offset:3px}
.einblender-text .tag{display:inline-block;border:1.4px solid var(--ink);border-radius:999px;padding:1px 9px;font-family:var(--display);font-size:12px;
  line-height:1.5;letter-spacing:.06em;text-transform:uppercase;font-weight:700;vertical-align:1px}
.einblender-text .tag.offen{border-style:dashed}
.einblender-text .stand{color:var(--muted);font-size:14px;margin-top:22px;padding-top:14px;border-top:1px solid var(--line)}
.einblender-text .nur-deutsch{font-size:14px;color:var(--muted);border:1px dashed var(--line);border-radius:10px;padding:8px 12px;margin-bottom:18px}
.einblender-knopf{display:inline-flex;align-items:center;min-height:44px;padding:0 20px;margin-top:14px;border-radius:999px;background:var(--ink);color:var(--bg);
  text-decoration:none;font-size:15px;font-weight:700}
.einblender-knopf:hover{background:var(--accent-ink);color:#fff}
@keyframes einblenden{from{opacity:0}to{opacity:1}}
@media (max-width:800px){
  .einblender{padding:16px 10px}
  .einblender-panel{padding:28px 20px 24px}
  .einblender-zu{top:10px;right:10px}
  .einblender-text{padding-right:34px}
  .einblender-text h2{padding-right:10px}
}
@media (prefers-reduced-motion:reduce){
  .einblender:target{animation:none}
  html{scroll-behavior:auto}
  *,*:before,*:after{transition:none!important}
}
'''


def baue():
    werte_je = [lies_grafik(g) for g in D.GRAFIKEN]
    schriften = werte_je[0]["schriften"]
    if not schriften:
        fehler("Kein Block <style id=\"schriften\"> in %s." % D.GRAFIKEN[0]["datei"])
    for g, w in zip(D.GRAFIKEN[1:], werte_je[1:]):
        if w["schriften"] and w["schriften"] != schriften:
            print("HINWEIS: Schriftblock in %s weicht ab; verwendet wird der aus %s."
                  % (g["datei"], D.GRAFIKEN[0]["datei"]))

    # Stand im Kopfbereich: bei gleichem Datum einmal, sonst je Grafik
    staende = sorted({w["stand"] for w in werte_je}, key=lambda d: d[6:] + d[3:5] + d[:2])
    if len(staende) == 1:
        hw = {"stand": staende[0], "stand_en": datum_en(staende[0])}
    else:
        hw = {"stand": " · ".join("%s %s" % (g["nr"], w["stand"]) for g, w in zip(D.GRAFIKEN, werte_je)),
              "stand_en": " · ".join("%s %s" % (g["nr"], w["stand_en"]) for g, w in zip(D.GRAFIKEN, werte_je))}

    S = D.SEITE
    faelle = []
    for i, (g, w) in enumerate(zip(D.GRAFIKEN, werte_je)):
        faelle.append(fall(g, w))
        if i == 0:
            faelle.append('''
<section class="bruecke" aria-label="Zusammenhang der beiden Denkfilter">
  <div class="bruecke-box">
    %s
    %s
  </div>
</section>''' % (zwei(S["bruecke"]["titel"], tag="h2"), zwei(S["bruecke"]["text"], tag="p")))

    index = "".join('<li><a href="#%s"><b>%s</b> %s</a></li>' % (g["anker"], g["nr"], g["index"])
                    for g in D.GRAFIKEN)

    seite = '''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(description)s">
<!--
  Erzeugt von startseite_build.py aus startseite_daten.py. Nicht von Hand bearbeiten:
  Texte, Dateinamen und Fassungsvergleich stehen in startseite_daten.py,
  Stand-Datum und Schriften kommen aus den Grafiken.
  Ohne Skript, ohne Speicherung, ohne externen Abruf.
-->
%(schriften)s
<style>%(css)s</style>
</head>
<body>
<input class="ui-toggle" type="radio" name="lang" id="lang-de" checked aria-label="Deutsch">
<input class="ui-toggle" type="radio" name="lang" id="lang-en" aria-label="English">
<input class="ui-toggle" type="checkbox" id="theme-dark" aria-label="Dunkles Farbschema / Dark colour scheme">
<div class="site">
<header class="topbar">
  <div class="topbar-inner">
    <a class="wortmarke" href="#top"><span class="marke" aria-hidden="true"></span>DENKFILTER</a>
    <div class="steuerung">
      <div class="sprachwahl" role="presentation">
        <label class="pill" for="lang-de" lang="de">DE</label>
        <label class="pill" for="lang-en" lang="en">EN</label>
      </div>
      <label class="schema" for="theme-dark">
        <span class="schalter" aria-hidden="true"><span class="knopf"></span>%(sonne)s%(mond)s</span>
        <span class="schema-text"><span class="zustand-hell">%(hell)s</span><span class="zustand-dunkel">%(dunkel)s</span></span>
      </label>
    </div>
  </div>
</header>

<main id="top">
<section class="hero">
  <div class="hero-raster">
    <div>
      <div class="kicker">%(kicker)s</div>
      <h1><span>DENK</span><span class="kontur">FILTER</span></h1>
    </div>
    <div class="hero-text">
      %(hero)s
      <span class="stand-chip"><span class="live" aria-hidden="true"></span>%(hero_stand)s</span>
    </div>
  </div>
</section>
<hr class="linie">
%(faelle)s

<footer class="fuss" id="fuss">
  <div>
    <div class="fuss-marke">DENKFILTER</div>
    %(fuss)s
    <ul class="fuss-recht">%(recht)s</ul>
  </div>
  <nav aria-label="%(index_label)s"><ul class="fuss-index">%(index)s</ul></nav>
</footer>
</main>
%(einblender)s
</div>
</body>
</html>
''' % {
        "title": S["title"], "description": html.escape(S["description"], quote=True),
        "schriften": schriften, "css": CSS, "sonne": SONNE, "mond": MOND,
        "hell": zwei({"de": "Hell", "en": "Light"}), "dunkel": zwei({"de": "Dunkel", "en": "Dark"}),
        "kicker": S["kicker"], "hero": zwei(S["hero"], tag="p"),
        "hero_stand": zwei(S["hero_stand"], hw), "faelle": "\n".join(faelle),
        "fuss": zwei(S["fuss"], tag="p"), "index_label": S["ui"]["index"], "index": index,
        "recht": "".join('<li><a href="#%s">%s</a></li>' % (e["id"], zwei(e["link"])) for e in D.EINBLENDER),
        "einblender": "\n".join(einblender(e) for e in D.EINBLENDER),
    }
    pruefe(seite, schriften)
    with open(ZIEL, "w", encoding="utf-8") as f:
        f.write(seite)
    print("geschrieben: %s (%s Byte)" % (os.path.basename(ZIEL), format(len(seite.encode("utf-8")), ",").replace(",", ".")))
    for g, w in zip(D.GRAFIKEN, werte_je):
        print("  %s  Stand %s%s" % (g["datei"], w["stand"],
              ("  Vorfassung %s" % w["vergleich"]) if w["vergleich"] else ""))


# ---------------------------------------------------------------------------
# Prüfungen am Ergebnis
# ---------------------------------------------------------------------------
def pruefe(seite, schriften):
    ohne_schrift = seite.replace(schriften, "")
    verboten = ["http://", "https://", "//fonts", "@import", "<script", "javascript:",
                "localStorage", "sessionStorage", "indexedDB", "document.cookie",
                "Local-safe", "local-safe", " & ", "&amp;"]
    for v in verboten:
        if v in seite:
            fehler("verbotene Zeichenfolge im Ergebnis: %r" % v)
    if re.search(r"register", ohne_schrift, re.I):
        fehler("Das Wort 'Register' kommt vor.")
    for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", seite):
        if not u.startswith("data:") and not u.startswith("#"):
            fehler("externe url(): %s" % u)
    if re.search(r'\ssrc=', ohne_schrift):
        fehler("src-Attribut gefunden; alles muss inline sein.")
    ids = set(re.findall(r'\sid="([^"]+)"', seite))
    for ziel in re.findall(r'href="([^"]+)"', seite):
        if ziel.startswith("mailto:"):
            continue
        if ziel.startswith("#"):
            if ziel[1:] not in ids:
                fehler("Anker %s existiert nicht." % ziel)
        elif not os.path.isfile(os.path.join(ORDNER, html.unescape(ziel))):
            fehler("Linkziel %s existiert nicht." % ziel)
    # Zeichenumfang der eingebetteten Schriften
    bereiche = []
    m = re.search(r"unicode-range:([^;]+);", schriften)
    for teil in m.group(1).split(","):
        teil = teil.strip()[2:]
        a, _, b = teil.partition("-")
        bereiche.append((int(a, 16), int(b or a, 16)))
    text = re.sub(r"<style.*?</style>", "", seite, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    fremd = sorted({c for c in text if not any(a <= ord(c) <= b for a, b in bereiche)})
    if fremd:
        fehler("Zeichen außerhalb der eingebetteten Schriften: %s"
               % ", ".join("U+%04X %s" % (ord(c), c) for c in fremd))


if __name__ == "__main__":
    baue()
