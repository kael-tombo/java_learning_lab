# REAL_WORLD_PROJECT — Graphs

Production use-case: **route planner over a transit network**. Secondary: build-dependency graph with cycle reporting.

## 1. Problem statement
Serve shortest-path and traversal queries at scale with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 query latency, throughput (ops/s), max heap, correctness bar (exact vs reference BFS/Dijkstra).

## 2. Architecture
- Ingest: edge feeds (transit timetables / dependency manifests).
- Core: adjacency-list graph with BFS/Dijkstra behind a narrow interface.
- Serve: route API + metrics + health.
- Persist: edge snapshot where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 query latency | define SLO | JMH / load test |
| p99 query latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at V+E scale | JOL / heap dump |
| Correctness | exact vs reference impl | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Disconnected input -> component census + degraded answers.
- Negative weights -> validation + Bellman-Ford fallback.
- Memory blowup -> adjacency compression + caps.
- Silent corruption -> checksums + invariant audits.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Graph_traversal
- https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
