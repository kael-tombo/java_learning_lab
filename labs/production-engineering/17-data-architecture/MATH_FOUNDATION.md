# Lab 17: Data Architecture & Migration Patterns — Math Foundation

Migrations fail on time: lock duration, queue growth, backfill rate, and the window during which rollback must remain available. All four are arithmetic.

---

## 1. Lock duration and queue growth

```
blocked_queries = arrival_rate × lock_duration
pool_exhaustion_time = pool_size / arrival_rate
user_impact_time    = pool_size / arrival_rate   (each pooled connection blocks on the lock)
```

`ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT 0` on a 380M-row PostgreSQL table, rewrite takes 9 minutes:
```
arrival_rate = 4,000 writes/s;  lock = 540 s
queued queries = 4,000 × 540 = 2,160,000
pool_size = 200  →  every pooled connection blocks within 200/4,000 = 0.05 s
user-visible impact starts at ~0.05 s, not at 540 s
```

**Conclusion**: the outage begins almost immediately; the DDL duration only determines how long it lasts. This is why the fix is `lock_timeout`, not patience:

```
lock_timeout = '3s'  →  DDL aborts in 3 s; queued queries ≈ 12,000 for one attempt; no sustained outage
```

---

## 2. Which DDL is safe: metadata-only versus rewrite

| Operation | Lock | Duration driver |
|---|---|---|
| `ADD COLUMN` (nullable, no default) | brief `ACCESS EXCLUSIVE` | instant (catalog only) |
| `ADD COLUMN ... DEFAULT <constant>` | brief (metadata-only in modern PG) | instant — verify for your version |
| `ADD COLUMN ... DEFAULT <volatile>` | `ACCESS EXCLUSIVE` | full rewrite |
| `ALTER COLUMN TYPE` (incompatible) | `ACCESS EXCLUSIVE` | full rewrite + index rebuild |
| `ALTER COLUMN TYPE` (binary-coercible, e.g. `varchar(10)`→`varchar(20)`) | brief | instant — verify |
| `RENAME COLUMN` | brief | instant, but breaks old code |
| `DROP COLUMN` | brief | instant, but breaks old code |
| `ADD CONSTRAINT` (with scan) | `ACCESS EXCLUSIVE` (or `SHARE ROW EXCLUSIVE`) | full scan |
| `ADD CONSTRAINT NOT VALID` → `VALIDATE` | brief, then `SHARE UPDATE EXCLUSIVE` | scan without blocking writes |
| `CREATE INDEX` | `SHARE` (blocks writes) | full scan |
| `CREATE INDEX CONCURRENTLY` | `SHARE UPDATE EXCLUSIVE` (writes continue) | two scans, no blocking |
| `DROP INDEX` | brief | instant |
| `DROP INDEX CONCURRENTLY` | brief | instant |

Rows scanned per second on a warm table, single-threaded, roughly `10^6–10^7` rows/s:

```
380M rows rewrite   →  38–380 s      (measured 540 s with concurrent load and WAL)
380M rows CONCURRENTLY index → 2 × scan → 76–760 s, non-blocking
380M rows ADD CONSTRAINT (blocking) → 38–380 s of blocked writes
380M rows NOT VALID + VALIDATE → 0.1 s lock + 38–380 s non-blocking scan
```

**Conclusion**: `NOT VALID` + `VALIDATE` converts a 6-minute write outage into a 0.1-second lock. That single pattern is worth more than any other DDL technique in this lab.

---

## 3. Backfill throughput

```
throughput   = batch_size / (transaction_time + pause)
duration_hrs = rows / (throughput × 3600)
```

`batch = 5,000 rows`, `transaction = 240 ms`, `pause = 260 ms` (cycle 0.5 s):
```
throughput = 5,000 / 0.5 = 10,000 rows/s
380M rows → 380e6 / (10,000 × 3,600) = 10.6 hours
```

Sensitivity:

| Batch | Txn | Pause | Throughput | Duration (380M) |
|---|---|---|---|---|
| 500 | 40 ms | 60 ms | 5,000/s | 21 h |
| 5,000 | 240 ms | 260 ms | 10,000/s | 10.6 h |
| 20,000 | 900 ms | 600 ms | 13,300/s | 7.9 h |
| 100,000 | 4 s | 300 ms | 23,300/s | 4.5 h |

Larger batches are faster but hold longer transactions and generate more lock pressure and more WAL per commit. Sweet spot for a large table: batches whose transaction is well under a second.

