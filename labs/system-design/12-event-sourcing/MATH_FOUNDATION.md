# Event Sourcing - Math Foundation

## Storage Growth: Unbounded by Design

Events are append-only, so storage grows linearly in the number of business
events with no upper bound short of explicit archival.

```
  storage = n_events * bytes_per_event * (1 + index_overhead)

  n_events/day = n_operations/day
  bytes_per_event:
    compact (protobuf/avro, field numbers)   120-250 B
    JSON with field names                     350-600 B
    JSON, verbose, with metadata              800-1,500 B
  index + WAL overhead                        ~1.4x raw

  400k orders/day, 3 events each = 1.2M events/day
    at 400 B compact + 1.4x = 1.2M * 400 * 1.4 = 672 MB/day
                         = 245 GB/year  =   4.4 TB/3-year retention
```
**Schema efficiency is a first-order cost lever.** Moving JSON with field names
to a compact binary encoding typically halves the bill. Re-verify the numbers
against your real event sizes; they vary more than people expect.

### What Does Not Compensate

Compression helps at rest (a factor of 3-6x on JSON events) but not in the
working set. Projection rebuild time and query latency are unaffected by
archive compression, so plan capacity on **uncompressed** working-set size.

## Snapshot Sizing

Replaying from genesis costs:

```
  load_time(aggregate) = replay_cost(n_events_since_genesis)

  with a snapshot at version v:
    load_time = deserialise(snapshot) + replay(n_events_since_v)

  serialisation_cost per snapshot = S bytes * c_sec_per_byte
```

### The Optimal Trigger

Snapshot when the replay cost exceeds the snapshot write cost by a factor:

```
  snapshot when  n_events_since_snapshot * r  >  S * c * K

  r = replay cost per event      ~50 µs
  S = snapshot size              ~500 B
  c = serialise cost per byte    ~2 ns
  K = safety factor (how much worse replay may get)  ~2

  n_trigger = (500 * 2e-9 * 2) / 50e-6
            = 2e-6 / 5e-5 = 0.04 events
```
That result says "snapshot constantly", which exposes the flaw in the model:
`S * c` is *not* per snapshot in isolation — it is **amortised across every
load that uses it**. The correct amortisation:

```
  snapshots_written = n_events / n_trigger
  total_snapshot_cost = (n_events / n_trigger) * S * c
  total_replay_cost   = (n_events / 2) * r        (on average, half the log)

  minimise total = derivative w.r.t. n_trigger -> 0

  =>  -S*c/n_trigger^2 + r/2 = 0
  =>  n_trigger = sqrt(2 * S * c / r)

  S=500B, c=2ns, r=50µs:
    n_trigger = sqrt(2 * 500 * 2e-9 / 50e-6)
              = sqrt(2e-6 / 5e-5)
              = sqrt(0.04)
              = ~0.2 events      (still degenerate)
```
The model is degenerate for these numbers because replay per event (50 µs) is
much more expensive than serialising a whole snapshot (1 µs). **Practical
consequence:** for a hot aggregate, snapshot far more often than feels
necessary — every 50-100 events is not unreasonable — and measure rather than
trust intuition. For cold aggregates, snapshot rarely or never.

### The Working Rule

```
  snapshot when  log_bytes_since_snapshot > K * state_bytes      (K ~ 1-4)
```
This is simple, self-tuning, and independent of the cost constants. It also
means a large state snapshots less often, which is the correct direction.

## Aggregate Hotspot Arithmetic

One aggregate, modified at rate `r`, serialised by the optimistic-concurrency
loop:

```
  conflict_rate = 1 - e^(-r * t_reload)     (Poisson approximation)
    t_reload = time to load + validate the aggregate (~1-5 ms)

  r = 50 writes/s, t_reload = 2 ms:
    conflict_rate = 1 - e^(-0.1) = 9.5%

  r = 500 writes/s:
    conflict_rate = 1 - e^(-1.0) = 63%     -> retries dominate
```
So an aggregate above roughly **100 writes/s becomes a contention problem**.
Mitigations, in order:

