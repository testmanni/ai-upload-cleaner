#!/usr/bin/env python3
"""
Eingebettete Bibliotheken des AI Upload Cleaner (ab 2.0) prüfen oder aktualisieren.

Das Werkzeug ist eine einzelne HTML-Datei. PDF.js, jsPDF und zwei WebAssembly-Decoder liegen
darin als Base64 in <script type="application/octet-stream">-Blöcken; die 4.0 enthält zusätzlich
Tesseract.js (Worker, WebAssembly-Kern) und das deutsche Sprachmodell für die Texterkennung.
Dieses Skript stellt sicher, dass diese Blöcke byteidentisch mit den offiziellen Quellen sind
(npm-Pakete bzw. das tessdata_fast-Repository von tesseract-ocr).

    python3 build/libs.py verify ai-upload-cleaner4.0.html
        Entpackt jeden eingebetteten Block, berechnet SHA-256 und vergleicht mit den
        hier festgeschriebenen Prüfsummen. Braucht kein Netz. Exit-Code 0 = alles identisch.
        Blöcke, die es nur in der 4.0 gibt, gelten in 2.0 und 3.0 als "nicht enthalten".

    python3 build/libs.py update ai-upload-cleaner4.0.html [--tarball-dir VERZEICHNIS]
        Lädt die festgeschriebenen Paketversionen von registry.npmjs.org (Tarball gegen die
        Integritätsangabe des Registers geprüft) bzw. die festgeschriebene Datei-URL, prüft jede
        Datei gegen die Prüfsumme unten, bettet sie neu ein und schreibt build/CHECKSUMS.txt.
        Mit --tarball-dir werden bereits vorhandene Downloads wiederverwendet.

    python3 build/libs.py hash ai-upload-cleaner4.0.html
        SHA-256 der fertigen HTML-Datei (für Release-Notizen).

Nur Python-Standardbibliothek, keine Abhängigkeiten.
"""
import base64
import hashlib
import io
import json
import os
import re
import sys
import tarfile
import urllib.request

REGISTRY = "https://registry.npmjs.org"

