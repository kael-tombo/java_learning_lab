# REAL_WORLD_PROJECT — Hash Tables

Production use-case: **session store / dedup ingest cache**. Secondary: frequency-counter sidecar for hot keys.

## 1. Problem statement
Serve O(1) put/get/delete with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 op latency, throughput (ops/s), max heap, correctness bar (exact vs HashMap oracle).

## 2. Architecture
- Ingest: session events / dedup keys feeding the table.
- Core: chained/open-addressed table behind a narrow interface.
- Serve: lookup API + hit-rate metrics + health.
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
| Correctness | exact vs HashMap oracle | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Hash flooding -> salted hashing / SipHash-style defense.
- Resize pauses -> incremental rehash or pre-sizing.
- Memory blowup -> load-factor caps + eviction.
- Concurrency bugs -> striped locks + stress tests.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/javase/8/docs/api/java/util/HashMap.html
- https://en.wikipedia.org/wiki/Hash_table
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
