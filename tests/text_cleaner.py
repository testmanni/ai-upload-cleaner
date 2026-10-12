"""Test für den AI Text Cleaner (Prototyp).

Bedient das Werkzeug im Browser wie ein Mensch (Playwright, Chromium) und prüft, was es
herausgibt: den kopierten maskierten Text, die gespeicherte Listendatei und die
Rückübersetzung. Geprüft wird in Python gegen bekannte Geheimnisse, nicht mit Code aus
dem Werkzeug.

Ablauf wie in der Praxis über zwei Tage: Tag 1 maskieren, Liste von Hand ergänzen, speichern.
Tag 2 in einem frischen Browser die Liste laden und die Antwort einer KI zurückübersetzen,
darunter eine „böse KI“, die Platzhalter verändert und erfindet.

Aufruf:  python3 tests/text_cleaner.py [ai-text-cleaner.html]
Optional: CHROMIUM_PATH=/pfad/zu/chromium
Ergebnis: Tabelle auf der Konsole, Bericht in tests/out/text_cleaner.md, Exit-Code 1 bei Fehlern.
"""
import datetime
import hashlib
import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "out" / "text_cleaner"

# Erfundene Daten. Jedes Geheimnis muss nach dem Maskieren verschwunden sein.
ORIGINAL = """Sehr geehrte Frau Dr. Erika Musterfrau,

wie besprochen fasse ich den Fall von Max Mustermann zusammen. Herr Mustermann ist seit 2019 Kunde der Muster GmbH.
Max Mustermanns Vertrag läuft bis Ende des Jahres.
Erreichbar ist er unter max.mustermann@example.com oder 0211 1234567.
Die Erstattung geht auf das Konto DE89 3704 0044 0532 0130 00.
Wohnhaft: Beispielweg 12, 40489 Düsseldorf. Geboren am 03.04.1981.
Kundennummer 4711-0815-42.

Mit freundlichen Grüßen
Muster GmbH
"""
SECRETS = ["Erika", "Musterfrau", "Max Mustermann", "Mustermann", "max.mustermann@example.com",
           "0211 1234567", "DE89 3704 0044 0532 0130 00", "Beispielweg", "40489", "Düsseldorf",
           "03.04.1981", "4711-0815-42", "Muster GmbH"]

# Für die exakte Rundreise: nur Werte ohne Varianten, dann muss das Original Zeichen für Zeichen zurückkommen
ROUNDTRIP = "Anna Beispiel (anna@example.org) schreibt an Hans Probe. Anna Beispiel zahlt auf DE02 1203 0000 0000 2020 51.\nGruß, Hans Probe\n"


def norm(s):
    return re.sub(r"\s+", "", s).lower()


class Results:
    def __init__(self):
        self.rows = []

    def check(self, group, name, ok, detail=""):
        self.rows.append((group, name, bool(ok), str(detail)))
        return ok


class Tool:
    def __init__(self, browser, html):
        self.ctx = browser.new_context(locale="de-DE", viewport={"width": 1280, "height": 1000}, accept_downloads=True)
        self.ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        self.requests, self.errors, self.dialogs = [], [], []
        self.ctx.on("request", lambda r: self.requests.append(r.url))
        self.page = self.ctx.new_page()
        self.page.on("console", lambda m: self.errors.append(m.text) if m.type == "error" else None)
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("dialog", self._dialog)
        self.page.goto(html.as_uri())

    def _dialog(self, d):
        self.dialogs.append(d.message)
        d.accept()

    def paste_into(self, sel, text):
        p = self.page
        p.evaluate("t => navigator.clipboard.writeText(t)", text)
        p.click(sel)
        p.keyboard.press("Control+A")
        p.keyboard.press("Control+V")
        p.wait_for_timeout(150)

    def add(self, value, kind):
        p = self.page
        p.fill("#addValue", value)
        opt = p.eval_on_selector("#addType", "(s, k) => [...s.options].find(o => o.value === 'new:' + k || o.value === 'var:' + k)?.value", kind)
        p.select_option("#addType", opt)
        p.click("#addBtn")

    def clipboard(self):
        return self.page.evaluate("() => navigator.clipboard.readText()")

    def save_list(self, dest):
        with self.page.expect_download() as dl:
            self.page.click("#saveList")
        d = dl.value
        d.save_as(dest)
        return d.suggested_filename

    def load_list(self, path):
        self.page.set_input_files("#listFile", str(path))
        self.page.wait_for_timeout(150)

    def close(self):
        self.ctx.close()


