# Lab 05: Databases in Production — Flashcards

~60 cards. Every answer is a number, a setting, or a rule.

---

## Pool Sizing

Q: Postgres `max_connections` is per-database across the whole cluster; why does that force small per-pod pools?
A: 30 pods × pool 50 = 1500 connections; each session is a process with memory, and contention collapses past the DB's CPU capacity. Budget total connections, not per-pod.

Q: Rule of thumb starting pool size for a Postgres primary on ~4 cores?
A: `cores × 2 + effective_spindles` ≈ 8–20 per instance, total under ~30–50 per DB before a pgbouncer.

Q: Why is a huge pool counter-productive?
A: Throughput peaks at moderate concurrency then inverts (context switches, lock waits, planner CPU). More threads ≠ more throughput.

Q: What does HikariCP `minimumIdle` control?
A: The floor of idle connections kept open; setting it equal to `maximumPoolSize` wastes DB connections.

Q: `connectionTimeout` vs `validationTimeout`?
A: How long the pool waits for a free connection (fail fast) vs how long a validation query may take. Keep validation well under connectionTimeout.

Q: `maxLifetime` vs `idleTimeout`?
A: Hard retirement age of a connection (must be shorter than upstream idle-kill) vs how long an idle connection may linger.

Q: Why do many pods × many pools exhaust `max_connections`?
A: Each pod opens its own pool and connections are not shared. That's what pgbouncer (transaction pooling) or a sidecar solves.

Q: What is a `leakDetectionThreshold`?
A: Logs a stack trace when a connection is held longer than the threshold — the single best tool for finding connection leaks.

Q: Transaction pooling vs session pooling?
A: Transaction pooling multiplexes many logical sessions onto few physical connections (breaks session state like temp tables/`SET`); session pooling is safer but uses more real connections.

Q: Statement caching (prepared statements) with pgbouncer transaction mode?
A: Requires care — transaction pooling can invalidate per-connection prepared-statement state; use PgBouncer's `max_prepared_statements` support or disable server-side prepare.

---

## Queries, Indexes, Plans

Q: Read an `EXPLAIN (ANALYZE, BUFFERS)` output's key columns?
A: Actual vs estimated rows (big skew = stale stats/misestimate), loops, and buffers (hit vs read) to see I/O.

Q: Estimate-vs-actual row mismatch is the #1 cause of what?
A: Bad join order / wrong plan. Fix with better stats (`ANALYZE`, extended stats, `CREATE STATISTICS`) or a query rewrite.

Q: What causes a sequential scan on a filtered large table?
A: Low selectivity combined with a missing/partial index, a type mismatch defeating the index, or a function-wrapped column (`WHERE date(created_at) = ...`) making the index unusable.

Q: Function-wrapped column fix?
A: Expression index (`CREATE INDEX ON t (date(created_at))`) or, better, rewrite as a range (`created_at >= d AND created_at < d+1`) to stay sargable.

Q: Index-only scans need what?
A: A covering index (`INCLUDE (...)`) and a recently vacuumed visibility map, else it still hits the heap.

Q: Why does adding an index sometimes slow writes?
A: Every insert/update must maintain it; on write-heavy tables an index can cost more than it saves. Measure.

Q: Partial index use case?
A: Hot subset of a large table (e.g. `WHERE deleted_at IS NULL` or only recent rows) — much smaller and faster.

Q: Covering index benefit?
A: Index-only scan, fewer heap fetches → often a bigger win than adding another column to the table.

Q: What is index bloat and its symptom?
A: Dead tuples accumulate in indexes after churn; lookups scan more pages → slower reads, wasted cache.

Q: When to REINDEX vs pg_repack?
A: `REINDEX CONCURRENTLY` for a quick fix with a brief lock; `pg_repack` online with more overhead; schedule both as maintenance, not ad hoc.

---

## Transactions & Locking

Q: Default Postgres isolation level?
A: `READ COMMITTED` (each statement sees a fresh snapshot). MySQL InnoDB default is `REPEATABLE READ`.

Q: What does `SELECT ... FOR UPDATE` lock?
A: The selected rows (and in Postgres, every row it scans without an index).

Q: Missing index on a `FOR UPDATE` filter → what happens?
A: Full table row lock: serializes all writers and blocks vacuum. Always index the filter.

Q: Long `READ ONLY` transaction danger?
A: Pins a snapshot → blocks vacuum reclaim of dead tuples → bloat → slower everything → more long transactions. The poison loop.

