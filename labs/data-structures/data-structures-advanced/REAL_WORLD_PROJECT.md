# REAL_WORLD_PROJECT — Data Structures Advanced

Production use-case: **telemetry service** computing rolling counters, membership probes, and integrity-tagged snapshots. Secondary: pattern search over a text corpus.

## 1. Problem statement
Handle a mixed stream of range queries, membership probes, and integrity-tagged events with p99 SLOs.

## 2. Architecture
- Ingest: telemetry consumers.
- Core: Fenwick/segment tree/Bloom/Merkle behind a narrow interface.
- Serve: query API + metrics + health.
- Persist: WAL + periodic snapshot.

## 3. Implementation plan (2 weeks)
W1: core + parity tests.
W2: API + metrics + JMH + restart drill + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 query latency | SLO | JMH |
| Throughput | updates/s | load gen |
| Bloom FPR | < 1% | sampled |
| Parity with baseline | 100% | property test |
| Recovery | < 5 s | restart |

## 5. Risks & prevention
- Fenwick overflow → use long and checked adds.
- Segment-tree lazy loss → push on visit; test with random updates.
- Bloom false-positive surge → size for capacity with margin; monitor FPR.

## 6. Runbook
- Alerts on parity mismatch and FPR drift; rollback flags to baseline structures.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Fenwick_tree
- https://en.wikipedia.org/wiki/Bloom_filter
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo + JMH + runbook.

## 8. Grading rubric
- Correctness 30 / Perf 30 / Operability 20 / Writeup 20.
