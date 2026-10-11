"""Unabhängige Prüfungen einer exportierten Datei.

Bewusst ohne PDF.js und ohne Code aus dem Werkzeug: Text kommt aus pypdf und pdftotext
(Poppler), Pixel aus pdftoppm (Poppler) und Pillow, die Zweit-Erkennung aus Tesseract.
Jede Prüfung liefert (Name, bestanden, Erläuterung).
"""
import io
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

DARK = 64  # gleicher Grenzwert wie die Selbstprüfung des Werkzeugs: R, G und B unter 64


def check(name, ok, detail=""):
    """ok=None heißt übersprungen (Funktion fehlt in dieser Version)."""
    return (name, None if ok is None else bool(ok), detail)


# ---------- PDF ----------

def pdf_text_pypdf(path):
    r = PdfReader(str(path))
    return "".join((p.extract_text() or "") for p in r.pages)


def pdf_text_poppler(path):
    return subprocess.run(["pdftotext", "-q", str(path), "-"], capture_output=True, text=True, check=True).stdout


def pdf_render(path, dpi=100):
    """Seiten mit Poppler rendern, nicht mit PDF.js."""
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(path), f"{d}/p"], check=True)
        return [Image.open(p).convert("RGB").copy() for p in sorted(Path(d).glob("p*.png"))]


TEXT_OPS = {b"BT", b"Tj", b"TJ", b"'", b'"'}


def pdf_text_ops(path):
    """Seiten, deren Inhalt Textbefehle enthält."""
    found = []
    for i, page in enumerate(PdfReader(str(path)).pages, 1):
        # nicht "if contents": ein ContentStream ohne eigene Schlüssel gilt in Python als leer
        contents = page.get_contents()
        data = contents.get_data() if contents is not None else b""
        ops = TEXT_OPS & set(data.split())
        if ops:
            found.append(f"Seite {i}: {', '.join(sorted(o.decode() for o in ops))}")
    return found


def pdf_fonts(path):
    """Eingebettete Schriftdaten und bloße Verweise auf Standardschriften getrennt.
    jsPDF schreibt die 14 Standardschriften als Verweis in jede Seite, ohne Schriftdaten."""
    embedded, refs = set(), set()
    for page in PdfReader(str(path)).pages:
        res = page.get("/Resources")
        res = res.get_object() if res is not None else {}
        fonts = res.get("/Font")
        for f in (fonts.get_object().values() if fonts is not None else []):
            f = f.get_object()
            name = str(f.get("/BaseFont", "?"))
            descs = [f.get("/FontDescriptor")] + [d.get_object().get("/FontDescriptor") for d in f.get("/DescendantFonts", [])]
            if any(d is not None and any(k in d.get_object() for k in ("/FontFile", "/FontFile2", "/FontFile3")) for d in descs):
                embedded.add(name)
            else:
                refs.add(name)
    return sorted(embedded), sorted(refs)


def pdf_metadata(path):
    r = PdfReader(str(path))
    info = {k: str(v) for k, v in (r.metadata or {}).items()}
    attachments = list((r.attachments or {}).keys())
    return info, attachments


def raw_contains(path, needles):
    """Kommt ein Geheimnis in den Rohbytes vor? Auch als UTF-16 (PDF-Textstrings)."""
    data = Path(path).read_bytes()
    hits = []
    for n in needles:
        for enc in ("utf-8", "utf-16-be", "latin-1"):
            try:
                b = n.encode(enc)
            except UnicodeEncodeError:
                continue
            if b in data:
                hits.append(f"{n!r} ({enc})")
                break
    return hits


# ---------- Pixel ----------

def region_stats(img, r, inset=0.15):
    """Anteil dunkler, weißer und farbiger Pixel in einem normierten Rechteck.
    inset schneidet den Rand ab, damit Kantenglättung nicht zählt."""
    W, H = img.size
    x0, y0 = r["x"] * W, r["y"] * H
    x1, y1 = (r["x"] + r["w"]) * W, (r["y"] + r["h"]) * H
    dx, dy = (x1 - x0) * inset / 2, (y1 - y0) * inset
    box = (int(x0 + dx), int(y0 + dy), int(x1 - dx), int(y1 - dy))
    px = list(img.crop(box).getdata())
    n = max(1, len(px))
    dark = sum(1 for p in px if p[0] < DARK and p[1] < DARK and p[2] < DARK)
    white = sum(1 for p in px if min(p) > 200)
    return dark / n, white / n


def is_redacted(img, r, label_allowed=False):
    dark, white = region_stats(img, r)
    if label_allowed:
        # Beschriftete Box: Schwarz mit weißer Schrift, keine Grautöne des Originals
        return dark >= 0.6 and dark + white >= 0.97, f"dunkel {dark:.0%}, weiß {white:.0%}"
    return dark >= 0.98, f"dunkel {dark:.0%}"


def is_readable(img, r):
    """Kontrollzeile: nicht geschwärzt, also überwiegend hell."""
    dark, white = region_stats(img, r, inset=0.0)
    return 0.02 < dark < 0.6, f"dunkel {dark:.0%}"


def red_pixels(img):
    return sum(1 for p in img.getdata() if p[0] > 180 and p[1] < 80 and p[2] < 80)


# ---------- Bilder und Metadaten ----------

def image_metadata(path):
    im = Image.open(path)
    exif = dict(im.getexif())
    keys = [k for k in im.info.keys() if k not in ("dpi",)]
    return exif, keys


def ocr_text(img):
    if not shutil.which("tesseract"):
        return None
    with tempfile.TemporaryDirectory() as d:
        p = f"{d}/i.png"
        img.save(p)
        return subprocess.run(["tesseract", p, "-", "-l", "deu"], capture_output=True, text=True).stdout


