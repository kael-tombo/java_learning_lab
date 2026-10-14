# Soak Plan: Metrics Registry and Crawler Queue Under Threads

Target. A metrics registry (counters, gauges, histograms) fed by 16
writer threads plus a lock-free work queue feeding 8 crawler workers.
The plan proves linearizable behavior first, then measures scaling, in
that order - numbers without a correctness story are rejected.

Registry design. LongAdder counters per metric, ConcurrentHashMap from
name to cell, striped histogram cells merged on read. No global lock on
the write path; reads tolerate merging across stripes with a documented
staleness bound of one collection interval.

Queue design. Michael-Scott style linked queue (or a bounded
array-backed ring with CAS head/tail - decision logged with rationale)
for crawl URLs, backpressure via fixed capacity plus a drop counter.
Enqueue/dequeue pairs reconciled: produced = consumed + dropped + held.

Correctness harness. Linearizability spot-checks on 2-thread
interleavings with a recorded schedule; then a chaos soak (4 producers,
4 consumers, 200k items) asserting no loss, no duplication, and counter
totals equal to per-thread sums.

Scaling runs. Writer threads 1/2/4/8/16 at fixed work per thread; the
report plots throughput and states where contention flattens the curve.
LongAdder vs synchronized-counter A/B included so the mechanism earns
its place with data.

Hazard list. ABA on head pointer (tagged/generational fix), false
sharing on hot cells (padding note with measurement), queue drain race
at shutdown (poison-pill protocol), registry key explosion (cardinality
cap with eviction rule).

Sign-off. Harness logs, soak reconciliation, scaling plot data, hazard
register with fixes. Weighting: harness rigor 12, soak reconciliation
10, scaling candor 8.
## Soak matrix
- Threads: 1, 2, 4, 8, 16.
- Same work per thread each run.
- Reconcile produced vs consumed.
- Plot flattening point explicitly.
- Keep poison-pill shutdown tested.
