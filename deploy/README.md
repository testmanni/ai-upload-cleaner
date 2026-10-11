# Upload zu ai-upload-cleaner.com

`deploy/deploy.py` lädt die öffentlichen Dateien per FTPS (FTP mit TLS) in den Webspace bei Host Europe. Der Ablauf `.github/workflows/deploy.yml` ruft es auf GitHub auf. Nur Python-Standardbibliothek, keine fremden Bausteine, die das Passwort zu sehen bekämen.

## Ablauf

| Ereignis | Was passiert |
| --- | --- |
| Push auf `main` | Export-Test für 6.0 und 3.0, dann Freigabe in der Umgebung „Produktion“, dann Upload und Prüfung über HTTPS |
| Push auf einen `claude/`-Branch | nur Trockenlauf: zeigt, was hochgeladen würde |
| Actions → Upload → Run workflow | Trockenlauf; auf `main` mit abgewähltem Haken echter Upload |

Ausgelöst wird nur, wenn sich eine öffentliche Datei, `deploy/` oder der Ablauf selbst ändert.

## Was das Skript tut

- **Nur öffentliche Dateien:** `index.html`, `anleitung.html`, `anleitung6.0.html`, die Werkzeugdateien 1.0, 3.0 und 6.0, `LICENSE`, `NOTICE`, `THIRD-PARTY-LICENSES.txt`, `licenses/`. Nie `tests/`, `build/`, `.github/`, `README.md`. Die Versionen 2.0, 4.0 und 5.0 bleiben offline; neue Werkzeugdateien müssen in `PUBLIC` in `deploy.py` ergänzt werden.
- **Nur Geändertes:** Auf dem Server liegt `.deploy-manifest.json` mit den SHA-256-Werten des letzten Uploads und dem Commit. Beim ersten Lauf fehlt es; dann wird nach Dateigröße verglichen.
- **Nichts löschen:** Dateien auf dem Server, die nicht im Repository stehen, bleiben unangetastet und werden im Protokoll nur genannt.
- **Keine halben Dateien:** Upload unter `<name>.uploading`, dann Umbenennen.
- **Prüfung über HTTPS:** Jede hochgeladene Datei wird von ai-upload-cleaner.com abgerufen und mit dem SHA-256 im Repository verglichen. Weicht eine ab, schlägt der Lauf fehl.

## Einrichtung

1. **Host Europe (KIS):** eigener FTP-Benutzer, beschränkt auf `/www/ai-upload-cleaner`, langes Passwort nur für diesen Zweck.
2. **GitHub → Settings → Secrets and variables → Actions → New repository secret:**
   - `FTP_SERVER`: Servername, für dieses Paket `vwp1575.webpack.hosteurope.de` (Rückwärts-DNS der FTP-IP, passt zum Zertifikat). Keine IP-Adresse: Das TLS-Zertifikat wird geprüft und ist auf einen Namen ausgestellt. Passt der Name nicht, bricht das Skript vor der Anmeldung ab und nennt die Namen im Zertifikat.
   - `FTP_USER`: Name des FTP-Benutzers
   - `FTP_PASSWORD`: sein Passwort
   - `FTP_DIR`: nur nötig, wenn der Benutzer nicht direkt im Webordner landet
3. **GitHub → Settings → Environments → „Produktion“ → Required reviewers:** dich eintragen. Dann wartet jeder Upload auf deinen Klick. Die Umgebung entsteht beim ersten Lauf auf `main` von selbst, aber ohne Freigabepflicht, bis sie eingetragen ist.
4. **Trockenlauf prüfen:** Actions → Upload → letzter Lauf → „Re-run jobs“. Die Zusammenfassung listet, was hochgeladen würde und welche Dateien nur auf dem Server liegen.

## Lokal

```
FTP_SERVER=… FTP_USER=… FTP_PASSWORD=… python3 deploy/deploy.py --trocken
```

Getestet am 11.10.2026 gegen einen lokalen FTPS-Server (pyftpdlib) mit erzwungener Verschlüsselung auf Steuer- und Datenkanal: erster Lauf nach Größe, Upload aller 30 Dateien, zweiter Lauf ohne Übertragung, einzelne geänderte Datei, falsches Passwort, fremde Datei bleibt erhalten, Prüfung über HTTP. Gegen den echten Server von Host Europe noch nicht.