# Festgeschriebene Versionen und SHA-256-Prüfsummen der eingebetteten Dateien.
# Stand: 25.09.2026 (PDF.js, jsPDF) und 26.09.2026 (Tesseract.js, Sprachmodell), berechnet aus den
# npm-Tarballs bzw. der heruntergeladenen Datei (Tarball-Integrität laut registry.npmjs.org: siehe CHECKSUMS.txt).
# "optional": True kennzeichnet Blöcke, die nur in der 4.0 vorkommen (Texterkennung).
PINS = {
    # Das "legacy"-Build enthält Polyfills und deckt laut PDF.js-Build (gulpfile, ENV_TARGETS)
    # Chrome >= 125, Firefox ESR, Safari >= 18 und die jeweils letzten zwei Versionen ab.
    # Das moderne Build setzt Sprachfunktionen voraus, die z. B. Chromium 141 noch nicht kennt.
    "lib-pdf": {
        "package": "pdfjs-dist", "version": "6.3.289", "path": "package/legacy/build/pdf.min.mjs",
        "sha256": "f401927e692efc7735e0cd528c490d0dd31b7f0972c122b7040df805be45cce4",
        "license": "Apache-2.0",
    },
    "lib-pdfworker": {
        "package": "pdfjs-dist", "version": "6.3.289", "path": "package/legacy/build/pdf.worker.min.mjs",
        "sha256": "a33cfe728c584fdba4fcc1fd54bcdc2f9f2f13889ddbb5b2bd1d0f8cbe49b84e",
        "license": "Apache-2.0",
    },
    "lib-wasm-openjpeg": {
        "package": "pdfjs-dist", "version": "6.3.289", "path": "package/wasm/openjpeg.wasm",
        "sha256": "004a0e62db930ba9ff2a22212f4554d0bb57a0635a8287caf70f98117cee14ba",
        "license": "BSD-2-Clause (OpenJPEG)",
    },
    "lib-wasm-jbig2": {
        "package": "pdfjs-dist", "version": "6.3.289", "path": "package/wasm/jbig2.wasm",
        "sha256": "e6bee67724a7b5436fe8162638e3708cfc8d52b6342db69a49715e30ff27cfdc",
        "license": "BSD-3-Clause (PDFium JBIG2)",
    },
    "lib-jspdf": {
        "package": "jspdf", "version": "4.2.1", "path": "package/dist/jspdf.umd.min.js",
        "sha256": "e6551fcdc32f09d6853b2c5126d18d01d9447e0da618a41a11ebeee0f6c20d54",
        "license": "MIT",
    },
    # Ab 4.0: Texterkennung. Der Worker läuft aus eingebettetem Code; die Haupt-Thread-Bibliothek von
    # Tesseract.js wird nicht gebraucht (das Werkzeug spricht das Nachrichtenprotokoll des Workers direkt).
    "lib-tessworker": {
        "package": "tesseract.js", "version": "7.0.0", "path": "package/dist/worker.min.js",
        "sha256": "576b7df7e3393e137e51849357c9adb53fe7ac1bb69bfa06cf3d61520f182c6d",
        "license": "Apache-2.0", "optional": True,
    },
    # Emscripten-Glue und WebAssembly-Kern: Tesseract OCR mit Leptonica und Bildbibliotheken, SIMD-Variante,
    # nur LSTM-Modelle (kleiner; die Legacy-Engine wird nicht gebraucht).
    "lib-tesscore": {
        "package": "tesseract.js-core", "version": "6.1.2", "path": "package/tesseract-core-simd-lstm.js",
        "sha256": "be3504705d7111d1d1f3f7f9dff326c26d334031ede36e31c4d3cf883027e982",
        "license": "Apache-2.0", "optional": True,
    },
    "lib-tesscore-wasm": {
        "package": "tesseract.js-core", "version": "6.1.2", "path": "package/tesseract-core-simd-lstm.wasm",
        "sha256": "187d76742dfc0d8929f0b49a619f145bb6370730776c7bd0d3e20c6b2098808d",
        "license": "Apache-2.0 (Tesseract), BSD-2-Clause (Leptonica) u. a., siehe THIRD-PARTY-LICENSES.txt", "optional": True,
    },
    # Sprachmodell Deutsch, schnelle Variante (tessdata_fast), festgeschrieben auf den Git-Tag 4.1.0.
    "lib-ocr-deu": {
        "url": "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/4.1.0/deu.traineddata",
        "origin": "tesseract-ocr/tessdata_fast, Tag 4.1.0, deu.traineddata",
        "sha256": "19d219bbb6672c869d20a9636c6816a81eb9a71796cb93ebe0cb1530e2cdb22d",
        "license": "Apache-2.0", "optional": True,
    },
}

BLOCK_RE = r'(<script id="%s" type="application/octet-stream">)(.*?)(</script>)'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_blocks(html: str):
    """Liefert {id: bytes} für die eingebetteten Blöcke der Datei. Pflichtblöcke müssen vorhanden sein,
    optionale Blöcke (nur 4.0) fehlen in älteren Dateien und werden dann ausgelassen."""
    out = {}
    for lib_id, pin in PINS.items():
        m = re.search(BLOCK_RE % re.escape(lib_id), html, re.S)
        if not m:
            if pin.get("optional"):
                continue
            raise SystemExit(f"Block {lib_id} nicht gefunden.")
        b64 = m.group(2).strip()
        if not b64 or b64.startswith("__"):
            out[lib_id] = b""
            continue
        out[lib_id] = base64.b64decode(b64, validate=True)
    return out


