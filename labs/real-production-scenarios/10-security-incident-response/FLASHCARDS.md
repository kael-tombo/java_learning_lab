# FLASHCARDS — Lab 10: Security Response

| Front | Back |
|---|---|
| Initial access | First foothold via cred/vuln/phish |
| Lateral movement | Host-to-host spread post-access |
| Exfiltration | Data leaving to unknown hosts |
| IOC | Indicator (IP/hash/path) to block/hunt |
| Revoke-first | Kill tokens/sessions before forensics |
| Session kill | Invalidate refresh + access tokens |
| Force re-auth | Require fresh login post-rotation |
| Quarantine | Isolate node/workload via label/taint |
| NetworkPolicy deny-all | Cut pod ingress/egress fast |
| Scale-to-0 malicious | Stop bad pods after snapshot |
| Snapshot first | Forensic copy + hash before rebuild |
| Immutable logs | Tamper-proof store for evidence |
| Chain of custody | Who handled evidence, when, hash |
| WAF rule | Edge block on path/IP/rate |
| Rate block | Throttle abusive pattern (with expiry) |
| JWT alg allowlist | e.g., RS256 only; never none |
| exp/aud/iss | Expiry, audience, issuer checks |
| Short-lived token | Minutes-hours, refresh via rotation |
| OIDC over static keys | Ephemeral creds, no repo secrets |
| Secret manager | Vault/KeyVault/Secrets Manager + rotation |
| Rotation | Re-issue + revoke old on schedule/leak |
| RBAC least privilege | Minimal verbs/resources, no wildcard admin |
| 2-person IAM approve | Review gate for policy changes |
| Wildcard grant alert | `*:*` admin grant pages |
| Base-image CVE | Patch by bumping tag + rebuild |
| SBOM | Software bill of materials for vuln trace |
| Rescan green | Image scan 0 critical before deploy |
| Sign artifact | Provenance for clean rebuild |
| `openssl s_client` | Cert chain/dates live check |
| `curl -v https` | TLS handshake + cert debug |
| HSTS | Force HTTPS, verify header |
| Managed cert | Auto-renew via ACM/KeyVault/letsencrypt |
| Impossible travel | Logins from distant geos in minutes |
| 403→200 flip | Access-control bypass signal |
| Egress anomaly | Unknown external host surge |
| Miner CPU | Unexpected 100% CPU + pool traffic |
| Audit log | kubectl/IdP control-plane trail |
| Flow log | Network 5-tuple for egress hunt |
| GuardDuty/Defender | Managed threat findings |
| Secret scanner | Pre-commit/pipeline leak detector |
| Notify window | Legal deadline for breach notice |
| DPO/legal trigger | When PII/scope threshold met |
| Factual notice | What/who/window/fix/next, no speculation |
| Staged return | Canary back with heightened alerts |
| Enhanced monitoring | Lower thresholds during recovery |
| Tabletop | Breach drill without prod impact |
| Runbook page | Scope→revoke→isolate→snapshot→block→notify |
| Token 401 verify | Old cred must fail after revoke |
| Egress verify | curl to IOC must time out after block |
| Clean backup | Known-good hash before restore |
| PITR caution | Don't restore attacker-planted data blindly |
| Blameless + accountable | Systemic fix, owner + date per action |
| Interview line | "Revoked in X min, isolated via NP, rebuilt clean" |
| Static key danger | Repo/env/log leak path |
| Key in image | Rebuild + revoke, history rewrite won't save |
| Scope table | Accounts×keys×hosts×data matrix |
| Severity SEV1 | Active exfil/ransom = all-hands |
| Comms discipline | Single IC voice, timestamped updates |
