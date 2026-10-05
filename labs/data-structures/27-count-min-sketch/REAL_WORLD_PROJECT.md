# REAL_WORLD_PROJECT — Count-Min Sketch (27)

Production use-case: **high-cardinality frequency estimation in an event pipeline** (e.g. per-endpoint request counters feeding an autoscaler). Secondary: RedisBloom-compatible Count-Min benchmark.

## 1. Problem statement
Estimate item frequencies over a firehose stream with a strict memory budget and bounded false inflation. SLOs: p50/p99 update latency, ops/s, max heap, error bound (ε with confidence δ).

## 2. Architecture
- Ingest: Kafka consumers feeding the sketch.
- Core: sketch behind a narrow interface (add/estimate/merge).
- Serve: query API + metrics + health.
- Persist: snapshot/WAL of counters for restart continuity.

## 3. Implementation plan (2 weeks)
W1: core + invariant checker + unit/property tests + merge commutativity test.
W2: API + Micrometer/JFR metrics + JMH load test + deploy notes.

## 4. Metrics to report
| Metric | Target | How measured |
|---|---|---|
| p50 update latency | < 200 ns | JMH |
| p99 update latency | < 1 µs | hdrhistogram |
| Throughput | ≥ 1M ops/s | load generator |
| Memory | ≤ 8 MB | JOL / heap dump |
| Error bound | ≤ εN w.p. 1−δ | property test |
| Restart recovery | < 5 s | chaos drill |

## 5. Risks & prevention
- Heavy-tail blowup → widen w, add heavy-hitter heap, monitor ε̂.
- Hash-function bias → use seeded independent hashes; test uniformity.
- Merge mismatch (w,d,seeds differ) → version the config; reject mismatched merges.
- Clock/ordering assumptions → keep sketch commutative; never rely on order.

## 6. Runbook
- SLOs in Grafana; alert on p99 > 1 µs and estimate-vs-sampled-exact drift > 5%.
- Rollback: revert to HashMap-based exact counter for small keysets.
- On-call: check heap cap, reset sketch on config change.

## Field notes — sourced (fetched Oct 2026 — verify before citing)
- https://en.wikipedia.org/wiki/Count-min_sketch
- https://redis.io/docs/data-types/probabilistic/
Confirm API/limit numbers against the live docs before quoting them in reviews.

## 7. Deliverables
- Repo with tests + JMH bench + dashboard screenshot.
- One-page ops runbook: SLOs, alerts, rollback.
- Demo script with seeded load.

## 8. Grading rubric
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
