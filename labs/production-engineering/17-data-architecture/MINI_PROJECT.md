# Lab 17: Data Architecture & Migration Patterns — Mini Project

## Project: `DataLab` — Migrate a 380M-Row Table Without Downtime, Then Build a Read Model

**Time**: 14–18 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, PostgreSQL 16 (via docker-compose), Flyway or Liquibase, Debezium (optional), Testcontainers, k6, `pg_stat_statements`

Perform a complete schema evolution on a large table under production-shaped load, prove the migration is safe at each step, and then design a CQRS read model with a tested rebuild path.

---

## Part 1 — The schema and the change

```
order-service (Spring Boot 3) → PostgreSQL 16
                                 orders        380M rows, 96 GB with indexes
                                 order_items   1.1B rows, 210 GB (line_items JSONB, avg 1.9 KB)
                                 customers     22M rows
```

```
orders:
  id UUID PRIMARY KEY, customer_id UUID, total_cents BIGINT, currency CHAR(3),
  status VARCHAR(16), created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ
  indexes: idx_orders_customer (customer_id, created_at DESC),
           idx_orders_status (status)          -- unindexed scan on status = the defect
```

The required change, framed as a business request:
- `total_cents` + `currency` → `amount_minor BIGINT` + `currency_code CHAR(3)` (a cross-team naming standardisation).
- New requirement: `fulfilled_at TIMESTAMPTZ` for fulfilment reporting.
- New requirement: line items must no longer be fetched from `order_items` on the list path (they made the table 210 GB).

Everything must happen with no downtime, and `order-service` 4.2.0 must remain rollback-deployable throughout the expand phase.

---

## Part 2 — Baseline and the dangerous inventory

### 2.1 Measure the table

```sql
SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) AS total,
       n_live_tup, n_dead_tup
FROM pg_stat_user_tables WHERE relname IN ('orders','order_items','customers');

SELECT count(*) FROM orders;   -- 380,000,000
```

### 2.2 Establish the load profile

```bash
k6 run -e RATE=4000 -e DURATION=30m orders.js    # 4,000 writes/s + 4,000 reads/s
```

Watch: `pg_stat_activity` count, `pg_locks` waiters, replication lag (`pg_stat_replication`), and application p99.

### 2.3 Inventory the current migrations and classify them

For each existing migration file:

| Migration | Statement | Lock type | Duration (estimated from table size) | Safe with old code deployed? | Verdict |
|---|---|---|---|---|---|
| V12 | `ALTER TABLE orders ALTER COLUMN currency TYPE VARCHAR(8)` | ACCESS EXCLUSIVE + rewrite | ~540 s | yes (widening) | dangerous: 9 min lock |
| V19 | `ALTER TABLE orders RENAME COLUMN total_cents TO total` | brief | instant | **no** | dangerous: breaks old code |
| V27 | `CREATE INDEX idx_orders_status ON orders(status)` | SHARE (blocks writes) | ~90 s | yes | dangerous: blocks writes |
| | | | | | |

**Deliverable**: `MIGRATION_INVENTORY.md` — every migration classified, with the lock type and the duration computed from the table size, ranked by risk, and with a remediation plan for the top three.

---

## Part 3 — The wrong migrations (demonstrate the failure first)

### 3.1 The rename

```sql
-- WRONG. Do this on purpose, on a copy, and measure.
ALTER TABLE orders RENAME COLUMN total_cents TO total;
```

Observe: the *running* application starts failing with `column "total_cents" does not exist` immediately, on pods that have not restarted. Then try to roll back — the previous version also expects `total_cents`. Record the outage duration and the rollback failure.

### 3.2 The blocking index

```sql
-- WRONG. Run on a copy and measure the blocked-query count.
SET lock_timeout = '30s';   -- still long enough to hurt
CREATE INDEX idx_orders_status ON orders (status);
```

Measure `pg_stat_activity` waiters during the 90-second build.

### 3.3 The constraint that scans

```sql
-- WRONG
ALTER TABLE orders ADD CONSTRAINT chk_currency CHECK (currency IN ('USD','EUR','GBP'));
```

Measure the blocked-write count over the scan.

**Deliverable**: `WRONG_MIGRATIONS.md` — the three experiments with measured blocked queries, application errors, and recovery time.

---

## Part 4 — The right migrations

### 4.1 Expand (Release A)

