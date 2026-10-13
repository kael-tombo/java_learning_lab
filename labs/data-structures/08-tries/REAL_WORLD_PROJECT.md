# REAL_WORLD_PROJECT — Tries

Production use-case: **autocomplete API for a search box**. Secondary: IP longest-prefix match table.

## 1. Problem statement
Serve prefix insert/suggest with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 suggest latency, throughput (ops/s), max heap, correctness bar (exact vs sorted-scan oracle).

## 2. Architecture
- Ingest: dictionary/corpus loader feeding the trie.
- Core: compressed trie behind a narrow interface.
- Serve: suggest API + metrics + health.
- Persist: serialized snapshot where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 suggest latency | define SLO | JMH / load test |
| p99 suggest latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | MB at N keys | JOL / heap dump |
| Correctness | exact vs sorted-scan oracle | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- Memory blowup -> radix compression + alphabet sizing.
- Skewed keys -> depth metric + rebuild policy.
- Unicode edge cases -> normalization + fuzz tests.
- Concurrency bugs -> copy-on-write reads + stress tests.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Trie
- https://en.wikipedia.org/wiki/Radix_tree
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
