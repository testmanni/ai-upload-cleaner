"""Erzeugt die Testdokumente für tests/run.py.

Alle Dokumente entstehen hier im Skript, damit keine Binärdateien im Repository liegen
und die Lage jedes Geheimnisses bekannt ist. fixtures.json hält diese Lagen fest,
normiert auf die Seite (0..1, Ursprung oben links).

Aufruf: python3 tests/make_fixtures.py <zielordner>
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import getAscentDescent, stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

NAME = "Erika Mustermann"
IBAN = "DE89 3704 0044 0532 0130 00"
EMAIL = "erika.mustermann@example.org"
PHONE = "+49 30 1234567"
CONTROL = "Rechnung März"
SECRETS = [NAME, IBAN, EMAIL, PHONE]

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _pdf_rect(text, x, y, size, pw, ph, font="Helvetica"):
    """Rechteck eines Textes in normierten Koordinaten (oben links)."""
    w = stringWidth(text, font, size)
    asc, desc = getAscentDescent(font, size)
    top = ph - (y + asc)
    return {"text": text, "x": x / pw, "y": top / ph, "w": w / pw, "h": (asc - desc) / ph}


def make_pdf(path):
    pw, ph = A4
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle(f"Kontoauszug {NAME}")
    c.setAuthor(NAME)
    c.setSubject(f"IBAN {IBAN}")
    pages = []

    # Seite 1: alle vier Geheimnisse und die Kontrollzeile
    rects = []
    c.setFont("Helvetica-Bold", 20)
    c.drawString(72, ph - 90, CONTROL)
    control = _pdf_rect(CONTROL, 72, ph - 90, 20, pw, ph, "Helvetica-Bold")
    c.setFont("Helvetica", 14)
    rows = [("Kontoinhaber: ", NAME), ("IBAN: ", IBAN), ("E-Mail: ", EMAIL), ("Telefon: ", PHONE)]
    y = ph - 150
    for label, secret in rows:
        c.drawString(72, y, label + secret)
        rects.append(_pdf_rect(secret, 72 + stringWidth(label, "Helvetica", 14), y, 14, pw, ph))
        y -= 34
    c.drawString(72, y - 20, "Betrag: 1.234,56 EUR")
    pages.append({"secrets": rects, "control": control})
    c.showPage()

    # Seite 2: Name und IBAN noch einmal, an anderer Stelle
    rects = []
    c.setFont("Helvetica", 14)
    c.drawString(72, ph - 100, "Seite 2 – Umsätze")
    # eine Zeile in eingebetteter Schrift, damit die Schriftprüfung eine Gegenprobe hat
    pdfmetrics.registerFont(TTFont("DejaVu", FONT))
    c.setFont("DejaVu", 12)
    c.drawString(72, ph - 130, "Verwendungszweck: Miete Oktober")
    c.setFont("Helvetica", 14)
    for label, secret, yy in (("Auftraggeber: ", NAME, ph - 300), ("Gegenkonto: ", IBAN, ph - 340)):
        c.drawString(72, yy, label + secret)
        rects.append(_pdf_rect(secret, 72 + stringWidth(label, "Helvetica", 14), yy, 14, pw, ph))
    pages.append({"secrets": rects, "control": _pdf_rect("Seite 2", 72, ph - 100, 14, pw, ph)})
    c.showPage()

    # Seite 3: wird im Test ausgeschlossen, darf im Export nicht vorkommen
    c.setFont("Helvetica", 14)
    c.drawString(72, ph - 100, "Geheimseite 3: Steuer-ID 12 345 678 901")
    pages.append({"secrets": [], "control": None, "excluded": True})
    c.showPage()
    c.save()
    # Anhang mit Kontodaten: darf im Export nicht mitreisen
    w = PdfWriter(clone_from=PdfReader(str(path)))
    w.add_attachment("kontodaten.txt", f"{NAME}\n{IBAN}\n".encode("utf-8"))
    with open(path, "wb") as fh:
        w.write(fh)
    return {"pages": pages, "excluded_text": "Steuer-ID 12 345 678 901"}


def _img_text(draw, xy, text, font, fill=(0, 0, 0)):
    draw.text(xy, text, font=font, fill=fill)
    l, t, r, b = draw.textbbox(xy, text, font=font)
    return l, t, r, b


def make_card(path):
    """Ausweisartiges Bild: Name wird per Box geschwärzt und beschriftet,
    die rote Ausweisnummer liegt außerhalb des Ausschnitts."""
    W, H = 1200, 760
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(FONT, 54)
    mid = ImageFont.truetype(FONT, 40)
    ctrl = _img_text(d, (80, 120), "PERSONALAUSWEIS", big)
    name = _img_text(d, (80, 320), NAME, big)
    red = _img_text(d, (80, 620), "Nr. L01X00T47", mid, fill=(220, 0, 0))
    n = lambda r: {"x": r[0] / W, "y": r[1] / H, "w": (r[2] - r[0]) / W, "h": (r[3] - r[1]) / H}
    meta = PngInfo()
    meta.add_text("Author", NAME)
    im.save(path, pnginfo=meta)
    # Ausschnitt: oberer Teil bis unter den Namen, die rote Nummer bleibt draußen
    crop = {"x": 0.03, "y": 0.08, "w": 0.94, "h": 0.62}
    return {"size": [W, H], "name": n(name), "control": n(ctrl), "red": n(red), "crop": crop}


def make_photo(path):
    """Foto mit GPS-Position und Kameramodell in den EXIF-Daten."""
    im = Image.new("RGB", (800, 600), (120, 160, 200))
    d = ImageDraw.Draw(im)
    d.rectangle((200, 150, 600, 450), fill=(240, 220, 120))
    exif = Image.Exif()
    exif[0x010F] = "TestHersteller"
    exif[0x0110] = "TestKamera X1"
    gps = exif.get_ifd(0x8825)
    gps[1] = "N"
    gps[2] = (52.0, 31.0, 12.0)
    gps[3] = "E"
    gps[4] = (13.0, 24.0, 36.0)
    im.save(path, "JPEG", quality=92, exif=exif)
    return {"exif_strings": ["TestKamera X1", "TestHersteller"]}


def make_scan(path):
    """Scan ohne Textebene: IBAN wird per Texterkennung gefunden und geschwärzt."""
    W, H = 1240, 900
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 40)
    ctrl = _img_text(d, (90, 110), CONTROL, ImageFont.truetype(FONT, 52))
    _img_text(d, (90, 300), "Bitte überweisen Sie auf das Konto", f)
    iban = _img_text(d, (90, 380), IBAN, f)
    _img_text(d, (90, 470), "bis zum 15.11.2026.", f)
    im.save(path)
    n = lambda r: {"x": r[0] / W, "y": r[1] / H, "w": (r[2] - r[0]) / W, "h": (r[3] - r[1]) / H}
    return {"size": [W, H], "iban": n(iban), "control": n(ctrl)}


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {
        "secrets": SECRETS,
        "control": CONTROL,
        "rechnung": make_pdf(out / "rechnung.pdf"),
        "ausweis": make_card(out / "ausweis.png"),
        "foto": make_photo(out / "foto.jpg"),
        "scan": make_scan(out / "scan.png"),
    }
    (out / "fixtures.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tests/out/fixtures")
