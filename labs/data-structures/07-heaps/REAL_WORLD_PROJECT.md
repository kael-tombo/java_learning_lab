# REAL_WORLD_PROJECT — Heaps

Production use-case: **priority scheduler for background jobs**. Secondary: top-K trending stream over events.

## 1. Problem statement
Serve push/pop-max with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 op latency, throughput (ops/s), max heap, correctness bar (exact vs sorted oracle).

## 2. Architecture
- Ingest: job submissions / event stream feeding the heap.
- Core: binary heap with heapify behind a narrow interface.
- Serve: pop/top-K API + metrics + health.
- Persist: snapshot/WAL where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 op latency | define SLO | JMH / load test |
| p99 op latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at N entries | JOL / heap dump |
| Correctness | exact vs PriorityQueue oracle | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Starvation -> aging / priority boost policy.
- Duplicate keys -> tie-breaker comparator.
- Memory blowup -> bounded caps + eviction.
- Silent corruption -> heap-invariant audits.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/javase/8/docs/api/java/util/PriorityQueue.html
- https://en.wikipedia.org/wiki/Heap_(data_structure)
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
