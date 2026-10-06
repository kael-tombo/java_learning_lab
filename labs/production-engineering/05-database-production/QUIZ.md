# Lab 05: Databases in Production — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. Why is a `SELECT` without a predicate on a large table dangerous even with an index elsewhere?**
- A) It uses CPU
- B) It forces a sequential scan of the whole relation and may hold locks / bloat vacuum / long shared locks as the heap grows
- C) It is slow to parse
- D) It cannot use the connection pool

**Answer: B** — A full scan is `O(n)` and holds an `ACCESS SHARE` lock for the duration, blocking `VACUUM FULL` and blocking schema changes. On a hot path this becomes an availability event.

---

**Q2. Connection pool size: why is "bigger is safer" wrong for a database?**
- A) Databases have no connection limit
- B) Concurrency is bounded by the DB's CPU/storage, not by client threads; excessive connections cause lock contention, context switches, and memory pressure per session, reducing throughput while increasing latency
- C) JDBC drivers cap connections
- D) Pools cannot exceed 100 connections

**Answer: B** — Throughput peaks and then *inverts* past a certain concurrency (see "the concurrency cliff" in MATH_FOUNDATION). A pool of 200 against a 4-core DB usually delivers less throughput than a pool of 20.

---

**Q3. `SELECT ... FOR UPDATE` without an index on the filter column causes what?**
- A) Nothing
- B) A full-table row lock — every row is locked, serializing all writers and blocking `INSERT`/`VACUUM`
- C) An error
- D) A deadlock automatically

**Answer: B** — PostgreSQL locks rows as it scans; without an index, that is every row. This is a classic production foot-gun in "check-then-insert" patterns.

---

**Q4. N+1 queries: the pattern and the fix?**
- A) One query per call layer; fix with a join, a `JOIN ... USING`/batched `IN`, or a DataLoader-style batcher
- B) A single query per table; fix with an index
- C) A query per connection; fix with pooling
- D) Nested transactions; fix with savepoints

**Answer: A** — The tell is a per-row query count in slow-query logs; the fix is batching (`WHERE id = ANY(?)` or an in-clause with a bounded tuple count).

---

**Q5. What does connection pool `maxLifetime` / `maxIdle` actually protect against?**
- A) Memory only
- B) Stale connections killed by a firewall/DB restart/pgbouncer restart, and idle-connection exhaustion across many instances
- C) SQL injection
- D) Transaction leaks

**Answer: B** — Long-lived idle connections get silently dropped by NAT/firewalls/DB failover; the pool must recycle them below the upstream idle timeout and cap idle count so many pods don't collectively exhaust the DB's `max_connections`.

---

**Q6. Read replica lag causes which concrete user-visible bug?**
- A) Higher write latency only
- B) Read-your-own-write violations — a user updates then immediately reads from a lagging replica and sees stale data
- C) Data loss on the primary
- D) Deadlocks

**Answer: B** — The classic "I just saved my profile but it's gone" bug. Fix with read-your-writes routing (sticky to primary, or a "min version" token) rather than giving up on replicas.

---

**Q7. Why is a long-running transaction in Postgres dangerous even if it's `READ ONLY`?**
- A) It blocks all reads
- B) It pins the transaction's snapshot, preventing `VACUUM` from reclaiming dead tuples and causing table/index bloat and eventually wraparound pressure
- C) It increases replication lag
- D) It locks the table in `ACCESS EXCLUSIVE` mode

**Answer: B** — Old snapshots block vacuum cleanup → bloat → slower queries → more CPU → more long transactions. This is the "long transaction poisons the whole DB" loop.

---

**Q8. What is the difference between statement and transaction timeouts, and why set both?**
- A) They're identical
- B) Statement timeout bounds one query; `idle_in_transaction_session_timeout`/lock timeout bounds idle time — together they prevent runaway statements and runaway idle sessions from holding locks/snapshots
- C) Transaction timeout is a performance hint
- D) Only one is supported

**Answer: B** — Many production incidents are "one session left a transaction open on an exception and nothing was ever committed or rolled back." Both timeouts are cheap insurance.

---

**Q9. When is a database the wrong place for a business invariant?**
- A) Never — the DB should enforce all invariants
- B) When enforcing it requires a cross-row/cross-table distributed lock or a global counter at scale; keep hot-path correctness in the application/queue and use the DB for single-row atomicity
- C) When the DB is not relational
- D) Always — enforce only in the app

**Answer: B** — Databases are excellent for single-row/per-transaction invariants and terrible for cross-shard coordination at scale. Push invariants to where the data is co-located.

---

**Q10. What is connection-pool exhaustion with 100% idle-looking threads usually?**
- A) Too small a pool
- B) Connections checked out and not returned — leaked result sets/streams, missing commit/rollback, slow queries holding connections, or a transaction opened and never closed
- C) Too large a pool
- D) DNS failure

**Answer: B** — "Pool exhausted" almost always means leaked or long-held connections, not "the pool is too small." Increasing size is a way to delay the same outage.

---

**Q11. What is index bloat and why does it matter?**
- A) Index pages are defragmented
- B) Deleted/updated rows leave dead tuples in indexes; over time index lookups scan more pages → slower reads and more I/O, plus wasted memory
- C) Indexes grow too small
- D) The planner ignores indexes

**Answer: B** — Bloat is why autovacuum matters and why `REINDEX`/`pg_repack` shows up in runbooks after heavy churn.

---

**Q12. Why prefer `INSERT ... ON CONFLICT DO UPDATE` (upsert) over check-then-insert?**
- A) It's shorter
- B) It's a single atomic statement, avoiding a TOCTOU race and a unique-violation retry storm under concurrency
- C) It bypasses constraints
- D) It's faster by 10x always

**Answer: B** — Check-then-insert races under concurrency: two transactions both see "not present" then one gets a unique violation, forcing retries that amplify load exactly during contention.

---

**Q13. What does statement-level `SERIALIZABLE` cost vs `READ COMMITTED` in a write-heavy system?**
- A) Nothing
- B) Serializable detects conflicts and aborts transactions (serialization failures) that must be retried — correctness for higher, but retries add load and can livelock under hot rows
- C) Serializable is read-only
- D) Serializable is faster under contention

**Answer: B** — `READ COMMITTED` + unique constraints + explicit locks is usually the pragmatic sweet spot; reserve `SERIALIZABLE` (or explicit advisory/row locks) for the few invariants that need it, and always handle the retry.

---

**Q14. A migration that adds a `NOT NULL` column with a default to a 200M-row table: the safe pattern is?**
- A) One `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT ...` and hope
- B) Add the column nullable, backfill in batches, then `SET NOT NULL` (ideally with a validated `CHECK` constraint first), to avoid a long `ACCESS EXCLUSIVE` lock and a huge single transaction
- C) Drop and recreate the table
- D) Do it during peak for less contention

**Answer: B** — PG 11+ can use a fast default (no rewrite), but `SET NOT NULL` still needs a full scan unless a valid `CHECK (col IS NOT NULL)` constraint exists. The batched pattern keeps locks short.

---

**Q15. Which single DB metric do you alert on first?**
- A) Slow query count
- B) Connection count vs limit and connection wait time (pool acquisition), because almost every DB incident shows here first
- C) Table size
- D) Replication lag only

**Answer: B** — Connections-in-use approaching `max_connections`, or pool acquisition wait spiking, is the earliest reliable signal of a DB-bound incident.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT + the real-world migration plan.
- 12–10: revisit pool sizing, locking, and long-transaction sections in THEORY.
- <10: redo EXERCISES 3–7 cold, retake in 48 hours.
