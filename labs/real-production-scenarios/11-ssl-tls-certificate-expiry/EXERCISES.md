# Lab 11 — SSL/TLS Certificate Expiry — Exercises (90)

## Part A — Inspection (1–15)
1. Run `echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -dates -subject -issuer`. Record dates.
2. Parse `notAfter` and compute days-to-expiry with `date -d`.
3. Check full chain: `openssl s_client -showcerts`. Identify leaf vs intermediate.
4. Verify hostname: compare SAN (`-ext subjectAltName`) vs requested host.
5. Inspect Java truststore: `keytool -list -v -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit | head -60`.
6. Write a 5-line Python script using `ssl` + `socket` to fetch expiry.
7. Configure a Prometheus `blackbox_exporter` TLS probe for one domain.
8. Write a PromQL alert for expiry < 14 days.
9. Create a cert inventory CSV: domain, issuer, expiry, owner, env (5 rows).
10. Simulate clock skew: what happens if server clock is +2 days? Explain OCSP impact.
11. Trigger a staging renewal with cert-manager: `kubectl describe certificate`.
12. Break renewal intentionally (wrong DNS-01 token) and capture the event.
13. Document the `certificate_expired` TLS alert in Wireshark/tcpdump.
14. Test Spring Boot SSL reload without restart.
15. Draft a 30/14/7-day escalation policy.

## Part B — Detection Lab (16–30)
16. Deploy `ssl_exporter` and scrape `probe_ssl_earliest_cert_expiry`.
17. Build a Grafana panel: days-to-expiry gauge with thresholds.
18. Write a Loki alert for `certificate has expired` in nginx logs.
19. Simulate expiry with a self-signed 1-minute cert; observe handshake failure.
20. Capture Java `SSLHandshakeException` stack trace; map to root cause.
21. Test CDN behavior (Cloudflare 526) with expired origin cert.
22. Verify OCSP stapling: `openssl s_client -status`.
23. Check CRL distribution points and fetch one CRL.
24. Audit wildcard vs per-service certs; list blast radius of each.
25. Run `cert-manager check` equivalent: list all Certificates + `renewalTime`.
26. Create a runbook step: "confirm expiry in <2 min".
27. Time yourself: from alert to diagnosis — target <5 min.
28. Write a post-mortem one-pager for a 20-min expiry outage.
29. Propose SLI: `% of certs with >14d validity`.
30. Peer-review another student's inventory for gaps.

## Stretch (Challenge)
- Automate renewal with ACME DNS-01 + Route53; prove zero-downtime rotation.
- Build a Lambda/cron that scans all domains weekly and posts to Slack.
