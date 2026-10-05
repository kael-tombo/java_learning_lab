# Lab 11 — Vision: On-Call Excellence for Cert Expiry

## The Standard
No customer ever discovers an expired certificate. Every expiry risk pages the owning team 30 days early with a runbook link. Rotation is automated; humans only handle exceptions.

## What Great Looks Like
- **Inventory as code**: every domain in a registry with owner, issuer, expiry, environment. No spreadsheet archaeology at 2 AM.
- **Alerts that escalate**: 30d ticket → 14d Slack → 7d page → 1d SEV. Each alert links to the 2-minute confirm command.
- **Zero-touch renewal**: ACME DNS-01 + cert-manager; staging proves rotation before prod.
- **Blast-radius thinking**: per-service certs for critical paths; wildcards only where rollback is fast.
- **Honest comms**: status page in 10 min, ETA updates every 15 min, no "minor issue" euphemisms for 100% TLS failure.

## Anti-Patterns
- Calendar reminder owned by someone who left the company.
- Shared wildcard with unknown consumers; nobody dares rotate it.
- `TrustAll` / `--insecure` committed as "temporary fix" and forgotten.
- Alert only at expiry — paging when it is already a SEV-1.

## On-Call Habits
1. Weekly cert report reviewed in standup during the 30-day window.
2. Quarterly rotation drill on staging (force renew + verify).
3. Every new domain merged with monitoring + owner in the same PR.
4. Post-mortems ask "why didn't automation catch it?" not "who forgot?"

## Interview Signal
Strong candidates describe days-to-expiry SLIs, cert-manager events triage, and fallback-secret strategy. Weak candidates say "we renew manually, it rarely fails."
