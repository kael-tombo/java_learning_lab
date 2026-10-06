# Lab 05: Databases in Production — Math Foundation

Database incidents are almost always arithmetic that was never done. These are the calculations that separate "tune it" from "rescale it."

---

## 1. The concurrency cliff (why pools have an optimum)

Throughput as a function of in-flight requests. With server-side service time `S` and `μ` cores:

```
Throughput_max = cores / S           (CPU-bound ceiling)
Optimal concurrency N* ≈ cores × (1 + wait/service)
```

Worked: DB with 4 cores, query service time `S = 25 ms`:

```
Throughput ceiling = 4 / 0.025 = 160 queries/s
```

Concurrency sweep (closed loop, each query waits for response):

| Pool size N | Offered rate (req/s) | Queueing (ms) | Throughput (q/s) | Notes |
|---|---|---|---|---|
| 2 | 80 | 0 | 80 | underutilized |
| 4 | 80 | ~0 | 80 | at ceiling |
| 8 | 300 | 5 | 160 | at ceiling, small queue |
| 16 | 600 | 22 | 160 | ceiling, real queueing |
| 32 | 1200 | 60 | 160 | ceiling, latency triples |
| 64 | 3000 | 180 | 160 | **inversion zone**: same throughput, 7x latency |

**Conclusion**: beyond ~2–4x the optimal pool, you buy *latency*, not throughput, and you consume DB connections that other workloads need. Increasing a pool during an incident makes latency worse while throughput is unchanged — the exact failure in the Lab 04 incident story.

For wait/service with a fixed pool (M/M/c, see Lab 04):

```
ρ = λ·S / N          utilization
```

Keep `ρ ≤ 0.7`. With `λ·S = 20` (offered load), `N = 20` → `ρ = 1.0` — saturated. Need `N ≥ 29` for `ρ = 0.7`.

---

## 2. Little's Law for the DB tier

```
L_db = λ_peak × S_p99
```

`λ_peak = 1200 req/s`, `S_p99 = 40 ms`: `L_db = 48` concurrent DB connections needed at peak.

Now check the DB's capacity: `cores/S_mean`. If `S_mean = 8 ms`, `cores = 8`: `64/s`… that is clearly too low, so `S_mean` must be smaller or cores larger. The exercise is the *reconciliation*: **if Little's Law requires more concurrency than the DB can serve even at 100% utilization, the request volume exceeds the DB's capacity and no pool size fixes it — you need caching, batching, or more DB capacity.**

Practical corollary for many pods:

```
total_connections = instances × pool_size ≤ 0.7 × max_connections
```

With 30 pods and `max_connections = 200`: `pool_size ≤ 0.7×200/30 = 4.6` → **4–5 per pod, which is unrealistic**, hence pgbouncer / transaction pooling / fewer replicas / a bigger DB. This arithmetic is exactly what forces the right architecture.

---

## 3. Connection memory and the session-cost budget

Each session costs the server memory (work_mem per sort/hash node, buffers, backend overhead):

```
session_memory ≈ backend_overhead + active_work_mem
active_work_mem  = work_mem × (sort_operations + hash_operations)
```

With `work_mem = 8 MB`, a query using one sort + one hash = `16 MB` active. At 100 concurrent such queries: `1.6 GB` just for per-query work memory. **Raising `work_mem` globally to "fix" a slow sort can OOM the DB** — that's why it's per-query (`SET LOCAL work_mem`) for the few expensive operations.

Budget check:

```
max_connections × backend_overhead + Σ active_work_mem ≤ memory_budget × safety(0.7)
```

---

## 4. Query cost and index selectivity

Estimated index scan rows vs total rows — selectivity:

```
selectivity = matched_rows / total_rows
rows_examined_by_index ≈ matched_rows           (good)
rows_examined_by_seqscan ≈ total_rows            (bad if selectivity < ~1-5%)
```

B-tree search is `O(log_B N)`, sequential is `O(N)`:

```
index_lookup = log_B(N) page_reads ;  B ≈ page_rows (≈ 100 for 8KB/≈80B rows)
N = 100M rows → log_100(100M) = 4 page reads  vs  100M/100 = 1M page reads for seq scan
```