Q: What causes lock queues to cascade?
A: A long holder makes waiters queue; those waiters hold connections; pool exhausts; new requests wait; a single slow query becomes an outage.

Q: `NOWAIT` vs `SKIP LOCKED`?
A: `NOWAIT` errors immediately if locked; `SKIP LOCKED` skips locked rows and returns fewer — ideal for queue/worker tables to avoid contention.

Q: Deadlock avoidance rule?
A: Consistent lock ordering everywhere; or for queues, `FOR UPDATE SKIP LOCKED` so workers never block each other.

Q: `idle_in_transaction_session_timeout` prevents what?
A: Sessions that opened a transaction and never committed/rolled back (usually an exception path) — holding locks/snapshots forever.

Q: `statement_timeout` prevents what?
A: A single runaway query holding locks/CPU and blocking vacuum.

Q: Connection leak vs pool exhaustion — the real cause?
A: Connections checked out and not returned: unclosed `ResultSet`/`Statement`, missing try-with-resources, missing commit/rollback, or a slow query holding them.

---

## Long Transactions & Vacuum

Q: What does a long transaction block?
A: Vacuum cleanup of dead tuples that the transaction's snapshot can still "see," leading to bloat and wraparound risk.

Q: Autovacuum's job?
A: Reclaim dead tuples, update the visibility map, and keep stats/statistics fresh — automatically, based on thresholds.

Q: When does autovacuum fall behind?
A: Very high churn, many long-lived snapshots/transactions, aggressive long-running replicas/readers, or under-tuned per-table thresholds.

Q: What is XID wraparound and why fear it?
A: Transaction IDs wrap after ~2^32; vacuum delay can push a DB toward rewrapping every row (extreme corruption/emergency mode). Monitor `age(datfrozenxid)`.

Q: Symptom of a vacuum-starved table?
A: Bloat (table and index much larger than data), slow index scans, growing "dead tuples" in `pg_stat_user_tables`.

---

## Replication & Reads

Q: Streaming replication is what kind of sync?
A: Async by default — the primary commits without waiting; replica may lag or (on failure) lose recent writes.

Q: Replication lag causes which user bug?
A: Read-your-own-write violations — user sees stale data right after a write routed to a lagging replica.

Q: Fix read-your-own-writes without abandoning replicas?
A: Route the writer's session to the primary (sticky), or pass a "read version >= my write" token so the replica waits for a minimum applied LSN/GTID.

Q: Why can a hot replica be a stale replica?
A: Lag grows when the replica can't apply fast enough; sending more reads can increase WAL/network pressure and worsen lag.

Q: Split-brain risk when promoting a replica?
A: Old primary may still accept writes → divergence; requires fencing (STONITH, `recovery.conf`/timeline discipline, or managed failover) to prevent two writers.

Q: Read replicas don't help which workload?
A: Write-heavy (replicas add WAL apply load) and read-after-write-heavy unless you solve staleness explicitly.

---

## Migrations

Q: Safe pattern for adding a `NOT NULL` column to a huge table?
A: Add nullable → backfill in batches → add validated `CHECK` → `SET NOT NULL` (fast path) → optionally drop the check. Avoid one giant `ALTER` holding `ACCESS EXCLUSIVE`.

Q: Why can `ADD COLUMN ... DEFAULT` be safe in modern PG?
A: PG 11+ stores a "missing" default without rewriting the table when the default is constant. Verify version and whether the default is truly constant/volatile.

Q: Dangerous migration pattern?
A: `ALTER TABLE` that takes `ACCESS EXCLUSIVE` on a huge table while it scans/rewrites — blocks all reads/writes for the duration. Use `CONCURRENTLY` (index builds, some ops) or batch.

Q: How to deploy a schema change with old + new app versions running?
A: Expand-contract: add the new column/table (backward compatible), deploy code writing both, backfill, switch reads, then contract (drop old). Never rename in one step.

Q: What is a "lock queue" during a migration?
A: The migration holds a brief lock; queued queries pile up and time out after, causing a thundering herd once the lock releases.

Q: Zero-downtime index build?
A: `CREATE INDEX CONCURRENTLY` (slower, non-blocking) — but it takes two table scans and can leave an invalid index on failure (`IF NOT EXISTS`, then validate).

Q: Rollback story for a migration?
A: Every migration must have a tested rollback OR be forward-only with a documented compensating migration. "It's additive, we can't roll back the data" is a real answer.

---

