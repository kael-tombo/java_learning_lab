# REAL_WORLD_PROJECT — Maps Deep

Production use-case: **session store / cache service** choosing the right map backend per workload. Secondary: a Bloom front-filter to cut disk reads.

## 1. Problem statement
Serve put/get/remove with p99 SLOs and consistent iteration semantics where needed.

## 2. Architecture
- Ingest: application requests.
- Core: pluggable Map backend (HashMap/TreeMap/LinkedHashMap/CHM).
- Serve: KV API + metrics.
- Persist: snapshot / WAL.

## 3. Implementation plan (2 weeks)
W1: core + parity tests.
W2: API + metrics + JMH + runbook + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 op latency | SLO | JMH |
| Throughput | ops/s | load gen |
| Iteration order correctness | matches spec | property tests |
| Memory | O(n) | JOL |
| Bloom FPR (if used) | < 1% | sampled |

## 5. Risks & prevention
- Long chains → widen capacity; watch load factor.
- TreeMap slow writes → move to HashMap if ordering isn't used.
- CHM iteration surprises → document weakly-consistent semantics.

## 6. Runbook
- Alerts on p99 and on unexpected ordering in iteration consumers.
- Rollback flag to HashMap backend.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo + JMH + runbook.

## 8. Grading rubric
- Correctness 30 / Perf 30 / Operability 20 / Writeup 20.
