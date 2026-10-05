# Lab 11 — Mini Project: Reproduce + Detect + Fix Cert Expiry

## Objective
Create a self-signed short-lived cert, serve it, detect expiry, and automate renewal — all locally in ~60 minutes.

## Part 1 — Reproduce (20 min)
1. Generate a 5-minute cert:
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 0.0035 -nodes -subj "/CN=localhost"
python3 -m http.server --help  # or use openssl s_server
openssl s_server -accept 8443 -cert cert.pem -key key.pem -www &
```
2. Connect: `echo | openssl s_client -connect localhost:8443 2>/dev/null | openssl x509 -noout -dates`.
3. Wait 5 min, reconnect, capture the `certificate has expired` error.
4. Wrap a Java client (`HttpsURLConnection`) and record the `CertificateExpiredException`.

## Part 2 — Detect (20 min)
1. Write `check_cert.py` (ssl + socket) printing days-to-expiry; exit 2 if <7d.
2. Add a cron/systemd timer running it every minute against localhost:8443.
3. Simulate Prometheus: log `cert_expiry_seconds` and alert when below threshold.
4. Build cert inventory CSV for 3 fake domains with staggered expiries.

## Part 3 — Fix (20 min)
1. Write `renew.sh` regenerating a 90-day cert and reloading `s_server` without downtime (kill + restart, then verify).
2. Implement `renewBefore` logic: renew when days_left < 30.
3. Force a renewal failure (bad permissions on key.pem); show your alert fires.
4. Document runbook: confirm (1 cmd) → renew (1 cmd) → verify (curl) — each under 2 min.

## Deliverables
- `check_cert.py`, `renew.sh`, expiry log capture, inventory CSV, 1-page runbook.
- Success: expired cert detected before "users" (curl loop) report it; renewal verified with `openssl x509 -dates`.

## Grading
- Reproduce (30%), Detect (35%), Fix + runbook (35%). Bonus: cert-manager manifest with `renewBefore: 720h`.
