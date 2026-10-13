# REAL_WORLD_PROJECT — Trees (BST & Traversals)

Production use-case: **ordered index with range scan for a catalog service**. Secondary: org-chart traversal API.

## 1. Problem statement
Serve ordered insert/lookup/range-scan with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 query latency, throughput (ops/s), max heap, correctness bar (exact vs TreeMap oracle).

## 2. Architecture
- Ingest: catalog writes feeding the tree.
- Core: BST with traversal orders behind a narrow interface.
- Serve: range-scan API + metrics + health.
- Persist: snapshot/WAL where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 query latency | define SLO | JMH / load test |
| p99 query latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at N entries | JOL / heap dump |
| Correctness | exact vs TreeMap oracle | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Degenerate input -> self-balancing variant or shuffle.
- Adversarial order -> rotation audits + height metric.
- Memory blowup -> bounded caps + node budget.
- Silent corruption -> BST invariant audits.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/javase/8/docs/api/java/util/TreeMap.html
- https://en.wikipedia.org/wiki/Binary_search_tree
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
