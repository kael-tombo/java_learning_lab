# SLO Sheet: Background-Job Scheduler on a Binary Heap

Service. A priority scheduler for background jobs (exports, emails,
thumbnail renders) with a top-K trending view over the event stream.
The heap is the entire scheduling core; everything else is plumbing.

SLO 1 - dispatch order. Jobs run in priority order with FIFO tiebreak by
sequence number. Conformance proven by draining 50k scripted jobs and
diffing against a sorted-oracle schedule. Zero inversions tolerated.

SLO 2 - operation cost. push and pop O(log n), peek O(1). The report
shows timing curves from 10k to 1M resident jobs beside the log-scale
expectation, flagging any superlinear drift.

SLO 3 - trending view. Top-K over a sliding event window, refreshed on
demand: K=10 over the last 100k events. Results must equal a full-sort
oracle on every refresh during the soak.

SLO 4 - overload conduct. Queue depth capped at 256k jobs; beyond that
the lowest-priority arrivals shed with a counter. The flood drill (5x
submit rate, 10 minutes) must reconcile: submitted = run + shed + held.

Build order. Array-backed heap with comparator plus sequence tiebreak,
then the scheduler shell (submit/cancel/list), then the trending view,
then the cap-and-shed policy, then the metrics exporter.

Heap audit. After each batch, parent <= children verified across the
array and size reconciled with submit/run/shed counters. Fuzz with 40k
random ops against PriorityQueue as oracle.

Rollback. Single flag swaps the custom heap for PriorityQueue; the
conformance suite must pass identically on both. Scoring: order fidelity
12, cost curves plus trending parity 10, flood reconciliation 8.
## Drill calendar
- Weekly: drain-order conformance.
- Monthly: flood reconciliation.
- Quarterly: cap review vs growth.
- Log every drill with seed.
