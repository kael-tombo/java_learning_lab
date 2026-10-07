# REAL_WORLD_PROJECT — Dancing Links (32)

Production use-case: **constraint solver backend** (scheduling, tiling, packaging). Secondary: SAT-solver-style exact-cover benchmark.

## 1. Problem statement
Solve exact-cover instances with many columns/rows under latency SLOs; provide exact counts for decision queries.

## 2. Architecture
- Ingest: problem matrix builder (Sudoku, scheduling, tiling).
- Core: DLX solver with MRV + node budget.
- Serve: solve API + metrics + health.
- Persist: problem spec + solution log.

## 3. Implementation plan (2 weeks)
W1: core + invariant tests + round-trip property.
W2: API + metrics + JMH + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 solve latency | SLO-driven | JMH |
| Nodes explored | minimal vs naive | counter |
| Throughput | solves/s | load gen |
| Memory | matrix size | JOL |
| Budget aborts | counted | node cap |

## 5. Risks & prevention
- Worst-case exponential search → node budget + timeout; return UNSAT-with-budget.
- Cover/uncover asymmetry bug → property-test round-trips; assert column counts.
- Memory blowup on wide matrices → sparse cell lists only.

## 6. Runbook
- Alert on node-budget abort rate and latency drift.
- Rollback: naive backtracking reference solver for small instances.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Dancing_links
- (link removed)
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
