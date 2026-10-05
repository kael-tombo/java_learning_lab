# QUIZ — Slow Query & Deadlock Resolution (15Q)

1. Total-time rank = ? A) calls×mean B) max only C) rows D) cost → **A**
2. Seq Scan on 2M rows with 10 expected means? A) perfect stats B) stale/misestimated stats C) fast D) cached → **B**
3. Non-sargable example? A) `WHERE id=1` B) `WHERE lower(email)=..` C) `WHERE id IN` D) PK lookup → **B**
4. `EXPLAIN ANALYZE` runs? A) plans only B) executes query C) kills txn D) vacuum → **B** (careful on primary)
5. `CREATE INDEX CONCURRENTLY` why? A) faster scan B) avoids write lock C) smaller D) no stats → **B**
6. Postgres deadlock does? A) hangs forever B) aborts one txn automatically C) kills DB D) ignores → **B**
7. App must on `deadlock detected`? A) crash B) idempotent retry w/ backoff C) ignore D) restart DB → **B**
8. Fix for row-order deadlock? A) more conns B) update rows in consistent order C) bigger timeout D) replica → **B**
9. `SELECT FOR UPDATE` risk? A) none B) holds row locks blocking writers C) speeds reads D) skips locks → **B**
10. `log_lock_waits=on` gives? A) query plans B) blocked-wait log lines C) heap dumps D) flames → **B**
11. First mitigation for pinning query? A) more pods B) kill/shed + timeout C) rewrite schema live D) vacuum full → **B**
12. Retry without jitter causes? A) success B) thundering retry collision C) faster D) less load → **B**
13. `statement_timeout` protects? A) pool from endless hold B) disk C) CPU flame D) GC → **A**
14. DDL at peak risks? A) nothing B) AccessExclusive blocks all C) faster D) no locks → **B**
15. Proof DB-bound latency? A) guess B) app p99 tracks DB digest p99 C) CPU flame D) heap dump → **B**

Score: 13–15 expert, 10–12 ready, <10 redo THEORY + EXPLAIN drill.
