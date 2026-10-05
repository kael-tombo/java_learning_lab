# REAL WORLD PROJECT — Lab 10: Breach War-Room

## 1. War-Room Timeline
| T | Event | Owner |
|---|---|---|
| T+0 | Secret-scanner + impossible-travel alert | Monitor |
| T+5 | IC SEV1; scope: 3 accounts, 2 keys, 4 hosts | SRE/Sec |
| T+10 | Revoke keys + sessions; force re-auth | IAM |
| T+15 | Quarantine + scale-to-0; snapshots hashed | Ops |
| T+25 | WAF blocks IOCs; egress normalizes | Edge |
| T+60 | Clean rebuild green; certs re-issued | Platform |
| T+90 | Staged return; enhanced monitoring | IC closes |

## 2. Triage Runbook
1. Scope accounts/keys/hosts/data. 2. Revoke + kill sessions. 3. Isolate + snapshot. 4. Block IOCs. 5. Notify legal/DPO per plan.

## 3. Commands
```bash
curl -H "Authorization: Bearer OLD" https://api.example.com/me -w "%{http_code}\n"  # expect 401
kubectl scale deployment compromised-app --replicas=0 -n prod
echo | openssl s_client -connect api.example.com:443 2>/dev/null | openssl x509 -noout -dates
```

## 4. Metrics of Recovery
- Old creds 100% 401; egress to IOC 0; scans 0 critical; auth success baseline; 24h enhanced watch clean.

## 5. Comms Template
> Security update: leaked keys revoked, affected hosts isolated, clean rebuild verified. Forced re-login required. Next update <time>. Contact <link>. No further action unless notified.

## 6. Prevention
- OIDC short-lived, manager rotation, least-privilege RBAC, scan gates, WAF managed rules, cert auto-renew, quarterly tabletop.

## 7. Cost Template
Forensics + rotation + downtime + notice + churn-risk; exposure window (min) as headline metric.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- OWASP Top 10 (access control, crypto, vulnerable components): https://owasp.org/www-project-top-ten/
- Kubernetes RBAC + NetworkPolicy hardening: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- GitHub secret scanning / push protection: https://docs.github.com/en/code-security/secret-scanning
