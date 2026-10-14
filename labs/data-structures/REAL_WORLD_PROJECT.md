# Data Structures Track - Real World Project

## Intent
Produce one service with production habits around a single track
structure, carrying explicit SLOs, at broader scope than a lab build.

## Lanes (home lab in brackets)
- **Caching** [15]: thumbnail/session LRU with a hit-rate SLO; compare
  against an LFU variant. Shard locks for concurrent access.
- **Indexing** [09/17]: ordered catalog index or geo-fence search over
  a grid/quadtree; range and prefix timings beside TreeMap.
- **Streaming** [13/26/27/28]: Fenwick live counters, Count-Min heavy
  hitters, HyperLogLog distinct counts, MinHash near-dup filtering.
- **Integrity** [10/20/22/34]: Merkle proofs for file sync, Bloom
  pre-checks trimming disk reads, versioned structures for audit trails.
- **Solvers** [23/32/35]: exact-cover scheduling, rollback-DSU offline
  connectivity, link-cut dynamic forest queries.

## Ship requirements
- SLO sheet written first: latency distribution, throughput, memory
  ceiling, and the exactness bar each structure owes (exact or bounded).
- Workload driver plus operation log (CSV with nanos and sizes).
- Hot-path microbench with warmup and medians; heap-based memory notes.
- Ops page: start, alerts, rollback; hostile pass (empty input, dup
  flood, adversarial order, restart recovery).

## Fortnight shape
- Days 1-2: SLO sheet agreed; core plus invariant checks compiling.
- Days 3-5: oracle-tested core; workload driver running seeded.
- Days 6-8: serving surface, operation log, first load numbers.
- Days 9-10: hostile pass recorded, ops page reviewed, demo rehearsed.

## Tooling hints
- CLI or JDK built-in HTTP server; no frameworks needed.
- CSV logs plus a summary script; heap deltas for memory.
- Fixtures seeded so report numbers reproduce bit-for-bit.

## Scoring
- Correctness 12 / SLO evidence 10 / Operability 8. Ship at 24 or more.
