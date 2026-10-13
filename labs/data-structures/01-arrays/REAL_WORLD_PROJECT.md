# REAL_WORLD_PROJECT — Arrays & Dynamic Arrays

Production use-case: **in-memory column buffer for a batch analytics CLI**. Secondary: ring-backed log tail with amortized-resize budget.

## 1. Problem statement
Serve range scans and appends over a growing `DynamicArray` with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 append and scan latency, max heap, amortized resize cost per append.

## 2. Architecture
- Ingest: CSV/batch loader appending rows to the column buffer.
- Core: dynamic array with doubling resize behind a narrow interface.
- Serve: scan/filter CLI + metrics + health.
- Persist: snapshot to file where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: CLI + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 append latency | define SLO | JMH / load test |
| p99 scan latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at N entries | JOL / heap dump |
| Correctness | exact vs ArrayList oracle | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Resize pauses -> doubling schedule + capacity pre-sizing.
- Memory blowup -> bounded caps + trim-to-size.
- Scan degradation -> cache-friendly layout audits.
- Silent corruption -> checksums + invariant audits.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/javase/8/docs/api/java/util/ArrayList.html
- https://en.wikipedia.org/wiki/Dynamic_array
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