def norm(s):
    return "".join(s.split()).lower()


# ---------- Prüfgruppen ----------

def check_pdf_export(path, fx, expected_pages):
    """Hauptfall: PDF mit Textebene, geschwärzt, Seite 3 ausgeschlossen."""
    out = []
    t1, t2 = pdf_text_pypdf(path), pdf_text_poppler(path)
    n1, n2 = len(norm(t1)), len(norm(t2))
    out.append(check("Kein Text (pypdf)", n1 == 0, f"{n1} Zeichen"))
    out.append(check("Kein Text (pdftotext)", n2 == 0, f"{n2} Zeichen"))
    ops = pdf_text_ops(path)
    out.append(check("Keine Textbefehle im Seiteninhalt", not ops, "; ".join(ops) or "nur Bildbefehle"))
    emb, refs = pdf_fonts(path)
    out.append(check("Keine eingebetteten Schriften", not emb, ", ".join(emb) or f"keine; {len(refs)} Verweise auf Standardschriften ohne Schriftdaten"))
    hits = raw_contains(path, fx["secrets"] + [fx["rechnung"]["excluded_text"]])
    out.append(check("Keine Geheimnisse in den Rohbytes", not hits, ", ".join(hits) or "nichts gefunden"))
    info, att = pdf_metadata(path)
    leak = [f"{k}={v}" for k, v in info.items() if any(norm(s) in norm(v) for s in fx["secrets"] + ["Mustermann"])]
    out.append(check("Metadaten ohne Namen", not leak, "; ".join(leak) or str(info)))
    out.append(check("Keine Anhänge", not att, ", ".join(att) or "keine"))
    imgs = pdf_render(path)
    out.append(check("Seitenzahl", len(imgs) == expected_pages, f"{len(imgs)} statt {expected_pages}"))
    kept = [p for p in fx["rechnung"]["pages"] if not p.get("excluded")]
    for pi, (page, img) in enumerate(zip(kept, imgs), 1):
        for r in page["secrets"]:
            ok, d = is_redacted(img, r)
            out.append(check(f"Seite {pi}: „{r['text']}“ geschwärzt", ok, d))
        if page["control"]:
            ok, d = is_readable(img, page["control"])
            out.append(check(f"Seite {pi}: Kontrollzeile lesbar", ok, d))
    joined = " ".join(norm(ocr_text(i) or "") for i in imgs)
    if shutil.which("tesseract"):
        found = [s for s in fx["secrets"] + [fx["rechnung"]["excluded_text"]] if norm(s) in joined]
        out.append(check("Tesseract findet keine Geheimnisse", not found, ", ".join(found) or "nichts gefunden"))
        out.append(check("Tesseract liest die Kontrollzeile", norm("Rechnung") in joined, "Gegenprobe der Zweit-Erkennung"))
    return out


def check_card_export(path, fx):
    """Box mit Beschriftung [Name] und Ausschnitt, Export als PNG."""
    out = []
    a = fx["ausweis"]
    img = Image.open(path).convert("RGB")
    W, H = img.size
    c = a["crop"]
    want = (c["w"] * a["size"][0]) / (c["h"] * a["size"][1])
    got = W / H
    out.append(check("Seitenverhältnis wie der Ausschnitt", abs(got - want) / want < 0.03, f"{got:.3f} statt {want:.3f}"))
    out.append(check("Rote Nummer außerhalb des Ausschnitts fehlt", red_pixels(img) == 0, f"{red_pixels(img)} rote Pixel"))
    to_crop = lambda r: {"x": (r["x"] - c["x"]) / c["w"], "y": (r["y"] - c["y"]) / c["h"], "w": r["w"] / c["w"], "h": r["h"] / c["h"]}
    ok, d = is_redacted(img, to_crop(a["name"]), label_allowed=True)
    out.append(check("Name geschwärzt (Beschriftung erlaubt)", ok, d))
    ok, d = is_readable(img, to_crop(a["control"]))
    out.append(check("Kontrollzeile lesbar", ok, d))
    exif, keys = image_metadata(path)
    out.append(check("PNG ohne Metadaten", not exif and not keys, f"EXIF {exif}, Felder {keys}"))
    t = ocr_text(img)
    if t is not None:
        out.append(check("Tesseract findet den Namen nicht", "mustermann" not in norm(t), "nichts gefunden" if "mustermann" not in norm(t) else "gefunden"))
    return out


def check_photo_export(path, fx):
    out = []
    exif, keys = image_metadata(path)
    out.append(check("Keine EXIF-Daten", not exif, str(exif) or "keine"))
    hits = raw_contains(path, fx["foto"]["exif_strings"] + ["GPS", "Exif"])
    out.append(check("Kamera und GPS nicht in den Rohbytes", not hits, ", ".join(hits) or "nichts gefunden"))
    out.append(check("Keine weiteren Metadatenfelder", not keys, str(keys) or "keine"))
    return out


def check_scan_export(path, fx):
    out = []
    s = fx["scan"]
    img = Image.open(path).convert("RGB")
    ok, d = is_redacted(img, s["iban"])
    out.append(check("IBAN geschwärzt", ok, d))
    ok, d = is_readable(img, s["control"])
    out.append(check("Kontrollzeile lesbar", ok, d))
    t = ocr_text(img)
    if t is not None:
        found = norm(fx["secrets"][1]) in norm(t)
        out.append(check("Tesseract findet die IBAN nicht", not found, "gefunden" if found else "nichts gefunden"))
    return out
