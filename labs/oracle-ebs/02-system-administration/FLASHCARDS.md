# FLASHCARDS — System Administration

| # | Front | Back |
|---|-------|------|
| 1 | FND security chain? | User → Responsibility → Menu/Functions → Data+Security groups. |
| 2 | `FND_USER_PKG.createuser` returns? | New `user_id`; bind responsibility after, with effective/expiry dates. |
| 3 | Per-row EXCEPTION purpose? | Isolate bad rows; log to error table; keep the other 499. |
| 4 | `processed_flag` pattern? | Staging state machine → idempotent restarts. |
| 5 | GL_JE_LINES_U1 keys? | `(JE_HEADER_ID, JE_LINE_NUM)` — dup = feeder bug. |
| 6 | Duplicate detection shape? | `GROUP BY header,line HAVING COUNT(*)>1`, scoped to failing period/status. |
| 7 | Re-sequence tool? | `ROW_NUMBER() OVER (PARTITION BY header ORDER BY line, date)`, applied by ROWID. |
| 8 | Concurrency-safe numbering? | Sequence `NEXTVAL`, never `MAX()+1`. |
| 9 | Profile precedence? | User > Responsibility > Application > Site. |
| 10 | `FND_HIDE_DB_PASSWORD=N` risk? | Credentials in every debug log, all tiers. |
| 11 | `fnd_profile.save` missing piece? | `COMMIT`, or nothing persists. |
| 12 | SOD violator query shape? | Filter conflicting resps, LISTAGG per user, HAVING DISTINCT>1. |
| 13 | Log file first because? | Exact ORA error + parameters — diagnosis starts at the failure, not the schema. |
| 14 | Quick fix vs permanent fix? | Re-sequence lines now; sequence-backed feeder forever. |
| 15 | Drift program purpose? | Nightly baseline diff on security profiles — prevention after remediation. |
