# REAL_WORLD_PROJECT — Advanced Trees (AVL / Red-Black / B-Tree)

Production use-case: **ordered index with range scan for a catalog**. Secondary: interval map for reservation windows.

## 1. Problem statement
Serve balanced insert/lookup/range-scan with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 op latency, throughput (ops/s), max heap, correctness bar (exact vs TreeMap oracle).

## 2. Architecture
- Ingest: catalog writes feeding the balanced tree.
- Core: AVL/red-black tree with rotation counters behind a narrow interface.
- Serve: range-scan API + height metrics + health.
- Persist: snapshot/WAL where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 op latency | define SLO | JMH / load test |
| p99 op latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at N entries | JOL / heap dump |
| Correctness | exact vs TreeMap oracle | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Rotation bugs -> color/height invariant audits.
- Adversarial order -> rotation-count metric.
- Memory blowup -> node budget + caps.
- Concurrency bugs -> narrow sync + stress tests.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/AVL_tree
- https://en.wikipedia.org/wiki/Red%E2%80%93black_tree
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