```sql
-- V30__expand_amount_columns.sql
SET lock_timeout = '3s';
SET statement_timeout = '60s';

-- 1. Additive, nullable, metadata-only. Instant.
ALTER TABLE orders ADD COLUMN amount_minor BIGINT;
ALTER TABLE orders ADD COLUMN currency_code CHAR(3);
ALTER TABLE orders ADD COLUMN fulfilled_at TIMESTAMPTZ;

-- 2. Composite index covering the list path, built without blocking writes.
--    NOTE: CREATE INDEX CONCURRENTLY cannot run inside a transaction block.
SET lock_timeout = '0';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status_created
  ON orders (status, created_at DESC);
SET lock_timeout = '3s';

-- 3. Constraint added without scanning, then validated without blocking writes.
ALTER TABLE orders ADD CONSTRAINT chk_currency_code
  CHECK (currency_code IS NULL OR currency_code IN ('USD','EUR','GBP')) NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT chk_currency_code;
```

Verify after each statement:
```sql
SELECT * FROM pg_stat_activity WHERE wait_event_type = 'Lock';   -- should stay empty
```

And verify no `INVALID` index was left behind:
```sql
SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE NOT indisvalid;
```

### 4.2 Dual-write

```java
@Repository
class OrderWriteRepository {

    /**
     * Writes BOTH shapes in one transaction so the previous release (which only knows
     * total_cents/currency) keeps working, and so rollback is still valid.
     */
    @Modifying
    @Query(value = """
        INSERT INTO orders (id, customer_id, total_cents, currency, amount_minor, currency_code, status)
        VALUES (:id, :customerId, :cents, :currency, :minor, :code, :status)
        """, nativeQuery = true)
    int insertDual(@Param("id") UUID id, @Param("customerId") UUID customerId,
                   @Param("cents") long cents, @Param("currency") String currency,
                   @Param("minor") long minor, @Param("code") String code,
                   @Param("status") String status);

    @Modifying
    @Query("""
        update Order o set o.totalCents = :cents, o.amountMinor = :cents,
               o.currency = :currency, o.currencyCode = :code
        where o.id = :id
        """)
    int updateAmountBoth(@Param("id") UUID id, @Param("cents") long cents,
                         @Param("currency") String currency, @Param("code") String code);
}
```

### 4.3 Backfill as a resumable, lag-guarded job

```java
@Component
@RequiredArgsConstructor
class BackfillJob {
    private static final int BATCH = 5_000;

    @Scheduled(fixedDelayString = "${backfill.delay-ms:500}")
    @Transactional
    public void runBatch() {
        if (lagGuard.exceedsThreshold()) { metrics.counter("backfill.paused.lag").increment(); return; }

        List<UUID> ids = jdbc.queryForList("""
            SELECT id FROM orders
            WHERE amount_minor IS NULL AND id > :highWater
            ORDER BY id LIMIT :batch
            """, Map.of("highWater", highWater, "batch", BATCH), UUID.class);

        if (ids.isEmpty()) { metrics.counter("backfill.complete").increment(); return; }

        int updated = jdbc.update("""
            UPDATE orders SET amount_minor = total_cents, currency_code = currency
            WHERE id = ANY(:ids) AND amount_minor IS NULL
            """, Map.of("ids", ids.toArray(new UUID[0])));
        highWater = ids.get(ids.size() - 1);          // resumable
        progress.mark(highWater, updated);
    }
}
```

```java
@Component
class ReplicaLagGuard {
    boolean exceedsThreshold() {
        Long lagSeconds = jdbc.queryForObject(
            "SELECT EXTRACT(EPOCH FROM now() - replay_lsn) FROM pg_stat_replication LIMIT 1", Long.class);
        if (lagSeconds == null) return false;
        return lagSeconds > lagThresholdSeconds;       // e.g. 30 s
    }
}
```

Run it under the k6 load and record: throughput, duration, replication lag over time, and the number of times the guard paused it.

**Compute before you run**:
```
throughput = 5,000 / (0.24 s txn + 0.26 s pause) = 10,000 rows/s
duration   = 380,000,000 / 10,000 = 38,000 s = 10.6 h
```
State that number in the plan, then measure and compare.

### 4.4 Switch reads (Release B)

