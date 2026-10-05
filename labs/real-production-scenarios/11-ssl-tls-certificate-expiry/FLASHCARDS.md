# Lab 11 — Flashcards: SSL/TLS Certificate Expiry

| # | Front | Back |
|---|-------|------|
| 1 | notBefore / notAfter | Validity window; client rejects outside it |
| 2 | TLS alert 45 | certificate_expired |
| 3 | Max public cert lifetime | 398 days (CA/B Forum) |
| 4 | Let's Encrypt lifetime | 90 days |
| 5 | SAN | SubjectAltName — hostname validation source |
| 6 | Chain of trust | Leaf → intermediate → root |
| 7 | openssl inspect dates | `openssl x509 -noout -dates` |
| 8 | Live chain check | `openssl s_client -connect host:443 -showcerts` |
| 9 | Java expired-cert error | SSLHandshakeException / PKIX path validation failed |
| 10 | cert-manager CR | Certificate → Secret |
| 11 | renewBefore | Early renewal window |
| 12 | Expiry metric | certmanager_certificate_expiration_timestamp_seconds |
| 13 | Alert thresholds | 30/14/7/1 days escalating |
| 14 | Blackbox TLS probe | probe_ssl_earliest_cert_expiry |
| 15 | OCSP | Online revocation status check |
| 16 | CRL | Certificate Revocation List |
| 17 | OCSP stapling check | `openssl s_client -status` |
| 18 | DNS-01 | ACME challenge required for wildcards |
| 19 | Cloudflare 526 | Invalid SSL Certificate (origin expired) |
| 20 | TrustAll workaround | Never — enables MITM |
| 21 | keytool list | `keytool -list -v -keystore cacerts` |
| 22 | SLI for certs | % certs with >14d validity / days-to-expiry |
| 23 | First detector | Metric alert, not user complaint |
| 24 | Blast radius control | Per-service certs, not one shared cert |
| 25 | Staging test | Verify renewal + truststore reload pre-prod |
| 26 | Clock skew impact | False expired/not-yet-valid failures |
| 27 | Ingress log signal | `certificate has expired` |
| 28 | Inventory fields | Domain, issuer, expiry, owner, env |
| 29 | Escalation | Ticket → Slack → Page as expiry nears |
| 30 | Root cause class | Process/automation failure, not bad luck |
| 31 | Handshake order | ClientHello → ServerHello + Certificate → validate |
| 32 | Intermediate expiry | Breaks whole chain even if leaf valid |
| 33 | Java truststore path | $JAVA_HOME/lib/security/cacerts |
| 34 | Readiness probe trick | Fail readiness on cert load error |
| 35 | ACME | Automated Certificate Management Environment |
| 36 | Wildcard risk | One expiry hits many services |
| 37 | Renewal event | kubectl describe certificate → Events |
| 38 | Post-mortem must | Timeline + detection gap + automation fix |
| 39 | Synthetic check | HTTPS probe every 1–5 min |
| 40 | On-call excellence | Automate + alert + inventory + rehearse |
| 41 | s_client servername | `-servername` for SNI hosts |
| 42 | Python fetch | ssl + socket getpeercert |
| 43 | Grafana gauge | Days-to-expiry with red <7d |
| 44 | Loki alert | Match `certificate has expired` |
| 45 | Self-signed drill | 1-min cert to observe failure safely |
| 46 | CDN behavior | Origin expiry → edge 526/errors |
| 47 | Private PKI | Internal CA needs same monitoring |
| 48 | Rotation without restart | Reload SSLContext / secret mount |
| 49 | Owner field | Every cert has a team + runbook link |
| 50 | Verify before citing | Re-check docs; don't copy expiry folklore |
| 51 | `kubectl get certificate` | Lists READY + AGE status |
| 52 | Secret mismatch | Wrong secretName mounted → stale cert served |
| 53 | Monitoring gap | Missing intermediate monitoring |
| 54 | Runbook target | Confirm expiry in <2 min |
| 55 | Diagnosis target | <5 min from alert |
| 56 | Prevention triad | Automate, alert, inventory |
| 57 | Audit cadence | Weekly scan + Slack report |
| 58 | Incident severity | Expired prod cert = SEV-1/2 (100% traffic risk) |
| 59 | Comm template | Status page + ETA + workaround |
| 60 | Lesson | Expiry is preventable process failure |
