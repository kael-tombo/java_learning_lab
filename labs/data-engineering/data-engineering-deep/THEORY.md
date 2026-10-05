# THEORY — The Ten Mental Models of Production Data Engineering

## 1. Time is the hardest part

There are two clocks and they disagree.

- **Processing time**: when your code saw the event.
- **Event time**: when the event happened.

Everything hard in streaming follows from that disagreement. An event can
arrive after the window it belongs to has closed. A replay can re-deliver old
events into a new watermark. A restart can move the watermark backwards.

The consequences, stated as rules:

- **R1**: any business-correct number must be computed in event time.
- **R2**: you must state an ordering assumption (how out-of-order events are),
  and that assumption belongs in code, not in a wiki.
- **R3**: a watermark is a *promise*, not a guarantee. Anything after it is
  late and needs a defined path: correction, side output, or reconciliation.
- **R4**: "too late" is a business decision with a cost. Choose a lateness
  budget; do not let it default to infinity.

```
watermark(t) = max_event_time_seen - out_of_orderness_bound - delay
```

The bound is only as good as your understanding of the producers. Derive it
per source, from observed behaviour, and re-derive it when a producer changes.

## 2. State is a liability, not an asset

Stateful processing buys correctness and costs: memory, checkpoint time, and
rescale time.

- **R5**: every state entry needs a TTL or a bound. Unbounded state is a leak
  with a fuse.
- **R6**: the cost of state is `keys x value_size x (1 + overhead)`, and
  checkpoint cost is roughly proportional to *changed* state, not total, if you
  use an incremental backend.
- **R7**: prefer aggregation over history. `ListState` of events scanned per
  event is O(n); a bucketed counter is O(1). The 2.4TB-to-340GB refactor in
  lab 18 is entirely this rule.

The design question is always: *what is the minimum state that makes the output
correct?* Usually it is a counter with a TTL, not a buffer.

## 3. Delivery is a spectrum, and only you choose where you land

- at-most-once: may lose, never duplicates
- at-least-once: may duplicate, never lose
- effectively-once: at-least-once delivery plus an idempotent sink
- exactly-once: requires a transactional sink or a transactional source+sink pair

- **R8**: exactly-once is a property of a *pipeline*, not a feature of a
  broker. If your sink is an HTTP API, you have at-least-once and you need an
  idempotency key.
- **R9**: make the sink idempotent and the delivery semantics stop mattering
  for correctness. This is the design move with the best return.

Idempotency comes from one of: a natural key with upsert, a dedup set keyed by
source position, or a version/monotonicity check (apply only if newer).

## 4. Schema is a contract between strangers

Your producer and your consumer are usually different teams, in different time
zones, one of whom has left the company.

- **R10**: additive changes (new nullable field) are safe. Renames, drops, and
  type narrowings are breaking, and they are breaking *silently* if your
  deserializer is permissive.
- **R11**: store enough history to read the old shape (an envelope with a
  schema version, or a table format with schema evolution).
- **R12**: a contract is only real if it is executed. A reviewed document is a
  wish.

Compatibility direction matters: BACKWARD (new readers read old data),
FORWARD (old readers read new data), and FULL. A topic that is both read and
written needs FULL or you will break the writers.

## 5. Partitioning is a physical decision with logical consequences

Partitioning determines parallelism, ordering scope, and file count. All three
at once.

- **R13**: ordering is guaranteed *within a partition only*. Cross-partition
  ordering requires either one partition (no parallelism) or a design that does
  not need it (sequence numbers + reorder buffer).
- **R14**: high-cardinality partitioning produces many small files. The rule of
  thumb: partition by low-to-medium cardinality time, and use a bucket
  transform for the high-cardinality filter column.
- **R15**: skew is a data property, not a code property. A hot key that is 0.1%
  of rows and 40% of a reducer's work will happen, and the schedule that
  creates it (a holiday, a promo) is not in your code.

## 6. Cost is a design output

```
monthly_cost = storage + bytes_scanned + compute + requests + egress
```

You can move two of those meaningfully: **bytes scanned** (partitioning,
pruning, pre-aggregation, columnar formats) and **compute** (warehouse
lifecycle, caching, right-sizing). Storage is mostly a function of what you
choose to keep, and requests are mostly a function of file counts.

- **R16**: measure the cost of a *question*, not of a system. "This dashboard
  costs $4,100/month" is not actionable. "This question costs 3.1TB of scan"
  is.
- **R17**: pre-aggregation is the highest-leverage cost move in analytics. It
  converts an expensive question into a cheap one, permanently.

## 7. Correctness is a claim you must be able to support

- **R18**: reconciliation against an *independent* source is the only check
  that catches shared bugs. Two pipelines that agree because they share a
  library prove nothing.
- **R19**: invariants must be cheap enough to always run. A check you sample is
  a check you do not have.
- **R20**: point-in-time correctness is a separate property from correctness.
  A number can be right and still be unusable because it leaked the future.

## 8. Backfill is a first-class operation, not an emergency

- **R21**: if you cannot backfill 90 days safely, you cannot deploy safely.
  Test it on a schedule, not in an incident.
- **R22**: backfills must be isolated (a separate pool, a shadow table or branch)
  so they cannot write over production results.
- **R23**: backfill is where point-in-time bugs surface. A backfill recomputes
  with today's code against historical data, so any non-determinism shows up
  here and nowhere else.

## 9. Operations are the product

- **R24**: every pipeline needs a freshness SLO, and the SLO needs an
  owner who is paged.
- **R25**: alert on data, not on tasks. "The job succeeded" and "the data is
  right" are different claims.
- **R26**: error budgets, not fixed thresholds. A fixed threshold either fires
  constantly or never fires.
- **R27**: mean time to *understand* is the metric that matters. A page that
  names the likely cause and the first command to run is worth ten pages that
  say "error".

## 10. Governance is a control system

- **R28**: classification must be automatic and evidenced, or it will be
  incomplete within a month.
- **R29**: deletion must be verifiable. "We ran the delete" is not evidence; a
  query returning zero rows is.
- **R30**: policy that no system reads is documentation. Policy evaluated in CI
  and at runtime is a control.

## How the models connect

Time (1) drives state (2), which drives delivery guarantees (3). Schema (4) and
partitioning (5) determine cost (6) and what correctness even means (7).
Backfill (8) is where 2, 3, and 7 are tested. Operations (9) is how you learn
that 1-8 were wrong. Governance (10) constrains everything above it.

Read them in that order the first time. Read them as a checklist in review.
