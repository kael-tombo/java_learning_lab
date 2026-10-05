# REAL_WORLD_PROJECT — Link-Cut Trees (35)

Production use-case: **dynamic network-topology connectivity service** (e.g. SDN controller prototype). Secondary: path-max latency aggregation.

## 1. Problem statement
Answer connected(u,v) and link/cut at high rates with amortized O(log n). SLOs: p99 query latency, update throughput, memory.

## 2. Architecture
- Ingest: topology change events (link/cut).
- Core: LCT forest behind a narrow interface.
- Serve: connected/aggregate API + metrics + health.
- Persist: topology snapshot + WAL of mutations.

## 3. Implementation plan (2 weeks)
W1: core + invariants + property tests vs DFS baseline.
W2: API + metrics + JMH + restart drill + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 connect query | SLO-driven | JMH |
| Update throughput | ops/s | load gen |
| Memory | O(n) | JOL |
| Amortization validity | O(log n) mean | counter stats |
| Recovery | < 5 s | restart drill |

## 5. Risks & prevention
- Preferred-path corruption → invariant assertions in tests; round-trip property.
- Evert misuse (non-tree precondition) → document preconditions; boolean check.
- Splay worst-case spike → amortized budget + p99 alert; fallback naive BFS flag.

## 6. Runbook
- Alert on p99 drift and amortized budget overruns; manual DFS fallback.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Link%E2%80%93cut_tree
- https://www.cs.cmu.edu/~guyb/papers/SleatorTarjan85b.pdf
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
