# FLASHCARDS — APEX Security

| # | Front | Back |
|---|-------|------|
| 1 | Auth order? | LDAP try → local verify; lockout checked before hashing. |
| 2 | Lockout rule? | 5 fails → 15-min lock; success resets. |
| 3 | Unknown user response? | Logged FALSE — indistinguishable from bad password. |
| 4 | Salt vs iterations? | Salt kills rainbow tables; iterations slow brute force. |
| 5 | PBKDF2 params here? | HMAC-SHA256, 10k iterations, 32-byte key, 16-byte salt. |
| 6 | Role default for unknown? | VIEWER (fail-closed to least privilege). |
| 7 | Permission check shape? | BULK COLLECT set → in-memory count; live tables, no cache. |
| 8 | Comma-armor INSTR? | Exact-token match, no substring false positives. |
| 9 | VPD trichotomy? | ADMIN `1=1` / scoped `branch_id=` / none `1=0`. |
| 10 | Predicate-filter alternative? | `AND (branch=:G OR role='ADMIN')` in every query — forgettable, unlike VPD. |
| 11 | Audit row contents? | User, action, detail, IP, session, page, app, timestamp. |
| 12 | Session lifetime? | 15 min idle + JS warning at 12 + KEEP_ALIVE callback. |
| 13 | Audit table growth? | Daily interval partitions + user/date indexes. |
| 14 | Hardening six-pack? | Binds, strip-HTML, session protection, checksums, HTTPS, error handler. |
| 15 | Three test classes? | Auth flow, authorization matrix, injection battery. |