## Patterns & Anti-Patterns

Q: Check-then-insert race → fix?
A: `INSERT ... ON CONFLICT DO UPDATE` (atomic upsert) or catch the unique violation and re-read.

Q: N+1 query fix?
A: Join, or batch-load with `WHERE id = ANY(?)` / bounded `IN (...)`, or DataLoader-style per-request batching.

Q: `SELECT *` anti-pattern?
A: Fetches unused columns (I/O + memory), defeats covering indexes, and couples the schema to your DTO.

Q: Offset pagination anti-pattern at depth?
A: `OFFSET 100000` makes the DB generate and discard 100k rows — `O(offset)`. Use keyset/seek pagination (`WHERE id > last_id ORDER BY id LIMIT n`).

Q: Why batch writes in chunks (e.g. multi-row `INSERT`)?
A: Fewer round trips and less per-statement overhead; batch size tuned to avoid huge locks/memory spikes (a few hundred to a few thousand rows).

Q: Prefer `ON CONFLICT` over application-level dedupe table?
A: One atomic operation, no extra table, no race, and fewer writes.

Q: Soft delete anti-pattern?
A: Adds a predicate to every query and hurts index usage/planning; prefer real deletes (or a status column you *always* filter with a partial index) unless history is required.

Q: Two-phase "read your writes" via session variable?
A: Setting `SET TRANSACTION ISOLATION` or a hint var on a pooled connection leaks state to the next borrower unless reset — the classic pooled-connection state bug.

Q: Sharding the DB when?
A: When a single instance's write throughput/storage ceiling is reached and you've already tuned and added replicas. Sharding is a last resort with the highest operational cost.

---

## Diagnostics

Q: First three queries when the DB is slow?
A: `pg_stat_activity` (what's running/waiting), `pg_locks` (who blocks whom), and slow-query log / `pg_stat_statements` (which statements and how much total time).

Q: `pg_stat_statements` gives you?
A: Per-statement call count, total/mean time, rows, and shared block hits/reads — the "top offenders by total time" tool (mean-only sorting hides the real problem).

Q: `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)` shows?
A: Actual plan with real timings, per-node row counts vs estimates, and buffer I/O (shared hit = cached, read = disk).

Q: Detect a missing index via logs?
A: Slow-query log lines with high "rows examined vs returned" ratio.

Q: What does `SELECT ... FOR UPDATE` on a non-existent row do under concurrency?
A: Nothing to lock, so concurrent inserts can both succeed — use a unique constraint + upsert/retry to make "insert if absent" atomic.

Q: Detect connection churn?
A: `pg_stat_database` `numbackends`, connection log rate, and pool metrics (`connections_created_total`).

Q: CPU-bound vs IO-bound DB?
A: `pg_stat_activity.wait_event_type` (`IO` vs `Lock` vs `Client` vs none) plus buffer hit ratio and disk latency.

Q: Detect a runaway autovacuum on a big table?
A: `pg_stat_progress_vacuum` and `pg_stat_activity` showing the autovacuum worker with `relid` and phase.

Q: What does `EXPLAIN` without `ANALYZE` tell you?
A: The *planned* plan — great for seeing index options, but it does not execute, so it can be misleading under skew. Always pair with `ANALYZE`.

---

## Operations

Q: Statement vs transaction vs idle-in-transaction timeouts — set all three?
A: Yes. Each catches a different runaway (long query, long transaction, abandoned session).

Q: Why alert on connection count, not just query latency?
A: Connection saturation is usually the earliest signal; latency is the lagging symptom.

Q: What's a safe autovacuum/ANALYZE policy for a high-churn table?
A: Lower `autovacuum_vacuum_scale_factor`/`analyze_scale_factor` and/or per-table thresholds so vacuum keeps up with churn rather than running rarely and hugely.

Q: Backups: what actually matters?
A: Tested restores (a backup you never restored is a hope), PITR via WAL archiving with retention matched to your RPO, and offsite/immutable copies.

Q: Failover RTO vs replica promotion time?
A: Promotion is fast; the risk is *divergence* and app reconnection. Fencing and connection-refresh behavior dominate real RTO.

Q: Read/write splitting gotcha?
A: Clock/timing: a request that writes then reads may cross the split. Sticky sessions to the writer for a short window fixes it.

Q: Cache invalidation from the DB side — options?
A: Logical decoding (CDC) → cache buster, periodic short TTL, or explicit invalidation on write. Pick based on staleness tolerance.
