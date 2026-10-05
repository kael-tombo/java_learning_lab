# FLASHCARDS — Connection Pool Exhaustion

| # | Front | Back |
|---|---|---|
| 1 | Pool exhaustion one-liner? | All slots checked out; new requests wait until `connectionTimeout` |
| 2 | App-wait vs DB-overload signal? | App pending + DB idle = pool starvation; DB active high = DB overload |
| 3 | Key metrics trio? | `active`, `idle`, `pending` threads (+ max) |
| 4 | Timeout exception text? | `Connection is not available, request timed out after Xms` |
| 5 | Leak cause? | `Connection`/`ResultSet` not closed on some branch |
| 6 | Leak detector setting? | `leakDetectionThreshold` (e.g., 10s) logs stack of holder |
| 7 | Canonical fix? | try-with-resources: `try(Connection c=ds.getConnection()){...}` |
| 8 | `connectionTimeout` meaning? | Max wait for a pool slot, not query time |
| 9 | `maxLifetime` purpose? | Recycle conns before DB/firewall kills them (e.g., 30min < DB timeout) |
| 10 | `idleTimeout` / `minimumIdle`? | Reclaim idle; keep floor warm to avoid connect storms |
| 11 | p99 cliff at 30s means? | Requests hitting 30s pool timeout — saturated pool |
| 12 | `pg_stat_activity` query? | `SELECT pid,state,now()-query_start,query FROM pg_stat_activity` |
| 13 | `idle in transaction` = ? | Slot held with open txn doing nothing — leak/hold bug |
| 14 | Fleet sizing formula? | `sum(app pools) < db_max × 0.8`; per-pod = budget/pods |
| 15 | Postgres default max_connections? | 100 — easy to oversubscribe with many pods |
| 16 | PgBouncer role? | Multiplex many app conns onto few DB conns (transaction pooling) |
| 17 | Blind pool increase risk? | Crushes DB (more concurrent queries, lock pileup) |
| 18 | Hold-time math? | Held = query + network + app work while conn open — shrink all three |
| 19 | Never hold conn across? | Remote call / queue wait / user think-time |
| 20 | First mitigation? | Restart/drain + kill blocker query + shed load |
| 21 | Kill query command? | `SELECT pg_terminate_backend(pid)` (cancel = `pg_cancel_backend`) |
| 22 | Pending alert? | pending>0 for 5m pages; active>90% 10m warns |
| 23 | Queue cascade? | Pool waiters pin Tomcat threads → web pool exhausts next |
| 24 | Slow-query proof? | `pg_stat_statements` mean/max time + `EXPLAIN ANALYZE` |
| 25 | Long-term prevention? | Close discipline, query SLOs, sizing check in deploy, PgBouncer |
| 26 | Test for leaks? | Soak test asserting idle returns to baseline after load |
| 27 | `minimumIdle` too low causes? | Connect storm on spike — keep small warm floor |
| 28 | Health-check isolation? | Probe must not need pool slot or stuck pool fakes healthy/sick loop |
| 29 | Interview one-liner? | Active≈max+pending, leak stacks vs slow query, size fleet<DB×0.8 |
| 30 | Postmortem artifact? | Pool graphs, leak stack, sizing math, fix + detector test |