def net_console(r, group, t):
    foreign = [u for u in t.requests if not u.startswith(("file:", "data:", "blob:"))]
    r.check(group, "Keine Netzwerkanfragen", not foreign, ", ".join(foreign[:3]) or f"{len(t.requests)} lokale Ladevorgänge")
    r.check(group, "Keine Fehler in der Konsole", not t.errors, "; ".join(t.errors[:3]))


def day1(browser, html, r):
    g = "Tag 1: maskieren"
    t = Tool(browser, html)
    p = t.page
    r.check(g, "Hinweis „ungetestete Version“ sichtbar", p.is_visible("text=Nur ungetestete Version im Entwicklungsprozess."))
    t.paste_into("#src", ORIGINAL)
    ph = p.eval_on_selector_all("#mapBody td.ph input", "els => els.map(e => e.value)")
    r.check(g, "Einfügen findet IBAN, E-Mail, Telefon von selbst", {"[IBAN 1]", "[E-Mail 1]", "[Telefon 1]"} <= set(ph), ", ".join(ph))

    t.add("Max Mustermann", "Person")
    t.add("Erika Musterfrau", "Person")
    t.add("Muster GmbH", "Firma")
    r.check(g, "Namen werden zu Platzhaltern", "[Person A]" in p.input_value("#masked") and "[Firma A]" in p.input_value("#masked"))

    # „Mustermanns“ wird wegen der Wortgrenze nicht ersetzt, die Leck-Prüfung muss das merken
    leak = p.is_visible("#leak")
    r.check(g, "Leck-Prüfung erkennt „Mustermanns“", leak and "„Max Mustermanns“ im Text" in p.inner_text("#leak"), p.inner_text("#leak")[:120] if leak else "nicht angeschlagen")
    r.check(g, "Kopieren bei Leck gesperrt", p.is_disabled("#copyMasked"))

    rest = p.inner_text("#rest")
    for frag in ["Herr Mustermann", "Beispielweg 12", "40489 Düsseldorf", "03.04.1981", "4711-0815-42"]:
        r.check(g, f"Restliste zeigt „{frag}“", frag in rest)

    # Liste von Hand ergänzen: Varianten und Adressdaten, wie ein Mensch es nach der Restliste tun würde
    t.add("Herr Mustermann", "[Person A]")
    t.add("Max Mustermanns", "[Person A]")
    t.add("Frau Dr. Erika Musterfrau", "[Person B]")
    for frag, kind in [("Beispielweg 12", "Adresse"), ("40489 Düsseldorf", "Ort"), ("03.04.1981", "Datum"), ("4711-0815-42", "Nummer")]:
        t.add(frag, kind)
    r.check(g, "Nach dem Ergänzen keine Leck-Warnung", not p.is_visible("#leak"))
    remaining = p.inner_text("#rest") if p.is_visible("#restBox") else ""
    r.check(g, "Restliste danach leer", not remaining.strip(), remaining.replace("\n", " ")[:160])

    p.evaluate("() => navigator.clipboard.writeText('VORHER')")
    if r.check(g, "Kopieren freigegeben", p.is_enabled("#copyMasked"), p.inner_text("#maskMsg")):
        p.click("#copyMasked")
        p.wait_for_timeout(150)
    masked = t.clipboard()
    (OUT / "maskiert.txt").write_text(masked, encoding="utf-8")
    r.check(g, "Maskierter Text liegt in der Zwischenablage", masked != "VORHER" and "[Person A]" in masked)
    r.check(g, "Hinweis an die KI steht vorne", masked.startswith("Hinweis: Wörter in eckigen Klammern"))
    found = [s for s in SECRETS if norm(s) in norm(masked)]
    r.check(g, "Kein Geheimnis im kopierten Text (unabhängig geprüft)", not found, ", ".join(found) or f"{len(SECRETS)} Geheimnisse geprüft")

    listfile = OUT / "zuordnung.txt"
    name = t.save_list(listfile)
    r.check(g, "Speichern fragt vorher nach", any("Klartext" in d for d in t.dialogs))
    r.check(g, "Dateiname zuordnung_NICHT_HOCHLADEN.txt", name == "zuordnung_NICHT_HOCHLADEN.txt", name)
    txt = listfile.read_text(encoding="utf-8")
    r.check(g, "Datei beginnt mit der Kopfzeile", txt.startswith("# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN"))
    r.check(g, "Datei enthält Varianten", "[Person A] = Max Mustermann; Herr Mustermann; Max Mustermanns" in txt)
    r.check(g, "Status „gespeichert“", "gespeichert" in p.inner_text("#mapState") and "nicht" not in p.inner_text("#mapState"), p.inner_text("#mapState"))
    net_console(r, g, t)
    t.close()
    return masked, listfile


