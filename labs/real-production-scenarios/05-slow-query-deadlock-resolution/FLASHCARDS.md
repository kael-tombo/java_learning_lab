# FLASHCARDS — Slow Query & Deadlock Resolution

| # | Front | Back |
|---|---|---|
| 1 | Slow-query cascade? | Bad plan → long hold → pool pinned → app queue → timeouts |
| 2 | Top-digest metric? | total_time = calls × mean in `pg_stat_statements` |
| 3 | `EXPLAIN` vs `EXPLAIN ANALYZE`? | Plan only vs plan + executes (shows actual rows/time) |
| 4 | Seq Scan red flag? | Large actual rows + filter removed most — missing index/stats |
| 5 | Sargable meaning? | Predicate can use index; `lower(col)` usually cannot |
| 6 | Fix for stale stats? | `ANALYZE table` / `autoanalyze`; check `last_analyze` |
| 7 | Safe index build? | `CREATE INDEX CONCURRENTLY` — no write block |
| 8 | DB deadlock vs JVM deadlock? | PG auto-aborts one txn (app retries); JVM hangs until restart |
| 9 | Deadlock log signature? | `ERROR: deadlock detected ... Process X waits for ... blocked by ...` |
| 10 | Enable wait logging? | `log_lock_waits=on` + `deadlock_timeout=1s` |
| 11 | Lock-chain query? | `pg_locks JOIN pg_stat_activity` waiter→holder→query |
| 12 | Update-order fix? | Touch rows in consistent order (id ASC) in short txns |
| 13 | Retry recipe? | 3 tries, backoff 50ms×2^n + jitter, idempotency key |
| 14 | `SELECT FOR UPDATE` caution? | Locks rows; keep txn short, order consistent, avoid over-selecting |
| 15 | `statement_timeout`? | Aborts runaway query (e.g., 3s) so pool slot frees |
| 16 | `lock_timeout`? | Caps wait for a lock separately from execution |
| 17 | Kill vs cancel? | `pg_cancel_backend` gentle; `pg_terminate_backend` hard kill |
| 18 | DDL lock level? | Most DDL takes AccessExclusive — blocks reads+writes; run off-peak |
| 19 | App p99 tracks DB p99 → ? | DB-bound; fix query, not replicas |
| 20 | Pool + slow query link? | Hold time W inflates N=λW — faster query shrinks pool need |
| 21 | Idempotency key why? | Retry of aborted txn must not double-apply (payments!) |
| 22 | `auto_explain` use? | Auto-log plans of slow queries for postmortems |
| 23 | N+1 query signal? | calls huge, mean small, total big — batch with JOIN/IN |
| 24 | Missing-index proof? | Before/after EXPLAIN + buffers + timing on staging |
| 25 | First mitigation? | Kill blocker / shed traffic / timeout; index concurrently |
| 26 | Never ANALYZE heavy on? | Primary at peak — use replica/staging |
| 27 | Alert thresholds? | Digest p99>SLO 10m warn; deadlock rate>0 5m warn |
| 28 | Postmortem artifact? | Digest table, plans before/after, deadlock detail, retry proof |
| 29 | Prevention trio? | Query SLOs + index review + ordered-txn lint |
| 30 | Interview one-liner? | Digest→EXPLAIN→index/order→short txn→jittered idempotent retry |