Planning decision rule: use an index when `selectivity × N / rows_per_page << N / rows_per_page`, i.e. when `selectivity` is small (≲ 5%). This is why `WHERE status = 'active'` on a 50%-selective column ignores the index, and why adding an index there doesn't help.

**Keyset vs offset pagination:**

```
offset_cost(k) ≈ k / rows_per_page    page reads, all discarded
keyset_cost   ≈ log_B(N)              page reads, constant
```

At `k = 100,000` and 100 rows/page: offset reads ~1000 pages of throwaway work per request; keyset reads ~4. **Offset pagination is O(page number); deep pagination must use seek/keyset.**

---

## 5. Write amplification and batching

Round-trip cost per statement (network RTT `R`, server exec `S`, plus parse/plan `P`):

```
single_row_time  ≈ R + S + P
batched(n)_time  ≈ R + S + P_batched + n·row_cost
per_row_time(batched n) = (R + S + P + n·row_cost)/n → R/n + ...   (R amortized)
```

With `R = 0.5 ms`, per-row 0.02 ms, plan 0.1 ms:

| n | total (ms) | per row (ms) | speedup |
|---|---|---|---|
| 1 | 0.62 | 0.62 | 1x |
| 100 | 2.6 | 0.026 | ~24x |
| 1000 | 21.1 | 0.021 | ~29x |
| 10000 | 201 | 0.020 | ~31x (diminishing) |

Batch size is bounded by memory/lock duration: a 100k-row single transaction holds locks, bloats WAL, and starves vacuum. Sweet spot typically 500–5000 rows.

---

## 6. Transaction lock-hold and queueing

Waiters behind a lock form a queue; each waiter holds its connection while waiting:

```
connections_held_while_waiting ≈ waiter_count
```

If a 25 ms statement blocks behind a 2 s lock holder and 40 requests queue: all 40 connections held → pool (size 50) nearly exhausted by *waiting*, not working. This is the mechanism that turns a slow report query into "the app can't log in."

Throughput collapse estimate — Little's Law with waiting:

```
W_total = S + W_lock ;  L = λ × W_total
```

`λ = 100/s`, `S = 20 ms`, `W_lock = 500 ms` → `W = 520 ms`, `L = 52`. If the pool is 30, `ρ > 1` → divergence. **Fix the lock holder (statement timeout, `NOWAIT`, batching), not the pool.**

---

## 7. Replication lag and staleness budget

With primary commit rate `c` writes/s, average write size `W` bytes, replica apply rate `A` bytes/s:

```
lag_seconds ≈ (unapplied_bytes) / A
unapplied_bytes ≈ c × W × lag   (steady state)
```

More usefully, growth in lag when `c·W > A`:

```
d(lag)/dt = c·W − A
```

If the replica can apply 20 MB/s and the primary generates 25 MB/s: lag grows 5 MB/s → unbounded until disk fills. **Replica capacity must exceed peak (not average) primary WAL rate**, with headroom ≥ 2x.

Read-your-writes staleness tolerance: if you allow staleness `S_max` on reads, then route reads that need fresh data to the primary; the fraction of such reads is your replica utility.

---

## 8. Vacuum, bloat, and transaction-id wraparound

Dead-tuple bloat factor:

```
bloat_factor ≈ dead_tuples / live_tuples
effective_table_size = real_size × (1 + bloat_factor)
```

With 30% bloat, every full scan reads 43% more pages, and index scans hit more pages → slower queries → longer transactions → worse vacuum. Autovacuum must keep `dead_tuples` below the threshold continuously.

Transaction ID wraparound margin:

```
xids_until_wraparound ≈ 2^32 − max_age(datfrozenxid)
```

`age(datfrozenxid)` rising steadily = vacuum starvation. Monitor and alert on age (e.g. warn at 100M, page at 1B) — wraparound forces emergency, near-unavailable shutdown.

---

## 9. Capacity planning: storage