def day2(browser, html, r, listfile):
    g = "Tag 2: zurückübersetzen"
    # Liste von Hand im Editor ändern: eine Variante ergänzen. Sie muss nach dem Laden wirken.
    edited = OUT / "zuordnung_bearbeitet.txt"
    txt = listfile.read_text(encoding="utf-8").replace("[Firma A] = Muster GmbH", "[Firma A] = Muster GmbH; Muster-Firma")
    edited.write_text(txt.replace("\n", "\r\n"), encoding="utf-8")  # Windows-Zeilenenden wie aus dem Editor

    t = Tool(browser, html)
    p = t.page
    t.load_list(edited)
    r.check(g, "Liste in frischem Browser geladen", "geladen" in p.inner_text("#listMsg"), p.inner_text("#listMsg"))
    p.click("#tabBack")
    answer = ("Gern. Kurzfassung für [Person B]:\n"
              "[Person A] ist Kunde der [Firma A]. Die Erstattung geht auf [IBAN 1].\n"
              "Bitte [person a] informieren und [Person D] einbinden. Person B sollte unterschreiben.\n")
    t.paste_into("#answer", answer)
    out = p.input_value("#restored")
    (OUT / "zurueck.txt").write_text(out, encoding="utf-8")
    rep = p.inner_text("#report")
    r.check(g, "Exakte Platzhalter ersetzt", "Erika Musterfrau" in out and "Max Mustermann ist Kunde der Muster GmbH" in out and "DE89 3704 0044 0532 0130 00" in out, out[:160])
    r.check(g, "„[person a]“ nicht ersetzt, als verändert gemeldet", "[person a]" in out and "[person a]" in rep and "[Person A]" in rep)
    r.check(g, "„[Person D]“ nicht ersetzt, als unbekannt gemeldet", "[Person D]" in out and "Unbekannt" in rep and "[Person D]" in rep)
    r.check(g, "„Person B“ ohne Klammern gemeldet", "„Person B“" in rep)
    r.check(g, "Fehlende Platzhalter genannt", "Nicht in der Antwort" in rep and "[Telefon 1]" in rep)

    # Von Hand ergänzte Variante wirkt beim Maskieren
    p.click("#tabMask")
    p.fill("#src", "Brief der Muster-Firma an Max Mustermann.")
    m = p.input_value("#masked")
    r.check(g, "Variante aus der bearbeiteten Datei wirkt", "Brief der [Firma A] an [Person A]." in m, m[-60:])

    # Verwechslung: Listendatei statt Antwort eingefügt
    p.click("#tabBack")
    t.paste_into("#answer", listfile.read_text(encoding="utf-8"))
    r.check(g, "Listendatei im Antwortfeld wird erkannt", "Zuordnungsdatei" in p.inner_text("#report") and not p.input_value("#restored"))
    net_console(r, g, t)
    t.close()


def roundtrip(browser, html, r):
    g = "Rundreise"
    t = Tool(browser, html)
    p = t.page
    t.paste_into("#src", ROUNDTRIP)
    t.add("Anna Beispiel", "Person")
    t.add("Hans Probe", "Person")
    p.uncheck("#prefix")
    if p.is_visible("#restBox"):
        p.check("#restOk")
    if r.check(g, "Kopieren freigegeben", p.is_enabled("#copyMasked"), p.inner_text("#maskMsg")):
        p.click("#copyMasked")
        p.wait_for_timeout(150)
    masked = t.clipboard()
    found = [s for s in ["Anna", "Beispiel", "Hans", "Probe", "anna@example.org", "DE02"] if norm(s) in norm(masked)]
    r.check(g, "Maskiert ohne Geheimnisse", not found, ", ".join(found) or masked.strip()[:100])
    lf = OUT / "rundreise_liste.txt"
    t.save_list(lf)
    t.close()

    t = Tool(browser, html)
    p = t.page
    t.load_list(lf)
    p.click("#tabBack")
    t.paste_into("#answer", masked)
    back = p.input_value("#restored")
    r.check(g, "Datei speichern, neu laden, zurückübersetzen: Zeichen für Zeichen gleich", back == ROUNDTRIP,
            "identisch" if back == ROUNDTRIP else repr(back[:120]))
    # Speichern und wieder laden muss dieselbe Datei ergeben (bis auf die Zeitzeile)
    lf2 = OUT / "rundreise_liste2.txt"
    t.save_list(lf2)
    strip = lambda s: "\n".join(l for l in s.splitlines() if not l.startswith("# Gespeichert:"))
    r.check(g, "Laden und erneut speichern ergibt dieselbe Liste", strip(lf.read_text("utf-8")) == strip(lf2.read_text("utf-8")))
    net_console(r, g, t)
    t.close()

    # Umlaute, ß und Sonderzeichen
    t = Tool(browser, html)
    p = t.page
    special = "Jürgen Weiß-Öztürk traf José Ñúñez und O'Brien in der Straße."
    p.fill("#src", special)
    for v in ["Jürgen Weiß-Öztürk", "José Ñúñez", "O'Brien"]:
        t.add(v, "Person")
    lf3 = OUT / "sonderzeichen.txt"
    t.save_list(lf3)
    masked = p.input_value("#masked")
    t.close()
    t = Tool(browser, html)
    p = t.page
    t.load_list(lf3)
    p.click("#tabBack")
    p.fill("#answer", masked.split("\n\n", 1)[-1])
    p.dispatch_event("#answer", "input")
    r.check(g, "Umlaute, ß, Akzente, Apostroph überstehen die Rundreise", p.input_value("#restored") == special, p.input_value("#restored"))
    t.close()