```java
@Query("select o.id, o.amountMinor as amount, o.currencyCode as currencyCode " +
       "from Order o where o.customerId = :cid order by o.createdAt desc")
List<OrderSummary> listForCustomer(...);
```

Keep the dual write for one more release. `Release A` remains rollback-deployable throughout.

**Deliverable**: `MIGRATION_REPORT.md` — the expand DDL with the lock measurements, the backfill rate and duration versus the predicted value, the replication-lag curve, the guard's pauses, and the read-switch verification (results identical for all rows where both columns are populated).

---

## Part 5 — Vertical partition the 210 GB table

Move `line_items` out of `order_items` into a table keyed by `order_id`, so the list path stops touching it.

```sql
SET lock_timeout = '3s';
-- Metadata-only: rewrite the primary key.
ALTER TABLE order_items DROP CONSTRAINT order_items_pkey;
ALTER TABLE order_items ADD PRIMARY KEY (order_id, item_index);   -- brief lock
```

```java
@Query("select new ItemDto(i.itemIndex, i.sku, i.quantity, i.unitPrice) " +
       "from OrderItem i where i.orderId = :oid")
List<ItemDto> itemsForOrder(@Param("oid") UUID oid);
```

Measure the before/after on the list and detail endpoints:
```
before: list endpoint reads 1.9 KB of JSONB per row → 380M × 2 page reads
after:  list endpoint never touches order_items; detail endpoint reads only the relevant order
```
Report the p99 and the I/O change, and the total size change.

**Deliverable**: `VERTICAL_PARTITION.md` — the DDL, the lock measurements, the endpoint I/O before/after, and the size change.

---

## Part 6 — A CQRS read model with a tested rebuild

### 6.1 The query that justifies it

"Customer order summary with item count and total, for the last 90 days, ordered by recency" — currently a 4-table join over 380M rows that takes 8 seconds.

### 6.2 The projection

```java
@Component
class OrderSummaryProjection {
    // Consumes from the outbox/Kafka topic; upserts into the read model.
    @Transactional
    void on(OrderCreated e) {
        projection.upsert(e.orderId(), e.customerId(), e.amountMinor(), e.currencyCode(),
                          e.itemCount(), e.occurredAt());
        lagGauge.set(Duration.between(e.occurredAt(), now()).toMillis());
    }
}
```

```sql
CREATE TABLE order_summary (
  order_id UUID PRIMARY KEY, customer_id UUID NOT NULL, amount_minor BIGINT,
  currency_code CHAR(3), item_count INT NOT NULL, occurred_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_summary_customer ON order_summary (customer_id, occurred_at DESC);
```

### 6.3 The freshness SLO and the lag alert

```yaml
- alert: ProjectionLagHigh
  expr: histogram_quantile(0.99, projection_lag_milliseconds_bucket) > 5000     # SLO: p99 < 5 s
  for: 2m
- alert: ProjectionLagWillExceedRetention
  expr: projection_lag_seconds > kafka_topic_retention_seconds * 0.5
  for: 5m
  annotations:
    summary: "Projection lag is halfway to data loss; the projection cannot catch up from retention."
```

### 6.4 Test the rebuild path (the part everyone skips)

```bash
# Full projection rebuild from the event log into an empty read model
./rebuild-projection.sh --from 2026-01-01 --into order_summary_rebuild --parallel 8
```

Then verify:
```sql
-- Row-by-row comparison between the incremental projection and the rebuilt one
SELECT count(*) FROM (
  (SELECT * FROM order_summary EXCEPT SELECT * FROM order_summary_rebuild)
  UNION ALL
  (SELECT * FROM order_summary_rebuild EXCEPT SELECT * FROM order_summary)
) diff;
```
Must be zero. Time it — this is the number you will need if you ever have to rebuild.

**Deliverable**: `CQRS_DESIGN.md` — the query that justified it, the projection, the freshness SLO, the alert, the rebuild time, and the zero-diff verification.

---

## Part 7 — Migration CI checks

