"""Lädt die öffentlichen Dateien per FTPS (FTP mit TLS) zum Webhosting hoch.

- Nur Dateien aus PUBLIC, nie tests/, build/, .github/, README.md oder die Versionen 2.0, 4.0, 5.0.
- Nur Geändertes: Auf dem Server liegt .deploy-manifest.json mit den SHA-256-Werten des
  letzten Uploads. Fehlt es (erster Lauf), wird nach Dateigröße verglichen und im Zweifel
  hochgeladen.
- Nichts wird gelöscht. Dateien auf dem Server, die nicht im Repository stehen, bleiben.
- Jede Datei geht erst unter einem Zwischennamen hoch und wird dann umbenannt, damit nie
  eine halb übertragene Datei ausgeliefert wird.
- Nach dem Upload wird jede geänderte Datei über HTTPS abgerufen und mit dem SHA-256 des
  Repositorys verglichen (wenn SITE_URL gesetzt ist).

Umgebung: FTP_SERVER, FTP_USER, FTP_PASSWORD, optional FTP_DIR (Standard: Startordner des
Benutzers), FTP_PORT (21), SITE_URL. Aufruf: python3 deploy/deploy.py [--trocken]
Nur Python-Standardbibliothek.
"""
import argparse
import fnmatch
import ftplib
import ipaddress
import hashlib
import io
import json
import os
import socket
import ssl
import sys
import tempfile
import time
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
# Werkzeugdateien einzeln: 2.0, 4.0 und 5.0 bleiben offline (Entscheidung vom 11.10.2026).
PUBLIC = ["index.html", "anleitung.html", "anleitung6.0.html",
          "ai-upload-cleaner.html", "ai-upload-cleaner3.0.html", "ai-upload-cleaner6.0.html",
          "ai-text-cleaner.html",  # ungetestete Entwicklungsversion, online seit 12.10.2026
          "og-image.png", "LICENSE", "NOTICE", "THIRD-PARTY-LICENSES.txt", "licenses/*"]
MANIFEST = ".deploy-manifest.json"


class ReusingFTP_TLS(ftplib.FTP_TLS):
    """Viele FTPS-Server verlangen, dass der Datenkanal die TLS-Sitzung des Steuerkanals
    wiederverwendet (sonst Fehler 522/425). ftplib tut das von sich aus nicht."""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn, server_hostname=self.host, session=self.sock.session)
        return conn, size


def local_files():
    files = {}
    for pattern in PUBLIC:
        for p in sorted(ROOT.glob(pattern)):
            if p.is_file():
                rel = p.relative_to(ROOT).as_posix()
                files[rel] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size": p.stat().st_size}
    return files


