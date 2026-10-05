# REAL_WORLD_PROJECT — Advanced Trees (Deep)

Production use-case: **an ordered index service** — leaderboard / time-series snapshot queries. Secondary: a prefix-search module on top of tries.

## 1. Problem statement
Serve add/remove/query with a target p99 latency; pick the structure via SLOs. SLOs: p99 latency, throughput, memory.

## 2. Architecture
- Ingest: mutation stream.
- Core: pluggable OrderedSet interface.
- Serve: query API + metrics + health.
- Persist: snapshot / WAL.

## 3. Implementation plan (2 weeks)
W1: interface + one backend + parity tests.
W2: pluggable backends + JMH + runbook + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 op latency | SLO | JMH |
| Throughput | ops/s | load gen |
| Memory | O(n) overhead | JOL |
| Invariant holds | 100% tests | parity checker |
| Recovery | < 5 s | restart drill |

## 5. Risks & prevention
- Wrong structure for workload → run SLO-driven pick table.
- Invariant drift → parity tests vs TreeMap.
- Worst-case splay latency → cap or provide fallback.

## 6. Runbook
- Alert on p99 drift; rollback flag to TreeMap.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html
- https://en.wikipedia.org/wiki/Red%E2%80%93black_tree
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo + JMH + runbook.

## 8. Grading rubric
- Correctness 30 / Perf 30 / Operability 20 / Writeup 20.