```bash
#!/usr/bin/env bash
# ./check-migrations.sh db/migration
set -euo pipefail
DIR=${1:-db/migration}; fail=0

for f in "$DIR"/*.sql; do
  # 1. lock_timeout must be set
  grep -q 'lock_timeout' "$f" || { echo "FAIL: $f sets no lock_timeout"; fail=1; }

  # 2. no full-rewrite DDL in a migration that ships with old code deployed
  if grep -qiE 'ALTER COLUMN .* TYPE|ADD COLUMN .*NOT NULL DEFAULT' "$f"; then
    grep -q 'REQUIRES-NO-DOWNTIME' "$f" || { echo "FAIL: $f may rewrite the table and lacks the downtime marker"; fail=1; }
  fi

  # 3. no rename/drop of a column referenced in application code
  grep -qiE 'RENAME COLUMN|DROP COLUMN' "$f" && \
    { echo "FAIL: $f renames or drops a column; use expand-contract"; fail=1; }

  # 4. indexes must be concurrent
  grep -q 'CREATE INDEX ' "$f" && ! grep -q 'CONCURRENTLY' "$f" && \
    { echo "FAIL: $f creates a non-concurrent index"; fail=1; }

  # 5. constraints must be added NOT VALID then validated
  grep -q 'ADD CONSTRAINT' "$f" && ! grep -q 'NOT VALID' "$f" && \
    { echo "FAIL: $f adds a validating constraint on a large table"; fail=1; }
done
exit $fail
```

**Acceptance**: five deliberately bad migrations each fail with a specific message, and the good ones pass.

---

## Part 8 — Erasure propagation

Design (and partially implement) the erasure path for one subject:

```java
@Service
class ErasureService {
    /** Erasure is asynchronous with a receipt per surface; we only claim completion when all are in. */
    public ErasureTicket requestErasure(String subjectId) {
        var ticket = tickets.open(subjectId);
        outbox.insert(subjectId, "SubjectErasureRequested", payload, Map.of("ticketId", ticket.id()));
        return ticket;
    }

    @Transactional
    void handle(SubjectErasureRequested e) {
        orders.eraseSubject(e.subjectId());          // 380M-row table: DELETE ... USING customers
        outbox.insert(e.subjectId(), "SubjectErasedFromPrimary", ...);
    }
}
```

Enumerate the surfaces: primary, read replicas, cache, search index, analytics warehouse, log archives, exports, backups. For each: mechanism, expected propagation time, and how you confirm it.

```markdown
| Surface | Mechanism | Propagation time | Confirmation |
|---|---|---|---|
| orders (primary) | DELETE ... USING customers, indexed | seconds | row count query |
| read replica | physical replication | seconds | lag = 0 + query |
| Redis customer cache | key pattern delete + TTL | minutes | SCAN + DEL report |
| search index | delete-by-query | minutes–tens of minutes | index doc count |
| analytics | batch pipeline skip + tombstone | hours | pipeline watermark |
| logs | retention-based | days | policy acknowledgement |
| backups | policy-based | 30–90 days | documented legal basis |
```

**Deliverable**: `ERASURE_PLAN.md` — the table, the coverage arithmetic at 1 hour and at 24 hours, and the honest statement of what you can tell the requester and when.

---

## Acceptance Criteria

- [ ] `MIGRATION_INVENTORY.md` classifies every existing migration with lock type, estimated duration, and a remediation plan.
- [ ] `WRONG_MIGRATIONS.md` documents three reproduced failures with measured blocked queries and application errors.
- [ ] `MIGRATION_REPORT.md`: expand DDL with zero blocked writes under 4,000 writes/s; backfill rate and duration measured against the predicted 10.6 h; replication lag curve and guard pauses; read-switch verified identical.
- [ ] Compatibility matrix filled in for every release in the sequence, with the drop date computed.
- [ ] `VERTICAL_PARTITION.md`: the 210 GB table restructured, endpoint I/O and p99 before/after measured.
- [ ] `CQRS_DESIGN.md`: read model with a freshness SLO, a lag alert, a measured rebuild time, and a zero-diff rebuild verification.
- [ ] `ERASURE_PLAN.md` with per-surface propagation and coverage arithmetic.
- [ ] `check-migrations.sh` blocks all five bad migrations.

---

## Stretch

- Add a `NOT VALID` constraint migration and measure the blocked-write count against the blocking form under load.
- Build the read model from Debezium CDC instead of the outbox, and compare projection lag against the outbox relay.
- Implement cryptographic erasure (per-subject key encryption) and demonstrate that deleting the key makes the PII unreadable without rewriting the log.
- Write a migration that converts `orders` from `CHAR(3)` to a lookup-table `currency_id` with a foreign key — the hardest version of expand-contract — and time it.
