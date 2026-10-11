"""Export-Test für den AI Upload Cleaner.

Bedient das Werkzeug im Browser wie ein Mensch (Playwright, Chromium), fängt die
exportierten Dateien ab und prüft sie mit tests/checks.py, also ohne PDF.js und ohne
Code aus dem Werkzeug. Vorher läuft eine Gegenprobe: Dieselben Prüfungen müssen an den
ungeschwärzten Originalen anschlagen, sonst beweisen sie nichts.

Aufruf:  python3 tests/run.py ai-upload-cleaner6.0.html
         python3 tests/run.py ai-upload-cleaner6.0.html --nur-schnell   (ohne Texterkennung)
Optional: CHROMIUM_PATH=/pfad/zu/chromium, falls Playwright seinen Browser nicht findet.
Ergebnis: Tabelle auf der Konsole, Bericht in tests/out/bericht.md, Exit-Code 1 bei Fehlern.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
import checks as C  # noqa: E402
import make_fixtures  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "out"


# ---------- Bedienung des Werkzeugs ----------

class Tool:
    def __init__(self, browser, html):
        self.ctx = browser.new_context(locale="de-DE", viewport={"width": 1280, "height": 1000}, accept_downloads=True)
        self.ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        self.requests, self.errors = [], []
        self.ctx.on("request", lambda r: self.requests.append(r.url))
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("console", lambda m: self.errors.append(m.text) if m.type == "error" else None)
        self.page.goto(html.as_uri())
        self.page.wait_for_selector("#langToggle", state="visible")

    def close(self):
        self.ctx.close()

    def has(self, selector):
        return self.page.locator(selector).count() > 0

    def load(self, path, pages=1):
        p = self.page
        p.set_input_files("#fileInput", str(path))
        p.wait_for_selector("#workspace:not(.hidden)", timeout=60000)
        p.wait_for_function("n => document.querySelectorAll('#thumbs .thumb').length === n", arg=pages, timeout=60000)
        p.wait_for_selector("#loadingMsg.hidden", state="attached", timeout=60000)

    def search_and_redact(self, mode, text=""):
        """Suchen, alle offenen Treffer schwärzen. Gibt die Zahl der Treffer zurück."""
        p = self.page
        if p.locator("#searchPanel.hidden").count():
            p.click("#searchBtn")
        p.select_option("#searchMode", mode)
        if text:
            p.fill("#searchInput", text)
        p.click("#searchRun")
        p.wait_for_function("() => document.getElementById('searchStatus').textContent.trim().length > 0", timeout=60000)
        p.wait_for_timeout(300)
        nav_visible = p.locator("#searchNav:not(.hidden)").count() > 0
        status = p.inner_text("#searchStatus").strip()
        hits = p.locator("#hitList .hitrow").count() if mode == "all" else (1 if nav_visible else 0)
        if nav_visible and p.locator("#hitAll").is_enabled():
            status += " → " + p.inner_text("#hitAll").strip()
            p.click("#hitAll")
            p.wait_for_timeout(300)
        return hits, status

    def close_search(self):
        if not self.page.locator("#searchPanel.hidden").count():
            self.page.click("#searchClose")

    def canvas_rect(self, r, margin=0):
        bb = self.page.locator("#boxCanvas").bounding_box()
        return (bb["x"] + r["x"] * bb["width"] - margin, bb["y"] + r["y"] * bb["height"] - margin,
                bb["x"] + (r["x"] + r["w"]) * bb["width"] + margin, bb["y"] + (r["y"] + r["h"]) * bb["height"] + margin)

    def drag(self, r, margin=0):
        """Rechteck ziehen. Gibt zurück, wie weit die Zeichenfläche beim Ansetzen verrutscht ist.
        Danach wird die Lage neu gemessen, wie ein Mensch, der der Seite mit der Maus folgt:
        Bis 6.0.0 blendete die erste Box das Beschriftungsfeld ein und die Seite rutschte."""
        top = lambda: self.page.locator("#boxCanvas").bounding_box()["y"]
        before = top()
        x0, y0, _, _ = self.canvas_rect(r, margin)
        m = self.page.mouse
        m.move(x0, y0)
        m.down()
        self.page.wait_for_timeout(100)
        shift = top() - before
        _, _, x1, y1 = self.canvas_rect(r, margin)
        m.move(x1, y1, steps=10)
        m.up()
        self.page.wait_for_timeout(200)
        return shift

    def export(self, dest, confirm_no_boxes=False):
        """Export auslösen. Der Download startet nur, wenn die Selbstprüfung bestanden ist."""
        p = self.page
        try:
            with p.expect_download(timeout=120000) as dl:
                p.click("#downloadBtn")
                if confirm_no_boxes:
                    p.wait_for_selector("#dlg:not(.hidden)", timeout=5000)
                    p.click("#dlgYes")
            dl.value.save_as(dest)
            ok = True
        except Exception:
            ok = False
        msg = p.inner_text("#exportMsg").strip()
        cls = p.get_attribute("#exportMsg", "class") or ""
        return ok, msg, "ok" in cls.split()


# ---------- Szenarien ----------

def scenario_rechnung(browser, html, fx, fxdir, outdir):
    t = Tool(browser, html)
    res, notes = [], []
    try:
        t.load(fxdir / "rechnung.pdf", pages=3)
        modes = ["all"] if t.page.locator("#searchMode option[value=all]").count() else ["iban", "email", "phone"]
        for m in modes:
            n, status = t.search_and_redact(m)
            notes.append(f"Suche „{m}“: {status}")
        n, status = t.search_and_redact("text", fx["secrets"][0])
        notes.append(f"Textsuche Name: {status}")
        t.close_search()
        t.page.locator("#thumbs .thumb").nth(2).click()
        t.page.click("#excludeBtn")
        dest = outdir / "rechnung_export.pdf"
        ok, msg, msg_ok = t.export(dest)
        res.append(C.check("Download nach bestandener Selbstprüfung", ok, msg))
        res.append(C.check("Werkzeug meldet 0 Textzeichen", msg_ok and "0 Textzeichen" in msg, msg))
        if ok:
            res += C.check_pdf_export(dest, fx, expected_pages=2)
        res += network_and_console(t)
    finally:
        t.close()
    return res, notes


def scenario_ausweis(browser, html, fx, fxdir, outdir):
    t = Tool(browser, html)
    res, notes = [], []
    a = fx["ausweis"]
    try:
        t.load(fxdir / "ausweis.png")
        shift = t.drag(a["name"], margin=8)
        res.append(C.check("Seite verrutscht nicht beim Ansetzen der ersten Box", abs(shift) < 1, f"{shift:.0f} px"))
        t.page.select_option("#labelSel", "[Name]")
        t.page.click("#cropToolBtn")
        t.drag(a["crop"])
        dest = outdir / "ausweis_export.png"
        ok, msg, msg_ok = t.export(dest)
        res.append(C.check("Download nach bestandener Selbstprüfung", ok, msg))
        if ok:
            res += C.check_card_export(dest, fx)
        res += network_and_console(t)
    finally:
        t.close()
    return res, notes


def scenario_foto(browser, html, fx, fxdir, outdir):
    t = Tool(browser, html)
    res, notes = [], []
    try:
        t.load(fxdir / "foto.jpg")
        meta = t.page.inner_text("#metaInfo")
        res.append(C.check("Werkzeug erkennt GPS im Foto", "GPS" in meta, meta.strip()))
        dest = outdir / "foto_export.png"
        ok, msg, _ = t.export(dest, confirm_no_boxes=True)
        res.append(C.check("Download", ok, msg))
        if ok:
            res += C.check_photo_export(dest, fx)
        res += network_and_console(t)
    finally:
        t.close()
    return res, notes


def scenario_scan(browser, html, fx, fxdir, outdir):
    t = Tool(browser, html)
    res, notes = [], []
    try:
        t.load(fxdir / "scan.png")
        if not t.page.locator("#ocrBtn:not(.hidden)").count():
            return [C.check("Texterkennung vorhanden", None, "übersprungen: Knopf fehlt")], ["übersprungen"]
        if t.has("#ocrLangSel"):
            t.page.select_option("#ocrLangSel", "deu")
        t0 = time.time()
        t.page.click("#ocrBtn")
        t.page.wait_for_selector("#ocrCancelBtn:not(.hidden)", timeout=10000)
        t.page.wait_for_selector("#ocrCancelBtn.hidden", state="attached", timeout=180000)
        notes.append(f"Texterkennung: {time.time() - t0:.1f} s")
        n, status = t.search_and_redact("iban")
        notes.append(f"IBAN-Suche: {status}")
        t.close_search()
        dest = outdir / "scan_export.png"
        ok, msg, _ = t.export(dest)
        res.append(C.check("Download nach bestandener Selbstprüfung", ok, msg))
        if ok:
            res += C.check_scan_export(dest, fx)
        res += network_and_console(t)
    finally:
        t.close()
    return res, notes


PASTE_JS = """async b64 => {
  const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const dt = new DataTransfer(); dt.items.add(new File([bin], 'image.png', {type: 'image/png'}));
  document.body.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
}"""
READ_CLIPBOARD_PNG = """async () => {
  const items = await navigator.clipboard.read();
  const item = items.find(i => i.types.includes('image/png'));
  if (!item) return null;
  const a = new Uint8Array(await (await item.getType('image/png')).arrayBuffer());
  let s = ''; for (const x of a) s += String.fromCharCode(x); return btoa(s);
}"""


def scenario_clipboard(browser, html, fx, fxdir, outdir):
    """Screenshot mit Strg+V einfügen, Texterkennung und Fundstellen laufen von selbst,
    „Alle schwärzen“, „In Zwischenablage kopieren“, kopiertes Bild unabhängig prüfen."""
    import base64
    t = Tool(browser, html)
    res, notes = [], []
    try:
        if not t.has("#copyBtn"):
            return [C.check("Zwischenablage vorhanden", None, "übersprungen: Funktion fehlt in dieser Version")], ["übersprungen"]
        p = t.page
        t0 = time.time()
        p.evaluate(PASTE_JS, base64.b64encode((fxdir / "scan.png").read_bytes()).decode())
        p.wait_for_selector("#workspace:not(.hidden)", timeout=30000)
        p.wait_for_function("() => document.querySelectorAll('#hitList .hitrow').length > 0", timeout=120000)
        notes.append(f"Einfügen bis Fundstellenliste: {time.time() - t0:.1f} s; {p.inner_text('#searchStatus').strip()}")
        res.append(C.check("Strg+V öffnet den Screenshot, Fundstellen erscheinen von selbst", True, p.inner_text("#toast").strip()))
        p.click("#hitAll")
        p.wait_for_timeout(300)
        t.close_search()
        p.evaluate("async () => navigator.clipboard.writeText('VORHER')")
        p.click("#copyBtn")
        p.wait_for_function("() => /\\b(ok|err)\\b/.test(document.getElementById('exportMsg').className)", timeout=60000)
        msg = p.inner_text("#exportMsg").strip()
        res.append(C.check("Werkzeug meldet: geprüft und kopiert", "Zwischenablage kopiert" in msg, msg[:120]))
        data = p.evaluate(READ_CLIPBOARD_PNG)
        res.append(C.check("Bild liegt in der Zwischenablage", data is not None, "image/png" if data else "kein Bild"))
        if data:
            dest = outdir / "zwischenablage.png"
            dest.write_bytes(base64.b64decode(data))
            res += C.check_scan_export(dest, fx)
            exif, keys = C.image_metadata(dest)
            res.append(C.check("PNG ohne Metadaten", not exif and not keys, f"EXIF {exif}, Felder {keys}"))
        res += network_and_console(t)
    finally:
        t.close()
    return res, notes


def network_and_console(t):
    foreign = [u for u in t.requests if not u.startswith(("file:", "data:", "blob:"))]
    return [
        C.check("Keine Netzwerkanfragen", not foreign, ", ".join(foreign[:3]) or f"{len(t.requests)} lokale Ladevorgänge"),
        C.check("Keine Fehler in der Konsole", not t.errors, "; ".join(t.errors[:3]) or "keine"),
    ]


# ---------- Gegenprobe ----------

# Diese Prüfungen dürfen am Original bestehen: Sie sichern ab, dass nicht zu viel geschwärzt wird.
MAY_PASS_ON_ORIGINAL = ("Kontrollzeile", "Tesseract liest")


def counter_test(fx, fxdir):
    groups = [
        ("rechnung.pdf", C.check_pdf_export(fxdir / "rechnung.pdf", fx, expected_pages=2)),
        ("ausweis.png", C.check_card_export(fxdir / "ausweis.png", fx)),
        ("foto.jpg", C.check_photo_export(fxdir / "foto.jpg", fx)),
        ("scan.png", C.check_scan_export(fxdir / "scan.png", fx)),
    ]
    res = []
    for name, checks in groups:
        for cname, ok, detail in checks:
            if any(k in cname for k in MAY_PASS_ON_ORIGINAL):
                continue
            res.append(C.check(f"{name}: „{cname}“ schlägt am Original an", not ok, detail))
    return res


# ---------- Ablauf und Bericht ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="Werkzeugdatei, z. B. ai-upload-cleaner6.0.html")
    ap.add_argument("--nur-schnell", action="store_true", help="ohne Texterkennung")
    args = ap.parse_args()
    html = (ROOT / args.html).resolve() if not Path(args.html).is_absolute() else Path(args.html)
    fxdir, outdir = OUT / "fixtures", OUT / "exporte"
    outdir.mkdir(parents=True, exist_ok=True)
    fx = make_fixtures.main(fxdir)

    sections = [("Gegenprobe an den Originalen", counter_test(fx, fxdir), [], 0.0)]
    scenarios = [
        ("PDF mit Textebene: Suche, Ausschluss, Export", scenario_rechnung),
        ("Bild: Box mit Beschriftung und Ausschnitt", scenario_ausweis),
        ("Foto mit GPS-Daten", scenario_foto),
    ]
    if not args.nur_schnell:
        scenarios.append(("Scan: Texterkennung und IBAN-Suche", scenario_scan))
        scenarios.append(("Zwischenablage: Strg+V, schwärzen, kopieren", scenario_clipboard))
    with sync_playwright() as pw:
        exe = os.environ.get("CHROMIUM_PATH")
        browser = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        version = browser.version
        for title, fn in scenarios:
            t0 = time.time()
            try:
                res, notes = fn(browser, html, fx, fxdir, outdir)
            except Exception as e:  # Abbruch im Ablauf ist ein Fehlschlag, kein Absturz des Tests
                res, notes = [C.check("Ablauf ohne Abbruch", False, f"{type(e).__name__}: {str(e).splitlines()[0]}")], []
            sections.append((title, res, notes, time.time() - t0))
        browser.close()

    failed = skipped = total = 0
    lines = [f"# Export-Test {html.name}", "",
             f"- Datei-SHA-256: `{hashlib.sha256(html.read_bytes()).hexdigest()}`",
             f"- Browser: Chromium {version}",
             f"- Lauf: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", ""]
    for title, res, notes, secs in sections:
        print(f"\n== {title}" + (f" ({secs:.1f} s)" if secs else ""))
        lines += [f"## {title}" + (f" ({secs:.1f} s)" if secs else ""), ""]
        for n in notes:
            print(f"   · {n}")
            lines.append(f"- {n}")
        if notes:
            lines.append("")
        lines += ["| Ergebnis | Prüfung | Befund |", "| --- | --- | --- |"]
        for name, ok, detail in res:
            total += 1
            mark = "übersprungen" if ok is None else ("bestanden" if ok else "FEHLER")
            skipped += ok is None
            failed += ok is False
            print(f"   {'–' if ok is None else ('✓' if ok else '✗')} {name}: {detail}")
            lines.append(f"| {mark} | {name} | {str(detail).replace('|', '/')} |")
        lines.append("")
    summary = f"{total - failed - skipped} von {total} Prüfungen bestanden, {failed} Fehler, {skipped} übersprungen."
    print("\n" + summary)
    lines.append(f"**{summary}**")
    (OUT / "bericht.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
