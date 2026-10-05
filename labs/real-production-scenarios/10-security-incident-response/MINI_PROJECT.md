# MINI PROJECT — Lab 10: Contain a Mock Breach

## Objective
Simulate leaked token + vulnerable image; revoke, isolate, rebuild.

## Part A — Reproduce (25 min)
1. Commit fake token to staging repo → scanner flags; use it to call `/admin/export` (expect 200 = vuln).
2. Deploy image with planted CVE (scanner red) + expired test cert (openssl shows dates).

## Part B — Detect (15 min)
1. Correlate scanner + impossible-travel log + 403→200 flip into scope table.
2. `curl -v`/`openssl` document cert failure.

## Part C — Fix (40 min)
1. Revoke token, force re-auth, verify old 401 / new 200.
2. Quarantine + scale-to-0, WAF-block IOC, snapshot with hash.
3. Patch image, rescan green, rotate cert, staged return with enhanced alerts.

## Deliverables
- Scope table + timeline + verify outputs (401/200, scan diff, cert dates).
- Notice draft + prevention (OIDC/RBAC/scan gates).

## Stretch
- JWT `alg:none` reject test; NetworkPolicy egress verify.

## Grading
Scope (25%), revoke verified (30%), rebuild green (25%), notice+prevention (20%).
