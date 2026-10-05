# REAL_WORLD_PROJECT — Persistent Segment Trees (34)

Production use-case: **time-travel analytics over an event log** (query any historical snapshot in O(log n)). Secondary: MVCC-friendly counter service.

## 1. Problem statement
Support "as-of-version" range queries over append-heavy numeric streams with bounded per-update cost. SLOs: p99 query latency, memory per update, version retention policy.

## 2. Architecture
- Ingest: append/update commands with version stamps.
- Core: persistent segment tree behind a versioned interface.
- Serve: as-of query API + metrics + health.
- Persist: root table + node pool (GC old roots per retention).

## 3. Implementation plan (2 weeks)
W1: core + invariants + property tests vs naive snapshot baseline.
W2: API + metrics + JMH + retention/GC drill + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 as-of query | SLO-driven | JMH |
| Memory per update | O(log n) | JOL |
| Version retention | configurable | policy test |
| Throughput | updates/s | load gen |
| Correctness | matches snapshot model | property tests |

## 5. Risks & prevention
- Node-pool growth unbounded → retention window + root GC.
- Version-tree confusion → version IDs monotonic; query validates version exists.
- Pointer-sharing bugs after deletes → never mutate shared nodes.

## 6. Runbook
- Alert on node-pool heap pressure; force old-root eviction.
- Rollback: materialized snapshots for small datasets.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Persistent_data_structure
- https://cp-algorithms.com/data_structures/segment_tree.html
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