Replicas: each backfilled row is a WAL record. At 200 B/row:
```
WAL rate = 10,000 × 200 = 2 MB/s sustained
if the replica applies at 6 MB/s  →  headroom exists
if the replica applies at 1.5 MB/s  →  unbounded lag; pause the backfill
```
**Conclusion**: a backfill that does not check replica lag is a read-staleness incident waiting to happen.

---

## 4. Rollback window and the expand-contract timeline

```
drop_safe_date = release_date_using_new_schema
                + max_plausible_rollback_age
                + time_to_deploy_a_forward_release
```

Policy: maximum rollback age 30 days; time to release a fix 2 days.

| Day | Release | Schema | Old column safe to drop? |
|---|---|---|---|
| 0 | R10 adds `amount_minor` (nullable), dual-writes | both columns | no |
| 1 | backfill completes (10.6 h run overnight) | both identical | no |
| 8 | R11 reads `amount_minor`, still dual-writes | both written | no (R10 must remain deployable) |
| 30 | — | R10 out of the rollback set | **yes** |
| 32 | R12 drops `amount_cents` | single shape | — |

If you drop at day 8, `rollout undo` breaks for 22 days. The rollback *appears* available and is not — the worst failure mode, because it is discovered during an incident.

**Cost of the safe path**: 32 days of carrying one extra nullable column plus a dual write. Measurable overhead, small (one extra 8-byte value and one extra write per row).

---

## 5. Queue and read-model consistency

```
staleness_bound = projection_lag_target
data_loss_boundary = retention_horizon  (must exceed projection_lag_target by a wide margin)
```

Consumer lag 5,000 messages, 200 msg/s processing, 500 msg/s producing:
```
lag_growth = 300/s  →  lag doubles every 17 s
lag hits retention horizon (say 1M) in 1M/300 = 55 min
```
So the requirement is:

```
retention ≥ max_tolerable_projection_outage × produce_rate × safety
```

Projection lag SLO `p99 < 5 s` and an outage tolerance of 2 h at 500 msg/s:
```
retention ≥ 500 × 7,200 × 2 = 7.2M messages
```

The ordering is important: **staleness is a UX problem, retention is a data-loss problem.** Set the retention from the outage tolerance and alert on lag growth.

---

## 6. Sharding arithmetic

```
shard_key_space = distinct keys
single_shard_queries = queries touching exactly one shard
cross_shard_cost     = scatter_gather = shards_touched × per_shard_query_cost
```

`orders` table, 400M rows, 2,000 tenant ids, 200,000 rows/tenant:
```
2,000 shards × 200,000 rows = 400M  ✓
```

Query "orders for tenant X" → 1 shard, index seek: fast.
Query "revenue by region for last 30 days" → all 2,000 shards:
```
cost = 2,000 × 1 ms = 2 s   vs 200 ms on a single unsharded table  →  10× slower
```
Query "count of orders per status" → all shards, plus a global aggregation step.

Global uniqueness across shards:
```
option A: uniqueness service, 1 extra network hop per insert (~2 ms)
option B: global index table on one shard (a hotspot: 400M keys, 1 shard)
option C: application-assigned ids (id = shard_id || sequence)  →  free, but the sequence is per-shard
```

Rebalancing from 2,000 to 4,000 shards requires moving half the data:
```
move_volume = 200M rows  at 10,000 rows/s = 5.5 hours of dual-write period
```
**Conclusion**: sharding is a two-way door that looks one-way. Take it only when a single node's write or storage ceiling is genuinely in the way.

---

## 7. Partitioning and retention

```
space_reclaimed_by_DROP_PARTITION = full, immediately
space_reclaimed_by_DELETE        = 0 until VACUUM; and bloat in the meantime
delete_cost(1M rows)             ≈ minutes of bloat + WAL + vacuum load
```

Time-partitioned table, daily partitions, 5M rows/day, 2 years to retain:
```
partitions = 730
dropping a month = ~150M rows
DELETE route  →  a long transaction, 150M dead tuples, autovacuum pressure, WAL volume
DROP PARTITION  →  catalog operation, instant, space reclaimed
```

Query pruning:
```
queries with a time predicate   →  touch 1 partition  →  fast
queries without a time predicate →  touch all 730       →  planning cost + scan
```
So partitioning has a cost: it punishes queries that are not time-bounded. If your access pattern is "last 7 days", partitioning is nearly free; if it is "all history by customer", it is a liability.

---

## 8. Row width and read amplification

```
read_cost = hot_columns_in_page + TOAST_pointer_lookup(1) + TOAST_page_read(1) if attribute accessed
```

