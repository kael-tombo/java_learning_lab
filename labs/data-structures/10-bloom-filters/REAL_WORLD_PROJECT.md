# REAL_WORLD_PROJECT — Bloom Filters

Production use-case: **disk-pre-check layer in front of an LSM store**. Secondary: crawler URL dedup front-filter.

## 1. Problem statement
Serve add/mightContain with a measured false-positive rate with a latency SLO and a memory budget.
Define SLOs up front: p50/p99 query latency, throughput (ops/s), m/k sizing, correctness bar (zero false negatives + FPR vs theory).

## 2. Architecture
- Ingest: key stream (SSTable keys / crawled URLs).
- Core: BitSet with k hashes behind a narrow interface.
- Serve: pre-check API + FPR metrics + health.
- Persist: bit-array snapshot where durability matters.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests.
W2: API + metrics (Micrometer/JFR) + load test (JMH) + deploy notes.

## 4. Metrics to report

| Metric | Target | How measured |
|---|---|---|
| p50 query latency | define SLO | JMH / load test |
| p99 query latency | define SLO | hdrhistogram |
| Throughput | ops/s | load generator |
| Memory | bits per key | JOL / heap dump |
| Correctness | FPR vs (1-e^(-kn/m))^k | property tests |
| Availability | restart recovery time | chaos/restart drill |

## 5. Risks & mitigations
- FPR drift as n grows -> capacity sizing + rebuild policy.
- Hash correlation -> double-hashing audit.
- No deletes -> counting variant or rebuild.
- Silent saturation -> fill-ratio alert.

## 6. Field notes
Sourced field notes (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Bloom_filter
- https://docs.oracle.com/javase/8/docs/api/java/util/BitSet.html
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