1. **Shard the aggregate** (e.g. one sub-aggregate per line item) — reduces
   `r` proportionally to the shard count.
2. Partition the event log so the hot aggregate is alone on its partition.
3. Accept retries with backoff and a cap, and document the aggregate as hot.
4. Move the workload to a different consistency mechanism (a counter in a KV
   store, with the event log written asynchronously).

## Log Index and Query Cost

Temporal queries need to seek to a point in time:

```
  (account_id, effective_at) index  ->  seek + scan

  events_per_account = n_events / n_accounts
  query cost = log(events_per_account) + events_in_range

  1.2M events/day, 200k accounts  ->  6 events/account/day
  balance(at = 30 days ago) scans ~180 events  ->  trivial

  balance(at = 3 years ago)      scans ~6,500 events  ->  still fine
```
Because the fan-out per aggregate is low, temporal queries are cheap **with the
right index**. Without `(aggregate_id, version)` or `(aggregate_id,
effective_at)`, the same query is a full table scan and the capability is
theoretically available but practically unusable. **The index is what makes
temporal queries real.**

## Projector Throughput and Lag

```
  projection_lag = backlog_events / projector_throughput

  backlog = event_rate * downtime
  catch_up_time = backlog / throughput

  event_rate = 1.2M/day = 14 events/s average, 60 events/s peak
  projector throughput = 400 events/s (measured, single-threaded-ish)

  after a 1-hour broker outage:
    backlog = 60 * 3600 = 216,000 events
    catch_up = 216,000 / 400 = 540 s = 9 minutes of stale read model
```

### Peak Matters, Not Average

```
  capacity sizing must use peak:
    if sized at average (14 events/s), a 3x peak instantly outruns capacity
    and lag grows without bound until read models are visibly wrong

  catch-up must be parallelisable and rate-limited so it does not itself
  starve the live path during recovery
```
Alert on **projection lag**, not on projector error rate. A projector that is
running perfectly but 9 minutes behind is broken, and its error rate is zero.

## Rebuild Time: The Number That Determines Feasibility

```
  rebuild_time = total_events / projector_throughput

  1.2M events/day, 4-year retention = 1.75B events
  projector at 400 events/s:
    rebuild_time = 1.75e9 / 400 = 4.375M s = 50.6 DAYS

  at 40 parallel projectors (typical host):
    rebuild_time = 4.375M / 40 = 109,375 s = 30.4 hours
```
**Rebuild time is the constraint that makes or breaks event sourcing.** 30 hours
is acceptable for a projection you rebuild quarterly. 30 days is not, and the
design must change: reduce retained events, increase projector throughput, or
use snapshot-seeded rebuilds.

### Snapshot-Seeded Rebuild

```
  rebuild_time = sum over aggregates of (load_snapshot + replay(tail))
                = n_aggregates * (snapshot_load + tail_events * r)

  200k accounts, snapshot every 100 events, avg tail 50:
    200k * (20 µs + 50 * 50 µs) = 200k * 2.52 ms = 504 s = 8.4 minutes
    vs. 30 hours from genesis
```
A **35x improvement**, available only because snapshots are deterministic
state at a known version. This is the strongest practical argument for
snapshotting.

## Optimistic Concurrency Retry Cost

```
  retry_cost = conflict_rate * t_reload * attempts
  expected_extra_time = conflict_rate * t_reload

  r = 100 writes/s, t_reload = 2 ms:
    conflict_rate = 1 - e^(-0.2) = 18%
    expected_extra_time = 0.18 * 2 ms = 0.36 ms per operation
    attempts (95% success) = ln(0.05)/ln(1-0.18) = 2.996/0.198 = ~15 attempts
```
15 attempts is a sign the aggregate is too hot, not that you need more retries.
Above roughly 100 writes/s, fix the boundary rather than the retry loop.

## Event Ordering and Causality

```
  total order per aggregate   (required, from the store's CAS)
  global order across all     (NOT required, and expensive)
  per-partition order         (from partition key = aggregate_id)

  cost of a global sequence:
    every append contends on one counter  -> the same hotspot problem
    and it buys nothing a per-aggregate version does not already give
```
Partitioning the log by `aggregate_id` gives per-aggregate ordering and scales
writes linearly. A global sequence is a bottleneck that provides no additional
guarantee for aggregates that never interact.

