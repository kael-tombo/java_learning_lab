# Data Structures Track — Real World Project

## Goal
Ship a production-flavored service around one track structure with SLOs,
mirroring the per-lab REAL_WORLD_PROJECT.md format at larger scope.

## Pick a lane (with home lab)
- **Caching**: LRU (15) thumbnail/session cache with hit-rate SLO; LFU
  variant comparison. Concurrent access via sharded locks.
- **Indexing**: B-tree-style ordered index (09) or spatial grid/quadtree
  (17) for geo-fence search; range/prefix benchmarks vs TreeMap.
- **Streaming analytics**: Fenwick (13) live counters, Count-Min (27) heavy
  hitters, HyperLogLog (26) distinct counts, MinHash (28) near-dup filter.
- **Integrity & sync**: Merkle tree (22) file-sync proofs; Bloom filter
  (10) pre-check cutting disk reads; persistent versions (20/34) for audit.
- **Solvers & dynamic graphs**: dancing-links exact cover (32), rollback
  DSU offline connectivity (23), link-cut dynamic forest (35).

## Requirements
- SLO sheet first: p50/p99 latency, throughput, memory cap, correctness
  bar (exact vs stated error bound per structure).
- Load generator + metrics (Micrometer/JFR or CSV + HDR-style summary).
- JMH microbench of the hot path; heap/JOL memory accounting.
- Ops runbook: deploy, alerts, rollback; chaos pass (empty, dup flood,
  adversarial order, restart recovery).

## Milestones (2 weeks)
W1: core + invariant checker + unit/property tests with oracle.
W1 also: SLO sheet signed off; load generator skeleton running.
W2: API + metrics + load test + deploy notes + demo script.
W2 also: chaos pass recorded; runbook reviewed against live behavior.

## Suggested stack
- Plain CLI or `com.sun.net.httpserver`; JMH for the hot path.
- CSV metrics + HDR-style summary; JOL for memory accounting.
- Seeded fixtures so every run in the report reproduces bit-for-bit.

## Grading
- Correctness 30 / Perf vs SLO 30 / Operability 20 / Writeup 20.
