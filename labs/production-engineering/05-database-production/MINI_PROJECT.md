# Lab 05: Databases in Production — Mini Project

## Project: `DbPostmortem` — Reproduce, Diagnose, and Fix Four Production Database Incidents

**Time**: 10–14 hours | **Difficulty**: Advanced | **Stack**: Java 21, JDBC/HikariCP, PostgreSQL (via Testcontainers or Docker), Flyway, `pg_stat_statements`

Build a lab database and a service, then deliberately cause the four incidents that account for most database outages. For each: reproduce it, capture evidence, diagnose from evidence (not memory), fix it, and prove the fix with numbers.

---

## Part 1 — The lab environment

```bash
docker run -d --name lab-pg -e POSTGRES_PASSWORD=lab \
  -p 5432:5432 postgres:16 \
  -c shared_preload_libraries=pg_stat_statements \
  -c log_min_duration_statement=50 \
  -c log_lock_waits=on
docker exec -i lab-pg psql -U postgres -c "CREATE EXTENSION pg_stat_statements;"
```

Service skeleton (JDBC + HikariCP so you control every knob):

```java
public final class DbConfig {
    public static HikariConfig base(String name) {
        var c = new HikariConfig();
        c.setJdbcUrl("jdbc:postgresql://localhost:5432/lab");
        c.setUsername("postgres");
        c.setMaximumPoolSize(20);          // we will deliberately get this wrong
        c.setMinimumIdle(20);              // and this too
        c.setConnectionTimeout(2000);      // fail fast rather than queue forever
        c.setLeakDetectionThreshold(3000); // our leak detector
        c.setPoolName(name);
        return c;
    }
}
```

Seed schema via Flyway (`V1__schema.sql`): `customers`, `orders`, `order_items`, `products`, plus a `hot_spots` table for the lock experiment, and an index deliberately missing on a hot filter column.

---

## Part 2 — Incident 1: the N+1 that looked like a network problem

**Reproduce**: an endpoint that loads an order and then, per item, queries the product:

```java
public List<OrderView> loadOrder(long orderId) {         // N+1 by construction
    Order order = repo.findOrder(orderId);
    return order.items().stream()
            .map(item -> {                                 // one query per item!
                Product p = productRepo.findById(item.productId());
                return new OrderView(item, p);
            })
            .toList();
}
```

**Evidence to capture**:
- `pg_stat_statements` top-20 by `total_exec_time` (not `mean` — this is the trap).
- `SELECT calls, mean_exec_time, total_exec_time FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;`
- Enable `log_min_duration_statement=50` and count query lines per request in the log.
- Application-side timing: total request time vs sum of query time (shows the gap is queries, not network).

**Fix** (single query):
```java
public List<OrderView> loadOrder(long orderId) {
    return jdbc.query("""
        SELECT o.id, i.sku, i.qty, p.name, p.price
        FROM orders o
        JOIN order_items i ON i.order_id = o.id
        JOIN products  p ON p.id = i.product_id
        WHERE o.id = ?
        """, mapper, orderId);
}
```

**Verify**: query count per request drops from `1 + N` to `1`; p99 improves; show the `pg_stat_statements` delta.

Also fix a **keyset pagination** bug in the same exercise (`OFFSET 5000` → `WHERE id > ? ORDER BY id LIMIT ?`) and measure the plan difference with `EXPLAIN (ANALYZE, BUFFERS)`.

---

## Part 3 — Incident 2: pool exhaustion caused by a connection leak

**Reproduce**: a path that opens a connection and returns before closing on an exception:

```java
public Optional<Customer> findCustomer(long id) {
    Connection c = dataSource.getConnection();   // NOT in try-with-resources
    try {
        PreparedStatement ps = c.prepareStatement("SELECT * FROM customers WHERE id = ?");
        ps.setLong(1, id);
        try (ResultSet rs = ps.executeQuery()) { return rs.next() ? Optional.of(map(rs)) : Optional.empty(); }
    } catch (SQLException e) {
        throw new DataAccessException(e);        // connection leaks here
    }
}
```

Drive a load test that includes failures; watch `hikaricp_connections_pending` and `HikariPool` logs (`leak detection stack trace found`).

**Diagnose from evidence**: HikariCP leak-detection stack trace (that is the smoking gun) + `pg_stat_activity` count climbing + `numbackends` climbing in `pg_stat_database`.

**Fix**: try-with-resources everywhere; add a test that asserts the pool returns to idle after the failing path; add a CI grep/ArchUnit rule banning `dataSource.getConnection()` outside a permitted helper.

**Bonus experiment**: prove that raising `maximumPoolSize` from 20 → 100 makes latency *worse* (throughput flat, tail latency up), reinforcing the concurrency cliff.

---

## Part 4 — Incident 3: `FOR UPDATE` without an index (the table lock)

**Reproduce**: a "claim a hot spot" pattern with a missing index:

```java
// NO INDEX on hot_spots.status -> Postgres locks EVERY row while scanning
public boolean claimSpot(long spotId) {
    return jdbc.update("""
        UPDATE hot_spots SET claimed_by = ?, claimed_at = now()
        WHERE id = ? AND status = 'AVAILABLE'
        """, claimant, spotId) == 1;
}
```