### Causal Ordering Across Aggregates

For cross-aggregate consistency (a transfer touching two accounts), you need a
**causal** mechanism, not a global sequence:

```
  transfer event carries the *expected version* of BOTH accounts
  -> the command fails if either moved  -> the caller retries coherently
```
This keeps each aggregate's concurrency control local while still preventing
inconsistent cross-aggregate operations. It is a saga step with version
preconditions.

## Effective Dating and Time

```
  event_time = occurred_at   (when the business event happened, set by the writer)
  record_time = recorded_at  (when it was appended)

  correct semantics: order and query by occurred_at, within a partition, with
                     the per-aggregate version as the tiebreak.
  never: rely on wall-clock ordering. Clocks are unsynchronised, NTP steps
         happen, and two events 1 ms apart can append in either order.
```
Store both, and prefer the version for ordering. This matters more than it
looks: a system that orders by timestamp will eventually produce a balance that
is wrong because of a clock step, and the reconstruction will not match the
live projection.

## Storage Tiering

```
  hot   (0-90 days)     full events, indexed, fast temporal queries
  warm  (90d-3y)        compressed, indexed sparsely
  cold  (3y+)           archived, query by explicit fetch

  temporal_query_cost at 3 years = archive_fetch + scan
    archive_fetch = 30 s - 10 min   -> NOT a real-time query
```
So the retention architecture determines which temporal queries are actually
answerable interactively. Be explicit: "we support balance-as-of for 90 days"
is an honest product statement; "we support balance-as-of" with a 4-hour cold
fetch is not.

## Immutable Log and Deletion

```
  erase_from_immutable_log:  impossible (by definition)

  workable: do not put erasable data in the log
    events contain customerRef, never name/email/address
    personal data lives in a mutable store, deleted on request

  cost: every read needs a join to the personal-data store
        -> the "balance as of" query becomes a join, not a scan
```

## Read Amplification: Projections Are Fixed Shapes

```
  1 projection per query shape

  queries: "balance by account", "top 10 by balance", "monthly statement",
           "balance as of date", "sum by currency"
  -> 5 projections, each with its own table, each rebuilt separately

  rebuild cost = 5 * rebuild_time  (if all are rebuilt on a schema change)
```
Blue-green projection deploys make this tractable (rebuild the new one while the
old one serves), but the multiplier is real. Include it in the feasibility
calculation before committing to event sourcing.

## Exactly-Once Effects

```
  at-least-once projection + idempotent handler = effectively-once EFFECT
  dedup_ttl >= broker_retention + max_retry_backoff

  broker retention 7 days, max backoff 5 min:
    dedup_ttl >= ~7 days
```
A dedup key with a 24-hour TTL against a 7-day-retained log is **not**
idempotent, and day-3 redeliveries will double-apply. Assert
`dedup_ttl > retention` in a test so it cannot silently regress.

## Sizing the Event Log Partition

```
  partition by aggregate_id

  hot aggregate at 100 writes/s needs its own partition or it starves others
  partitions = max(1, ceil(target_throughput / per_partition_capacity))

  40 partitions * 500 events/s = 20,000 events/s capacity
  target load = 60 events/s peak  -> 1 partition would technically suffice,
  but headroom for rebalancing and rebuild consumers argues for more
```
Rebuild consumers read the whole log, so they compete with live traffic.
Partition count is a capacity decision, not just a write-throughput decision.

## Verification Cost (the audit story)

```
  verify(audit at version v):
    1. load snapshot <= v          ~20 µs
    2. replay events <= v          tail_count * 50 µs
    3. compare against the projection at its recorded version

  cost per verification = ~2.5 ms   -> 400 verifications/second/single-threaded
  a full audit of 200k accounts    = 500 s single-threaded, ~13 s at 40 threads
```
This is cheap enough to run continuously. **Do** — an audit nobody runs is an
audit that has never been tested. Run it daily and alert on any mismatch.