def cmd_verify(html_path: str) -> int:
    html = open(html_path, encoding="utf-8").read()
    blocks = read_blocks(html)
    ok = True
    print(f"{'Block':20} {'Paket':24} {'Bytes':>9}  Ergebnis")
    for lib_id, pin in PINS.items():
        name = pin_name(pin)
        if lib_id not in blocks:
            print(f"{lib_id:20} {name:24} {'-':>9}  nicht enthalten (optional)")
            continue
        data = blocks[lib_id]
        if not data:
            print(f"{lib_id:20} {name:24} {0:9}  LEER (Platzhalter)")
            ok = False
            continue
        digest = sha256(data)
        good = digest == pin["sha256"]
        ok = ok and good
        print(f"{lib_id:20} {name:24} {len(data):9}  {'identisch' if good else 'ABWEICHUNG: ' + digest}")
    print("Datei-SHA-256:", sha256(open(html_path, "rb").read()))
    print("Ergebnis:", "alle eingebetteten Bibliotheken sind byteidentisch mit den npm-Paketen." if ok else "ABWEICHUNG GEFUNDEN.")
    return 0 if ok else 1


def pin_name(pin: dict) -> str:
    return f"{pin['package']}@{pin['version']}" if "package" in pin else "tessdata_fast@4.1.0"


def fetch_url(pin: dict, cache_dir: str | None) -> bytes:
    """Lädt eine festgeschriebene Datei-URL (oder nimmt sie aus dem Cache) und prüft die SHA-256-Prüfsumme."""
    fname = pin["url"].rsplit("/", 1)[-1]
    local = os.path.join(cache_dir, fname) if cache_dir else None
    if local and os.path.exists(local) and sha256(open(local, "rb").read()) == pin["sha256"]:
        print(f"  {fname}: aus {cache_dir}")
        return open(local, "rb").read()
    print(f"  {fname}: lade {pin['url']}")
    with urllib.request.urlopen(pin["url"], timeout=300) as r:
        data = r.read()
    if sha256(data) != pin["sha256"]:
        raise SystemExit(f"{fname}: SHA-256 {sha256(data)} weicht von der festgeschriebenen Prüfsumme ab. Abbruch.")
    if local:
        os.makedirs(cache_dir, exist_ok=True)
        open(local, "wb").write(data)
    print(f"  {fname}: {len(data)} Bytes, Prüfsumme bestätigt")
    return data


def registry_meta(package: str, version: str) -> dict:
    with urllib.request.urlopen(f"{REGISTRY}/{package}/{version}", timeout=60) as r:
        return json.load(r)


def integrity_ok(data: bytes, integrity: str) -> bool:
    algo, _, b64 = integrity.partition("-")
    h = hashlib.new(algo, data).digest()
    return base64.b64encode(h).decode() == b64


def fetch_tarball(package: str, version: str, tarball_dir: str | None) -> tuple[bytes, str]:
    fname = f"{package}-{version}.tgz"
    meta = registry_meta(package, version)
    integrity = meta["dist"]["integrity"]
    local = os.path.join(tarball_dir, fname) if tarball_dir else None
    if local and os.path.exists(local):
        data = open(local, "rb").read()
        print(f"  {fname}: aus {tarball_dir}")
    else:
        url = meta["dist"]["tarball"]
        print(f"  {fname}: lade {url}")
        with urllib.request.urlopen(url, timeout=300) as r:
            data = r.read()
        if local:
            os.makedirs(tarball_dir, exist_ok=True)
            open(local, "wb").write(data)
    if not integrity_ok(data, integrity):
        raise SystemExit(f"Integritätsprüfung des Tarballs {fname} fehlgeschlagen (Register: {integrity}).")
    print(f"  {fname}: {len(data)} Bytes, Integrität laut Register bestätigt ({integrity[:16]}…)")
    return data, integrity


