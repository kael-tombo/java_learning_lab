# REAL_WORLD_PROJECT — LRU Cache (HashMap + Doubly-Linked List)

Production use-case: **HTTP response / thumbnail cache for a web service**. Secondary: database query-result cache with hit-rate SLO.

## 1. Problem statement
Serve o(1) get/put with eviction workload at scale with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 latency, throughput (ops/s), max heap, correctness bar (exact vs error-bounded).

## 2. Architecture
- Ingest: parsers/queues feeding the structure.
- Core: this lab's structure behind a narrow interface.
- Serve: query API + metrics + health.
- Persist: snapshot/WAL where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 query latency | define SLO | JMH / load test |
| p99 query latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at N entries | JOL / heap dump |
| Correctness | exact or error bound | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Degenerate input -> randomization/rehash/rebalance.
- Concurrency bugs -> narrow sync + stress tests.
- Memory blowup -> bounded caps + eviction.
- Silent corruption -> checksums + invariant audits.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Cache_replacement_policies
- https://docs.oracle.com/javase/8/docs/api/java/util/LinkedHashMap.html
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
