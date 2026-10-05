# THEORY — Lab 10: Security Incident Response

## 1. Mechanics: How Breaches Unfold
- Leaked credential / vulnerable lib → recon → initial access → lateral movement → exfiltration.
- OWASP Top 10 roots: injection, broken access control, crypto failures, vulnerable components.
- Secret in image/env/log + overly broad RBAC + unpatched base image = fast path.

## 2. Detection Signals
- Impossible-travel logins, new API keys, `403→200` flips on admin paths, egress to unknown hosts, crypto-miner CPU.
- Alerts: GuardDuty/Defender findings, WAF spike, secret-scanner hit, cert-transparency new subdomain.
- Triage: `kubectl audit logs`, IdP sign-ins, `openssl s_client` cert check, egress flow logs.

## 3. Containment Order (Stop Bleed First)
1. Revoke/rotate exposed creds + sessions (kill tokens, not just password).
2. Isolate workload: NetworkPolicy/quarantine node, scale malicious pods to 0.
3. Block IOCs at WAF/edge; snapshot forensic copies before rebuild.
4. Preserve logs (immutable store) — don't `rm` evidence.

## 4. Eradication + Recovery
- Patch base image, bump dep, rebuild from clean tag; verify SBOM/scan green.
- Re-issue certs/keys; force re-auth; restore from known-good backup, verify hashes.
- Staged return: canary + enhanced monitoring before 100%.

## 5. JWT / TLS Pitfalls
- `alg:none`, missing expiry/audience check, long-lived tokens, keys in repo.
- Expired/mismatched cert → `curl -v`/`openssl` shows chain error; rotate via managed cert + HSTS.

## 6. Least Privilege + Secrets
- RBAC minimal roles, short-lived OIDC (no static keys), secret manager + rotation, image pull least-privilege.
- Require 2-person approve for IAM/policy changes; alert on wildcard grants.

## 7. Common Mistakes
- Resetting password but leaving API tokens/sessions alive.
- Rebuilding on same compromised node without isolation.
- Paying ransom / hiding breach — legal + trust disaster.

## 8. Triage Order (First 15)
Scope (accounts/hosts/keys) → revoke → isolate → snapshot → block IOCs → notify per plan.

## 9. Legal/Comms
- Know DPO/legal trigger + notification windows; pre-approved templates; no speculation in writing.

## 10. Takeaways
- Speed of revocation + isolation beats perfect forensics; preserve evidence while cutting access.
