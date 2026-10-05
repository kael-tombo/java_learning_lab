# VISION — Lab 10: On-Call Excellence in Security

## What Great Looks Like
- Leak → revoke in minutes, isolate in one command, evidence hashed, comms factual.
- Short-lived creds + minimal RBAC make most leaks non-events.
- No hero SSH; rebuild clean, verify green, return staged.

## Habits
1. Verify old token 401s — trust revoke, not intent.
2. Snapshot before rebuild, every time.
3. Expiry dates on every WAF block and quarantine.
4. Secret-scanner + image-scan gates in pipeline.
5. Quarterly breach tabletop with legal/DPO.

## Anti-Habits
- Speculating in chat/logs; hand-editing compromised hosts; hiding scope.

## Maturity Ladder
L0 static keys → L1 manager + rotation → L2 OIDC + least-privilege → L3 auto-scan/block + staged recovery → L4 zero-trust, continuous verify.

## Interview Signal
Scope table + revoke time + isolation command + rebuild proof + prevention (OIDC/RBAC/scan).
