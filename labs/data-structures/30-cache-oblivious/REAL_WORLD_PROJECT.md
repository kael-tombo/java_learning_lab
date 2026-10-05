# REAL_WORLD_PROJECT — Cache-Oblivious Structures (30)

Production use-case: **layout for a read-mostly in-memory index** scanned by heterogeneous clients (unknown cache sizes). Secondary: funnelsort microservice for log batches.

## 1. Problem statement
Minimize block transfers across unknown hardware tiers while keeping build simple. SLOs: p99 lookup latency across cache sizes, build time, footprint.

## 2. Architecture
- Ingest: bulk loader of keys.
- Core: vEB static layout or cache-oblivious search structure.
- Serve: lookup API + metrics + health.
- Persist: serialized layout.

## 3. Implementation plan (2 weeks)
W1: layout builder + iterator + property tests vs sorted array.
W2: JMH bench across L1/L2/L3 regimes + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 lookup | SLO-driven | JMH |
| Build time | linearithmic | unit bench |
| Footprint | ~ n keys | runtime.mem |
| Cache misses proxy | lower than row-major | perf counters if available |
| Throughput | lookups/s | load gen |

## 5. Risks & prevention
- Implementation bias on one machine → test on multiple tiers; use rank-based validation.
- Dynamic updates break static layout → use rebuild windows or cache-oblivious dynamic structures.
- Naive recursion overhead → cutoff base cases (e.g. subtree ≤ 16 nodes).

## 6. Runbook
- Alert on p99 regressions after deploy; keep row-major fallback flag.
- Rollback: switch index layout at config flag.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Cache-oblivious_algorithm
- https://ocw.mit.edu/courses/6-851-advanced-data-structures-spring-2012/
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
