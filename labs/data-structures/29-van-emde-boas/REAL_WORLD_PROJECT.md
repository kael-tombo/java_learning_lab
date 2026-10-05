# REAL_WORLD_PROJECT — van Emde Boas Trees (29)

Production use-case: **fast predecessor scheduling** (e.g. timer wheels, route matching with bounded prefix space). Secondary: benchmark vs TreeSet at various universe sizes.

## 1. Problem statement
Serve pred/succ queries on keys drawn from a bounded universe with sub-logarithmic latency. SLOs: p99 pred latency, ops/s, memory, correctness (exact answers).

## 2. Architecture
- Ingest: event/timer stream.
- Core: vEB tree behind a narrow interface.
- Serve: query API + metrics + health.
- Persist: key snapshot for restart.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + property tests.
W2: API + metrics + JMH + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 pred latency | < 300 ns | JMH |
| Throughput | ops/s | load generator |
| Memory | MB at capacity | JOL |
| Correctness | exact | property tests |
| Recovery | < 5 s | restart drill |

## 5. Risks & prevention
- Universe blowup (u huge) → sparse universe: y-fast or hash-mapped clusters.
- Recursion depth bugs → bound recursion; test u=2 base cases.
- min/max stale after deletes → assert via reference set in tests.
- Filling u=2^32 → never allocate full array; use lazy allocation.

## 6. Runbook
- Alert on p99 > 300 ns and on capacity > 70%.
- Rollback: TreeSet exact structure for correctness path.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Van_Emde_Boas_tree
- https://ocw.mit.edu/courses/6-851-advanced-data-structures-spring-2012/
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