`orders` table, 200 B of hot columns, 40 KB of `line_items` JSONB in the same row:
```
every row read → 1 heap page + 1 TOAST fetch (~4 KB, separate page, cache-unfriendly)
hot index scan of 1M rows → 1M × 2 page reads instead of 1M × 1
```
Vertical partition:
```
orders (200 B hot)      line_items (order_id, payload)  ← joined only when items are needed
list/scan queries       touch only the narrow table  →  ~2× fewer page reads on the hot path
```

---

## 9. Queue-driven backpressure on writes

```
write_capacity_limited_by = min( storage_write_throughput, replica_apply_rate, bloat_headroom )
```

Accepting writes at 5,000/s when replication applies at 3,000/s:
```
lag_growth = 2,000/s
lag grows 7.2M per hour  →  a read replica serving 1-hour-old data, then storage exhaustion
```
Mitigation: apply backpressure (reject or queue writes when replica lag exceeds a threshold), or reduce per-write WAL (fewer indexes on the hot table, `fillfactor`, batch commits).

---

## 10. Erasure arithmetic

```
erasure_surface = replicas + backups + caches + search_index + analytics + logs + exports
erasure_time    = time_to_reach_all_surfaces
unreached_after_T hours = surfaces_not_covered_by_T
```

One subject's data across 7 surfaces, each with a different propagation path:
```
DB              →  minutes (transactional)
read replicas   →  seconds
cache           →  invalidate + TTL propagation, minutes
search index    →  minutes to tens of minutes (reindex or delete-by-query)
analytics store →  minutes to hours (batch pipelines)
logs            →  retention-based, days
backups         →  30–90 days by policy
```
Erasure completeness after 1 hour: `3/7` surfaces. A GDPR request answered at hour 1 with "complete" is a false statement.

**Conclusion**: propagate erasures asynchronously with a per-surface receipt, and answer the request when all receipts are in — or state clearly which surfaces are covered by a legal retention basis.

---

## 11. Quick drills

1. 4,000 writes/s, 9-minute `ACCESS EXCLUSIVE` rewrite, pool 200. When does user impact start? **Answer: ~0.05 s (pool exhausts almost immediately). With `lock_timeout=3s`, no sustained outage.**
2. 380M-row table: blocking `ADD CONSTRAINT` vs `NOT VALID`+`VALIDATE`. Lock time? **Answer: 38–380 s of blocked writes vs ~0.1 s.**
3. `batch=5,000`, 240 ms txn, 260 ms pause. Throughput and duration for 380M rows? **Answer: 10,000 rows/s → 10.6 h.**
4. Backfill WAL 2 MB/s vs replica apply 1.5 MB/s. **Answer: unbounded lag. Pause the backfill.**
5. Rollback age 30 days + 2 days to release a fix. Drop date? **Answer: day 32, not day 8.**
6. Consumer lag 5,000, produce 500/s, process 200/s. Time to 1M lag? **Answer: 1M/300 ≈ 55 min → retention must exceed that by the safety factor.**
7. 2,000 shards, cross-shard revenue query. Cost vs unsharded? **Answer: 2,000 × 1 ms ≈ 2 s vs 200 ms → 10× worse.**
8. Reshard 2,000 → 4,000 shards at 10,000 rows/s. Dual-write period? **Answer: 200M rows / 10,000 = 5.5 h.**
9. 730 daily partitions, `DELETE` 150M rows vs `DROP PARTITION`. **Answer: DELETE = minutes of bloat/WAL/vacuum; DROP = instant, space reclaimed.**
10. Erasure across 7 surfaces; 3 covered in 1 hour. **Answer: 4/7 unreached — a "complete" answer at hour 1 is false.**

---

## 12. Formulas worth memorizing

| Formula | Use |
|---|---|
| `user_impact = pool_size / arrival_rate` | DDL outage starts in seconds, not minutes |
| `lock_timeout` + metadata-only DDL | the standard safety posture |
| `NOT VALID` + `VALIDATE` | constraint without blocking writes |
| `backfill_rate = batch/(txn+pause)`; `duration = rows/rate` | decide if a backfill is a release step |
| `replica_headroom = apply_rate − wal_rate` | pause the backfill when negative |
| `drop_safe_date = release + rollback_age + fix_time` | expand-contract timeline |
| `retention ≥ outage_tolerance × rate × safety` | read-model and event retention |
| `cross_shard_cost = shards × per_shard_cost` | the price of sharding |
| `DROP PARTITION` vs `DELETE` | retention on append-only tables |
| `erasure_coverage = surfaces_confirmed / total_surfaces` | how to answer an erasure request |

