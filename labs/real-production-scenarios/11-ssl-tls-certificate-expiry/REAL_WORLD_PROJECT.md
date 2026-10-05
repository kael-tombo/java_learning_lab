# Lab 11 — Real-World Project: Cert Expiry War Room

## Incident Timeline (Example SEV-1)
| Time | Event |
|------|-------|
| T+0 | Blackbox probe fails: `probe_ssl_earliest_cert_expiry < 0` for `api.example.com` |
| T+2m | On-call confirms: `openssl s_client` shows `Not After: Oct 04` (yesterday) |
| T+5m | SEV-1 declared; status page "API TLS errors — investigating" |
| T+8m | cert-manager events show `Failed` ACME DNS-01 for 29 days (alert misrouted to ex-employee) |
| T+12m | Fallback: issue manual cert via CA dashboard, update secret, rolling restart |
| T+18m | `curl -sv` clean; error rate drops 100% → 0% |
| T+30m | Status page resolved; support macro sent |
| T+2d | Post-mortem + action items |

## War-Room Runbook
1. **Confirm** (2 min): `openssl s_client` dates + `kubectl describe certificate`.
2. **Scope**: which domains/secrets share the issuer? `kubectl get certificate -A`.
3. **Mitigate**: force renew (`cmctl renew`) or push fallback secret + restart.
4. **Verify**: curl health from 2 networks + blackbox probe green + Java client test.
5. **Communicate**: status page at 10 min, updates every 15 min, All-clear with duration.
6. **Follow-up**: post-mortem in 48h; track renewal-automation fix to done.

## Metrics That Matter
- TTD (time-to-detect): should be <5 min via probe, not user report.
- TTM (time-to-mitigate): fallback secret push <15 min.
- SLI: `min(days-to-expiry across fleet)`; SLO: always >14d.
- Support tickets tagged `tls/cert`; error budget burn during incident.

## Prevention Backlog
- [ ] ACME DNS-01 for all public certs; `renewBefore: 720h` (30d).
- [ ] Alerts 30/14/7/1d routed to owning team + escalation policy fix.
- [ ] Pre-staged fallback secret procedure tested quarterly.
- [ ] Cert inventory registry + weekly Slack digest.
- [ ] Staging renewal drill in CI.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Let's Encrypt issuance/renewal and 90-day lifetimes: https://letsencrypt.org/docs/
- Kubernetes cert-manager Certificate + renewBefore reference: https://kubernetes.io/docs/ (search cert-manager integration)
- Mozilla TLS / cipher guidance (Server Side TLS): https://wiki.mozilla.org/Security/Server_Side_TLS