def cmd_update(html_path: str, tarball_dir: str | None) -> int:
    html = open(html_path, encoding="utf-8").read()
    present = read_blocks(html)  # nur Blöcke, die es in dieser Datei gibt
    tarballs = {}
    urls = []
    lines = []
    for lib_id, pin in PINS.items():
        if lib_id not in present:
            print(f"  {lib_id}: in dieser Datei nicht enthalten, übersprungen")
            continue
        if "url" in pin:
            print(f"Datei {pin['origin']}")
            content = fetch_url(pin, tarball_dir)
            urls.append(pin)
            src = pin["origin"]
        else:
            key = (pin["package"], pin["version"])
            if key not in tarballs:
                print(f"Paket {key[0]}@{key[1]}")
                tarballs[key] = fetch_tarball(key[0], key[1], tarball_dir)
            data, integrity = tarballs[key]
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                member = tf.extractfile(pin["path"])
                if member is None:
                    raise SystemExit(f"{pin['path']} nicht im Tarball.")
                content = member.read()
            src = f"{pin['package']}@{pin['version']:10} {pin['path']}"
        digest = sha256(content)
        if digest != pin["sha256"]:
            raise SystemExit(f"{lib_id}: SHA-256 {digest} weicht von der festgeschriebenen Prüfsumme ab. Abbruch.")
        b64 = base64.b64encode(content).decode("ascii")
        html, n = re.subn(BLOCK_RE % re.escape(lib_id), lambda m: m.group(1) + b64 + m.group(3), html, count=1, flags=re.S)
        if n != 1:
            raise SystemExit(f"Block {lib_id} nicht gefunden.")
        print(f"  {lib_id}: eingebettet ({len(content)} Bytes, sha256 {digest[:16]}…)")
        lines.append(f"{lib_id:20} {src:52} sha256={digest}  {pin['license']}")
    open(html_path, "w", encoding="utf-8", newline="\n").write(html)
    file_hash = sha256(open(html_path, "rb").read())
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHECKSUMS.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("AI Upload Cleaner: Herkunft und Prüfsummen der eingebetteten Bibliotheken (ab Version 2.0; Texterkennung ab 4.0)\n")
        f.write("Quelle: registry.npmjs.org (Tarball-Integrität laut Register geprüft) und das tessdata_fast-Repository von tesseract-ocr.\n")
        f.write("Nachprüfen ohne Netz: python3 build/libs.py verify <datei>.html\n\n")
        for (pkg, ver), (_, integrity) in tarballs.items():
            f.write(f"Tarball {pkg}-{ver}.tgz  integrity={integrity}\n")
        for pin in urls:
            f.write(f"Datei {pin['url']}  sha256={pin['sha256']}\n")
        f.write("\n")
        f.write("\n".join(lines) + "\n\n")
        for name, digest in tool_file_hashes(os.path.dirname(os.path.abspath(html_path))):
            f.write(f"{name}  sha256={digest}\n")
    print(f"Fertig. {html_path} aktualisiert, {out} geschrieben.")
    print("Datei-SHA-256:", file_hash)
    return 0


def tool_file_hashes(root: str):
    """SHA-256 aller Werkzeugdateien im Repo-Wurzelverzeichnis, deren eingebettete Blöcke den Pins entsprechen."""
    out = []
    for name in sorted(os.listdir(root)):
        if not (name.startswith("ai-upload-cleaner") and name.endswith(".html")):
            continue
        path = os.path.join(root, name)
        try:
            blocks = read_blocks(open(path, encoding="utf-8").read())
        except SystemExit:
            continue  # ältere Datei ohne die Pflichtblöcke (1.0)
        if all(blocks[k] and sha256(blocks[k]) == PINS[k]["sha256"] for k in blocks):
            out.append((name, sha256(open(path, "rb").read())))
    return out


def main(argv):
    if len(argv) < 3 or argv[1] not in ("verify", "update", "hash"):
        print(__doc__)
        return 2
    cmd, html_path = argv[1], argv[2]
    if cmd == "verify":
        return cmd_verify(html_path)
    if cmd == "hash":
        print(sha256(open(html_path, "rb").read()), " ", html_path)
        return 0
    tarball_dir = None
    if "--tarball-dir" in argv:
        tarball_dir = argv[argv.index("--tarball-dir") + 1]
    return cmd_update(html_path, tarball_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