def certificate_names(host, port):
    """Nur zur Diagnose bei unpassendem Zertifikat: Namen im Zertifikat auslesen, ohne Anmeldung.
    Es wird kein Benutzername und kein Passwort gesendet."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    probe = ftplib.FTP_TLS(context=ctx, timeout=60)
    probe.connect(host, port)
    probe.auth()
    der = probe.sock.getpeercert(binary_form=True)
    probe.close()
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as fh:
        fh.write(ssl.DER_cert_to_PEM_cert(der))
    try:
        info = ssl._ssl._test_decode_cert(fh.name)  # CPython, liest das Zertifikat ohne Zusatzpakete
    finally:
        os.unlink(fh.name)
    names = [v for k, v in info.get("subjectAltName", ()) if k == "DNS"]
    cn = [v for rdn in info.get("subject", ()) for k, v in rdn if k == "commonName"]
    return names or cn


def connect():
    host = os.environ["FTP_SERVER"]
    ctx = ssl.create_default_context()
    if os.environ.get("FTP_INSECURE_TLS") == "1":  # nur für den lokalen Test mit eigenem Zertifikat
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    port = int(os.environ.get("FTP_PORT", "21"))
    ftp = ReusingFTP_TLS(context=ctx, timeout=120)
    ftp.connect(host, port)
    try:
        ftp.auth()  # TLS mit Zertifikatsprüfung, bevor Zugangsdaten gesendet werden
    except ssl.SSLCertVerificationError as e:
        print(f"Das TLS-Zertifikat passt nicht zu FTP_SERVER={host!r}: {e.verify_message}")
        names = []
        try:
            names = certificate_names(host, port)
            print("Das Zertifikat ist ausgestellt auf: " + ", ".join(names))
            print("Einen dieser Namen als FTP_SERVER eintragen (ein Name mit * steht für beliebige Vorsilben).")
        except Exception as diag:
            print(f"Namen im Zertifikat nicht lesbar: {diag}")
        try:
            ipaddress.ip_address(host)
            rname = socket.gethostbyaddr(host)[0]
            fits = any(fnmatch.fnmatch(rname, n) for n in names)
            print(f"Name zur IP (Rückwärts-DNS): {rname} – passt {'zum' if fits else 'nicht zum'} Zertifikat.")
        except ValueError:
            pass  # FTP_SERVER ist keine IP
        except OSError as dns:
            print(f"Kein Name zur IP gefunden ({dns}).")
        print("Abgebrochen, ohne Anmeldung. Es wurden keine Zugangsdaten gesendet.")
        raise SystemExit(3)
    ftp.login(os.environ["FTP_USER"], os.environ["FTP_PASSWORD"])
    ftp.prot_p()
    ftp.set_pasv(True)
    if os.environ.get("FTP_DIR"):
        ftp.cwd(os.environ["FTP_DIR"])
    return ftp


def remote_manifest(ftp):
    buf = io.BytesIO()
    try:
        ftp.retrbinary(f"RETR {MANIFEST}", buf.write)
        return json.loads(buf.getvalue().decode("utf-8")).get("files", {})
    except ftplib.error_perm:
        return None


def remote_size(ftp, path):
    try:
        ftp.voidcmd("TYPE I")
        return ftp.size(path)
    except ftplib.error_perm:
        return None


def ensure_dir(ftp, rel_dir, made):
    parts = PurePosixPath(rel_dir).parts
    for i in range(1, len(parts) + 1):
        d = "/".join(parts[:i])
        if d in made:
            continue
        try:
            ftp.mkd(d)
        except ftplib.error_perm:
            pass  # existiert schon
        made.add(d)


def upload(ftp, rel, made):
    parent = str(PurePosixPath(rel).parent)
    if parent != ".":
        ensure_dir(ftp, parent, made)
    tmp = rel + ".uploading"
    with open(ROOT / rel, "rb") as fh:
        ftp.storbinary(f"STOR {tmp}", fh, blocksize=256 * 1024)
    try:
        ftp.delete(rel)
    except ftplib.error_perm:
        pass
    ftp.rename(tmp, rel)


def verify_http(site, rel, want, tries=3):
    url = site.rstrip("/") + "/" + rel
    for i in range(tries):
        try:
            req = urllib.request.Request(url + f"?v={int(time.time())}", headers={"Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=60) as r:
                got = hashlib.sha256(r.read()).hexdigest()
            if got == want:
                return True, "identisch"
            detail = f"abweichend ({got[:12]}… statt {want[:12]}…)"
        except Exception as e:  # Netz, 404, TLS
            detail = f"{type(e).__name__}: {e}"
        time.sleep(5 * (i + 1))
    return False, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trocken", action="store_true", help="nur anzeigen, nichts hochladen")
    args = ap.parse_args()

    local = local_files()
    ftp = connect()
    print(f"Verbunden mit {os.environ['FTP_SERVER']}, Ordner: {ftp.pwd()}")
    manifest = remote_manifest(ftp)
    plan = []
    for rel, info in local.items():
        if manifest is not None:
            old = manifest.get(rel)
            if old and old.get("sha256") == info["sha256"]:
                continue
            plan.append((rel, "neu" if not old else "geändert"))
        else:
            size = remote_size(ftp, rel)
            if size is None:
                plan.append((rel, "fehlt auf dem Server"))
            elif size != info["size"]:
                plan.append((rel, f"Größe weicht ab ({size} statt {info['size']} Bytes)"))
            else:
                plan.append((rel, "gleiche Größe, ohne Prüfsumme nicht sicher gleich"))

    print("Vergleich: " + ("über .deploy-manifest.json" if manifest is not None else "ohne Manifest, nach Dateigröße (erster Lauf)"))
    total = sum(local[r]["size"] for r, _ in plan)
    for rel, why in plan:
        print(f"  ↑ {rel}  [{why}]")
    print(f"{len(plan)} von {len(local)} Dateien hochzuladen, {total / 1048576:.1f} MB")
    try:
        listing = set(ftp.nlst())
        extra = sorted(n for n in listing if n not in {r.split('/')[0] for r in local} and n not in (".", "..", MANIFEST))
        if extra:
            print("Auf dem Server, nicht im Repository (bleibt unangetastet): " + ", ".join(extra))
    except ftplib.error_perm:
        pass

    if args.trocken or not plan:
        print("Trockenlauf: nichts hochgeladen." if args.trocken else "Server ist auf dem Stand des Repositorys.")
        ftp.quit()
        return 0

    made = set()
    for rel, _ in plan:
        print(f"  lade {rel} …", flush=True)
        upload(ftp, rel, made)
    data = json.dumps({"files": local, "uploaded": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                       "commit": os.environ.get("GITHUB_SHA", "")}, indent=1).encode("utf-8")
    ftp.storbinary(f"STOR {MANIFEST}", io.BytesIO(data))
    ftp.quit()
    print(f"Hochgeladen: {len(plan)} Dateien, Manifest aktualisiert.")

    site = os.environ.get("SITE_URL")
    if not site or not plan:
        return 0
    failed = 0
    for rel, _ in plan:
        ok, detail = verify_http(site, rel, local[rel]["sha256"])
        print(f"  {'✓' if ok else '✗'} {site.rstrip('/')}/{rel}: {detail}")
        failed += not ok
    if failed:
        print(f"{failed} Dateien werden nicht so ausgeliefert, wie sie im Repository stehen.")
        return 1
    print("Alle hochgeladenen Dateien werden byteidentisch ausgeliefert.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (*ftplib.all_errors, KeyError) as e:
        print(f"Abbruch: {type(e).__name__}: {e}")
        sys.exit(2)