BAD_FILES = {
    "ohne Kopfzeile": "[Person A] = Max\n",
    "doppelter Platzhalter": "# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN\n[Person A] = Max\n[Person A] = Moritz\n",
    "leerer Wert": "# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN\n[Person A] = \n",
    "leere Variante": "# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN\n[Person A] = Max;;Herr M\n",
    "Wert bei zwei Platzhaltern": "# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN\n[Person A] = Max\n[Person B] = Moritz; max\n",
    "ungültiger Platzhalter": "# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN\n[Person a] = Max\n",
    "abgeschnitten": "# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN\n[Person A] = Max\n[Person B",
    "keine Einträge": "# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN\n# nur Kommentare\n",
}


def bad_files(browser, html, r):
    g = "Kaputte Listendateien"
    t = Tool(browser, html)
    p = t.page
    good = OUT / "gut.txt"
    good.write_text("# AI Text Cleaner · Zuordnung v1 · NICHT HOCHLADEN\n[Person A] = Gültig Bleibt\n", encoding="utf-8")
    t.load_list(good)
    for name, content in BAD_FILES.items():
        f = OUT / f"kaputt_{len(name)}_{abs(hash(name)) % 1000}.txt"
        f.write_text(content, encoding="utf-8")
        t.load_list(f)
        msg = p.inner_text("#listMsg")
        kept = p.eval_on_selector_all("#mapBody input", "els => els.map(e => e.value)")
        ok = "nicht geladen" in msg and ("Zeile" in msg or "keine Einträge" in msg) and "Gültig Bleibt" in kept and len(kept) == 3
        r.check(g, f"abgelehnt: {name}", ok, msg.replace("\n", " ")[:140])
    net_console(r, g, t)
    t.close()


def main():
    html = (ROOT / (sys.argv[1] if len(sys.argv) > 1 else "ai-text-cleaner.html")).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    r = Results()
    # Gegenprobe: Die Geheimnis-Prüfung muss am unmaskierten Original anschlagen, sonst beweist sie nichts
    missed = [s for s in SECRETS if norm(s) not in norm(ORIGINAL)]
    r.check("Gegenprobe", "Alle Geheimnisse im Original gefunden", not missed, ", ".join(missed) or f"{len(SECRETS)} von {len(SECRETS)}")
    with sync_playwright() as pw:
        exe = os.environ.get("CHROMIUM_PATH")
        browser = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        _, listfile = day1(browser, html, r)
        day2(browser, html, r, listfile)
        roundtrip(browser, html, r)
        bad_files(browser, html, r)
        browser.close()

    passed = sum(1 for x in r.rows if x[2])
    sha = hashlib.sha256(html.read_bytes()).hexdigest()
    lines = [f"# Test AI Text Cleaner: {passed} von {len(r.rows)} bestanden", "",
             f"Datei: `{html.name}` · SHA-256 `{sha}` · {datetime.datetime.now():%d.%m.%Y %H:%M}", "",
             "| Bereich | Prüfung | Ergebnis | Detail |", "| --- | --- | --- | --- |"]
    for gname, name, ok, detail in r.rows:
        lines.append(f"| {gname} | {name} | {'✅' if ok else '❌'} | {detail.replace('|', '/').replace(chr(10), ' ')} |")
        print(f"{'OK ' if ok else 'FEHLER'}  {gname:26} {name}" + ("" if ok else f"   → {detail}"))
    (OUT.parent / "text_cleaner.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{passed} von {len(r.rows)} bestanden")
    sys.exit(0 if passed == len(r.rows) else 1)


if __name__ == "__main__":
    main()
