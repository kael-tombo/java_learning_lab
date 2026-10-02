# FLASHCARDS — Upgrade & Migration

| # | Front | Back |
|---|-------|------|
| 1 | ADOP-safe table, 3 steps? | Rename `_tb` → editioning view (orig name) → INSTEAD OF trigger. |
| 2 | Readiness query finds? | `XX%`, edition NULL, valid — zero rows is the gate. |
| 3 | Unscoped trigger UPDATE? | Rewrites whole table — always PK-scope. |
| 4 | Deprecated logging call → ? | `FND_FILE.PUT_LINE` → `FND_LOG.STRING`. |
| 5 | 14 h ADOP cycle assumes? | Deprecated-API cleanup already done. |
| 6 | DMS outage covers? | Stop-replication → promote → flip endpoints only (<2 h). |
| 7 | Endpoint target? | ELB DNS via fnd_profile.save + COMMIT. |
| 8 | DB-link credentials? | Wallet/secret — never cleartext scripts. |
| 9 | 11g→19c pre-checks? | preupgrd.sql + feature-usage audit. |
| 10 | LONG in 19c PL/SQL? | Compile error — rewrite to CLOB. |
| 11 | Post-upgrade stats? | Fixed-object, then dictionary GATHER STALE. |
| 12 | Standby-first why? | Outage shrinks to switchover; fallback preserved. |
| 13 | Missing COMMIT after save? | Change evaporates (same as sysadmin lab). |
| 14 | Rehearsal count? | Three: find, validate, prove-the-clock. |
| 15 | Fallback mechanism? | DB flashback + tested restore path, trigger criteria written down. |
