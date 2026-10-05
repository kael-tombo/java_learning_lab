# REAL_WORLD_PROJECT — Lists Deep

Production use-case: **a job queue / inbox service** using ArrayDeque, with CopyOnWriteArrayList snapshots for readers. Secondary: LRU cache on top of LinkedHashMap.

## 1. Problem statement
Serve enqueue/dequeue/peek with p99 SLOs and a snapshot read model for monitoring.

## 2. Architecture
- Ingest: producers.
- Core: ArrayDeque behind a narrow interface; snapshot via CopyOnWriteArrayList.
- Serve: dequeue API + metrics.
- Persist: WAL of enqueue/dequeue.

## 3. Implementation plan (2 weeks)
W1: core + invariants + property tests.
W2: API + metrics + JMH + runbook + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 dequeue | SLO | JMH |
| Throughput | ops/s | load gen |
| Snapshot lag | near 0 | event counter |
| Memory | O(n) | JOL |
| Recovery | < 5 s | restart drill |

## 5. Risks & prevention
- LinkedList GC churn → prefer ArrayDeque.
- Concurrent read sees partial → snapshot via COW list or sync.
- Null element crashes → reject null at ingress validation.

## 6. Runbook
- Alerts on p99 and on snapshot size vs queue size divergence.
- Rollback to Vector (if migrating) or back to LinkedList (if regressing) behind a flag.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedList.html
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo + JMH + runbook.

## 8. Grading rubric
- Correctness 30 / Perf 30 / Operability 20 / Writeup 20.