Better demonstration of the lock blast radius:
```java
jdbc.query("SELECT id FROM hot_spots WHERE status = 'AVAILABLE' ORDER BY id LIMIT 1 FOR UPDATE", rs -> {});
```
With no index on `status`, this scans and locks the whole table. While that transaction is open, run from another session:
```sql
INSERT INTO hot_spots(...) VALUES (...);   -- blocks
VACUUM hot_spots;                          -- blocks
```

**Evidence**: `pg_locks` showing `tuple` locks on every row / `relation` locks; the blocked `INSERT` in `pg_stat_activity` with `wait_event_type='Lock'`.

**Fix**: add `CREATE INDEX ON hot_spots(status) WHERE status = 'AVAILABLE'` (partial index), and demonstrate the lock footprint collapses. Then re-run and show only 1 row locked.

Also demonstrate the queue-friendly pattern:
```sql
SELECT id FROM hot_spots WHERE status='AVAILABLE' FOR UPDATE SKIP LOCKED LIMIT 10;
```
Run two workers concurrently and show zero blocking.

---

## Part 5 — Incident 4: the long-transaction bloat loop

**Reproduce**: open a long `READ ONLY` transaction in one session (or set `idle_in_transaction_session_timeout` high and leave a transaction open), then in another session churn a table:

```sql
-- session A (long-lived snapshot)
BEGIN;
SELECT count(*) FROM orders;   -- leave open
-- session B
UPDATE orders SET status = 'x' WHERE id % 2 = 0;   -- churn -> dead tuples
DELETE FROM orders WHERE id % 3 = 0;
```

Then inspect:
```sql
SELECT relname, n_dead_tup, n_live_tup, last_autovacuum
FROM pg_stat_user_tables WHERE relname='orders';
```

**Evidence**: `n_dead_tup` climbs, `last_autovacuum` stale; `age(datfrozenxid)` on a churned table rising; index size growing after the churn.

**Fix**: configure `idle_in_transaction_session_timeout` (e.g. 60 s), `statement_timeout`, and `lock_timeout`; add a monitoring query for "longest running transaction." Verify autovacuum now keeps up.

**Bonus**: `REINDEX CONCURRENTLY` on the bloated index vs `pg_repack` and report the lock behavior difference.

---

## Part 6 — Migration rehearsal (expand-contract)

Take a 200M-row equivalent table (generate ~20M locally for time, or use a smaller table and extrapolate timing), and rehearse:

1. **Expand**: `ALTER TABLE t ADD COLUMN new_flag boolean;` (nullable, no rewrite — verify with `pg_class.relfilenode` unchanged).
2. **Add constraint (validated)**: `ALTER TABLE t ADD CONSTRAINT t_new_flag_nn CHECK (new_flag IS NOT NULL) NOT VALID;` then `VALIDATE CONSTRAINT` (concurrent, low lock).
3. **Batched backfill**: a loop of `UPDATE t SET new_flag = true WHERE id BETWEEN ? AND ?` with small batches + sleep, so autovacuum keeps up and no long lock is held.
4. **Enforce**: `ALTER TABLE t ALTER COLUMN new_flag SET NOT NULL;` (fast path via the validated check).
5. **Contract** (later deploy): drop the old column.

**Monitor during every step** (this is the point of the exercise):
```sql
SELECT pid, mode, granted, relation::regclass FROM pg_locks
WHERE relation = 't'::regclass AND NOT granted;
```
Plus a `lock_timeout = '3s'` on the migration session so a blocking attempt fails fast instead of queueing behind peak traffic.

**Deliverable**: `MIGRATION_REHEARSAL.md` with per-step duration, max lock held, and proof that no `ACCESS EXCLUSIVE` blocked for more than ~100 ms.

---

## Part 7 — Read-your-own-writes with a lagged replica

Set up a streaming replica and delay apply (`recovery_min_apply_delay`) to force ~5 s lag. Reproduce the bug: write via primary, read via replica, observe stale.

Then implement sticky-to-primary routing (or a `read-your-writes` token: record the write's LSN/GTID and require the replica to have applied at least that point before serving the read):

```java
public record ReadToken(Long lastAppliedLsn) {}

public Customer read(long id, ReadToken token) {
    if (replicaCaughtUpTo(token.lastAppliedLsn())) return replica.findById(id);
    return primary.findById(id);   // fall back to primary until replica catches up
}
```

**Verify**: the stale-read bug disappears while replica utilization stays high for all *other* traffic.

---

## Acceptance Criteria

- [ ] All four incidents reproduced with captured evidence (query counts, leak stack trace, lock waits, dead tuples).
- [ ] Each fix verified with before/after numbers (latency, query count, lock footprint, `n_dead_tup`).
- [ ] Concurrency-cliff experiment shows throughput flat while latency rises as the pool grows.
- [ ] Migration rehearsal documents per-step lock durations; no blocking lock over ~100 ms.
- [ ] Read-your-writes fix eliminates the stale read against a deliberately lagged replica.
- [ ] `POOL_BUDGET.md` computes pool sizes for a 40-pod fleet against a `max_connections` budget and concludes whether a pooler is required.

---

## Stretch

- Build a `pg_stat_statements`-based "top 10 by total time" report wired into CI to catch regressions.
- Add a chaos toggle that makes the replica stall, verifying the read-your-writes fallback engages correctly.
- Implement a schema-drift check (Flyway validate) in CI and demonstrate it catching an out-of-band change.
