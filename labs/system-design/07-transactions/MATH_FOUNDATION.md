# Distributed Transactions - Math Foundation

## ACID Costs in a Single Node (the baseline you are paying to preserve)

### Atomicity / Durability: fsync latency dominates

```
  write_latency ~= commit_latency = fsync_latency + log_write
  throughput     <= 1 / commit_latency          (serial commits)

Group commit amortises fsync across a commit group of size G:
  throughput = G / fsync_latency

  fsync = 1 ms,  G = 100  ->  100,000 commits/s
  fsync = 1 ms,  G = 1    ->      1,000 commits/s   (100x worse)
```
**Lesson:** group commit is not an optimisation detail; without it, a
synchronous-commit database is bounded at ~1,000 writes/s per node. This is
why "batching" shows up in every throughput budget.

### Isolation: serialisability rate falls as concurrency rises

Under 2PL, conflict probability grows with the number of *concurrent* active
transactions in the overlapping key range:

```
  conflicts ~= C(k, 2) * p     k = concurrent txns, p = key collision prob
  serialisable_throughput ~= 1 / (txn_duration + conflict_overhead)
```
Optimistic concurrency control (OCC) makes this explicit: aborts grow with
contention, so its throughput *peaks* and then falls:

```
  T(OCC) = attempts_per_commit * (read + validate + write) / (1 - abort_rate)
  abort_rate rises ~ k^2 for a fixed hot-key set
```
Pick pessimistic when contention is high and known; pick optimistic when the
working set is large and conflicts are rare.

## Two-Phase Commit: latency and blocking

### Latency

```
  T_2PC = T_prepare + T_commit
        ~= RTT + max_i RTT_i + 2 * log_write     (for F participants)

  log_write  ~= 0.5 ms,  RTT = 1 ms, F = 4 participants:
  T_2PC ~= 1 + 1 + 1 = ~3 ms   vs ~1.5 ms for a local commit
```
You pay roughly **one extra round trip** plus a coordinator log flush per
transaction, *per committed transaction*, forever.

### Blocking window (why 2PC is dangerous)

If a participant crashes after replying `PREPARED` but before the coordinator
logs `COMMIT`:

```
  P(blocked) = P(crash in that window)
  Expected blocking time = MTTR_participant   (bounded only by recovery)
```
Recovery therefore **must** consult a durable coordinator log before deciding
to `ABORT`. Without it, the recovery path can unilaterally abort a transaction
the primary already committed — the classic "in-doubt" corruption.

### Capacity collapse risk

A coordinator failure with 3,000 in-doubt transactions and a 60 s recovery
timeout means 3,000 blocked connections for up to 60 s. Connection pool sizes
are sized for throughput, not for this. Model it:

```
  blocked_connections = in_flight_at_failure * failure_rate
  pool_needed         = throughput * normal_latency + blocked_connections
```
This is why real systems bound concurrent transactions *per resource* and
reject with an explicit backpressure signal rather than queueing silently.

## Three-Phase Commit: the extra phase

3PC adds a pre-commit phase so participants can commit if the coordinator
dies. Its safety relies on a **bounded network delay assumption** that real
networks do not honour — so it is largely of academic interest. Cost model:

```
  T_3PC = 3 RTT + log_write   (vs 2 RTT for 2PC)
```
You pay 50% more latency for a guarantee that fails under the one condition
you built the system to survive: partition.

## Saga failure combinatorics

With `n` steps and per-step failure probability `p`, and each failed step
triggering a compensation that itself fails with probability `q`:

```
  P(all n steps succeed)             = (1 - p)^n
  P(at least one failure)            = 1 - (1 - p)^n
  P(a failure AND its compensation fails) >= p * q
  P(any compensation fails)          ~= 1 - (1 - p*q)^n

  n = 8, p = 0.01, q = 0.05:
    P(no failure)            = 0.923
    P(at least one failure)  = 0.077
    P(compensation fails)    ~= 1 - (1 - 0.0005)^8 = 0.4%
```
A 0.4% chance of an unrecoverable state means you still need a **manual
reconciliation path** and a human on call. Budget for it.

### Compensatability is not binary

Classify each step, because the label determines the design:

```
  compensatable   : reserve inventory     -> release reservation
  repeatable      : charge card           -> refund (repeatable N times)
  non-compensatable: email the customer   -> NOTHING (send a correction)
```
If any step is non-compensatable, the saga needs an approval gate or a
"human in the loop" fallback before the irreversible step fires. Design that
gate in from the start; adding it later means re-architecting the saga.

## Idempotency: the deduplication window

Effectively-once = at-least-once delivery * a bounded dedup window. The window
must exceed the maximum plausible redelivery horizon:

```
  dedup_ttl >= p99_delivery_delay + max_retry_backoff + broker_retention_window

  p99 delay = 5 s, max backoff = 5 min, broker retention = 7 days
  dedup_ttl >= ~7 days
```
A dedup key with a 24 h TTL against a 7-day-retained queue is *not*
idempotent — it will double-apply on day 3. This mismatch is a top cause of
"we saw the same charge twice".

## Outbox: cost of the dual write

The outbox removes the dual-write problem at the cost of one extra table and
one extra poll. Its steady-state cost:

```
  poll_cost_per_second   = pollers * (1 / poll_interval)
  outbox_rows_per_day    = event_rate * 86400
  bloat_factor           = 1 + index_overhead + vacuum_overhead   (~1.5x)

  event_rate = 1000/s  ->  86.4M rows/day retained before cleanup
```
Two consequences: (1) the outbox table needs aggressive partition-by-time
drops, not `DELETE`; (2) poller count must exceed consumer count or you create
a new bottleneck at the drain step.

## Transactional Throughput Ceiling (the number to remember)

```
  sync_2pc_throughput ~= 1 / (fsync + RTT + fsync)
  With fsync = 1 ms and 1 ms RTT:  ~333 txns/s of PARTIAL DB LOCKS
```
Distributed transactions also consume locks in *several* databases at once.
With `k` resources held per transaction, effective capacity collapses:

```
  effective_throughput ~= min_i( capacity_i / k )
```
Held locks across 3 resources at 1,000 ops/s each => ~333 concurrent
transactions system-wide, and the slowest resource is the bottleneck. This is
the arithmetic that ends "let's just use 2PC" conversations.