```
rows_per_day = λ_writes × 86400
bytes_per_day = rows_per_day × avg_row_bytes × (1 + index_overhead + bloat_allowance)
index_overhead ≈ 0.5–1.5× table (depends on index count/width)
growth_headroom = horizon_days × growth_rate^(n)
```

Example: `λ = 500/s`, `row = 500 B`, index overhead 1.0x, bloat 0.3:

```
bytes/day = 500×86400×500×(1 + 1.0 + 0.3) = 43.2M×500×2.3 ≈ 49.7 GB/day
```

At 30% month-over-month growth, year-1 volume ≈ 1.5 TB. This is why partitioning, archival, and retention policies are capacity decisions, not cleanup tasks.

---

## 10. Error-budget view of database availability

```
A_db = MTBF / (MTBF + MTTR) ;  MTTR = detect + diagnose + mitigate
```

With `MTBF = 60 days`, `MTTR = 30 min`: `A = 96.7%`. To hit 99.95% (SLO), with `MTBF = 60 d` you need `MTTR < ~4.3 min`. **Database incidents are dominated by MTTR, not MTBF** — invest in fast failover, rehearsed runbooks, and instant rollback of bad migrations.

Migration risk budget:

```
P(no-impact migration) ≈ 1 − P(lock_conflict) − P(long_rewrite)
```

For a 200M-row table, an unindexed `ALTER` holding `ACCESS EXCLUSIVE` for 3 minutes during peak: expected downtime `≈ (lock_hold / time_window) × peak_qps × avg_query_cost`. Always batch.

---

## 11. Pool sizing vs max_connections across tiers

```
Σ_tiers (instances_tier × pool_tier) + admin_reserve ≤ 0.7 × max_connections
```

For a two-tier app (web + workers) on a 200-connection DB:

```
web:     12 pods × 8  = 96
workers: 20 pods × 3  = 60
admin/replication/monitoring reserve: 20
total = 176 ≤ 140?  → NO → too many.
```

Resolution options, in order of preference: (1) pgbouncer transaction pooling, (2) reduce worker count/pool, (3) read replicas for reporting, (4) bigger DB. Note how the arithmetic *forces* the architecture.

---

## 12. Backup / RPO math

```
RPO = time since last recoverable point
WAL archiving interval + backup frequency ⇒ RPO bound
RTO = detect_fail + promote/failover + app_reconnect + validate
```

With continuous WAL archiving, `RPO ≈ seconds`. Without it (nightly dumps only), `RPO = 24 h`. RTO is dominated by **app reconnection behavior** (poolers retrying, DNS/cache TTLs, connection storms on promotion), which is why failovers need jittered reconnects and a warm standby.

---

## 13. Quick drills

1. 4-core DB, 25 ms queries, pool 64 offered at 3000/s → what happens? **Answer: throughput capped ~160/s, latency ~180 ms queueing — inversion zone. Shrink pool, or add cache/capacity.**
2. `λ_peak = 1200/s`, `S_p99 = 40 ms` → connections needed? **Answer: 48. Check DB capacity; if short, cache/batch/shard.**
3. 30 pods, 200 max_conn → per-pod pool? **Answer: ~4. Use pgbouncer.**
4. Replica applies 20 MB/s, primary peak WAL 25 MB/s → outcome? **Answer: lag grows 5 MB/s → unbounded. Need ≥2x headroom.**
5. Deep pagination to row 100,000 at 100 rows/page → offset page reads? **Answer: ~1000 discarded pages vs ~4 for keyset.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `ρ = λ·S/N`, keep ≤ 0.7 | pool sizing; beyond optimum you buy latency, not throughput |
| `Throughput ≤ cores/S` | the hard DB ceiling |
| `L_db = λ_peak × S_p99` | connections needed at peak |
| `total = instances × pool ≤ 0.7·max_conn` | forces pooling/proxy/replicas |
| `offset_cost(k) ≈ k/rows_per_page` | why deep pagination must use keyset |
| `per_row(batch) ≈ R/n + cost` | batch size justification |
| `d(lag)/dt = c·W − A` | replica capacity rule |
| `bloat ≈ dead/live` | vacuum monitoring |
| `A = MTBF/(MTBF+MTTR)` | invest in MTTR |
