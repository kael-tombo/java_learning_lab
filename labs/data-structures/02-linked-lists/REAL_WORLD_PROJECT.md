# REAL_WORLD_PROJECT — Linked Lists

Production use-case: **O(1)-splice playlist / task-queue service**. Secondary: undo-history chain with bounded memory.

## 1. Problem statement
Serve insert/remove/splice at known positions with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 splice latency, throughput (ops/s), max heap, correctness bar (exact order vs oracle).

## 2. Architecture
- Ingest: task/playlist events feeding the list.
- Core: singly/doubly linked list behind a narrow interface.
- Serve: reorder API + metrics + health.
- Persist: snapshot/WAL where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 splice latency | define SLO | JMH / load test |
| p99 splice latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at N entries | JOL / heap dump |
| Correctness | exact vs ArrayList oracle | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Lost-node corruption -> rotor/invariant audits.
- Traversal degradation -> doubly-linked + tail pointer.
- Memory blowup -> bounded caps + node pooling.
- Concurrency bugs -> narrow sync + stress tests.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/javase/8/docs/api/java/util/LinkedList.html
- https://en.wikipedia.org/wiki/Linked_list
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
