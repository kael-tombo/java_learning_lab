# REAL_WORLD_PROJECT — Ropes (31)

Production use-case: **large-buffer text service** (editor backend or log viewer) with heavy middle edits. Secondary: concat-heavy document store benchmark.

## 1. Problem statement
Support concat/split/edit on multi-MB buffers with bounded per-op latency. SLOs: p99 edit latency, throughput of edits/s, memory overhead per leaf.

## 2. Architecture
- Ingest: edit commands (concat/split/insert/delete).
- Core: rope with cursor persistence.
- Serve: render API + metrics + health.
- Persist: serialized leaf table + parent index.

## 3. Implementation plan (2 weeks)
W1: core + invariants + property tests vs String model.
W2: API + metrics + JMH + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p99 edit latency | SLO-driven | JMH |
| Edit throughput | ops/s | load gen |
| Memory overhead | ≤ 2x payload | JOL |
| Render traversal | O(n) once | unit bench |
| Cursor correctness | exact | property tests |

## 5. Risks & prevention
- Degeneration after many splits → rebalance when depth > c·log n.
- charAt hot path O(depth) → expose cursor/iterator API.
- Memory fragmentation from tiny leaves → cap leaf size and merge on concat.

## 6. Runbook
- Alert on p99 edit latency and depth-growth after splits.
- Rollback: contiguous buffer mode for small docs.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Rope_(data_structure)
- (link removed)
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
