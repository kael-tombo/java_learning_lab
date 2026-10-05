# REAL_WORLD_PROJECT — Queue & Stack Deep

Production use-case: **worker pool service** with a bounded priority queue and overflow policy. Secondary: a request-FIFO API gateway.

## 1. Problem statement
Serve submit/poll with p99 SLOs and bounded memory; handle backpressure.

## 2. Architecture
- Ingest: producers.
- Core: bounded blocking queue + priority queue back-end.
- Serve: submit API + metrics.
- Persist: WAL or in-memory only.

## 3. Implementation plan (2 weeks)
W1: core + invariants + property tests.
W2: API + metrics + JMH + runbook + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 poll latency | SLO | JMH |
| Throughput | ops/s | load gen |
| Bounded memory | ≤ capacity | JOL |
| Overflow policy | counted | metrics |
| Recovery | < 5 s | restart drill |

## 5. Risks & prevention
- Priority queue dies if you add blocking: use PriorityBlockingQueue only when unbounded is acceptable; else drive a bound from a counter.
- Deadlock on unbounded blocking: set a capacity bound.
- Iterator surprises: only use poll for order.

## 6. Runbook
- Alert on p99 and overflow count.
- Rollback flag to FIFO ArrayBlockingQueue.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayDeque.html
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo + JMH + runbook.

## 8. Grading rubric
- Correctness 30 / Perf 30 / Operability 20 / Writeup 20.
