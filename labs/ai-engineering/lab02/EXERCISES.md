# Lab 02: Vector Database Integration — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Distance Metrics (E)

Implement cosine, dot product, squared L2, and angular distance. Verify the identity
`|a-b|^2 = 2 - 2cos` for unit vectors.

**Verify**: identical vectors give cosine 1.0, L2 0.0; orthogonal vectors give cosine 0.0.

---

## Exercise 2: Normalization and the Dot-Product Fast Path (E)

Implement `normalize` and verify `cos(a,b) == dot(a_hat, b_hat)` within 1e-9.

**Verify**: after normalization the flat search uses a single dot-product loop.

---

## Exercise 3: In-Memory Flat Index (E)

Build `FlatIndex` with add/update/delete and top-k search. Use quickselect + partial
sort rather than a full sort.

**Verify**: returns the true nearest neighbours; a deletion removes the vector.

---

## Exercise 4: Top-K Selection (M)

Implement quickselect-based top-k and compare against full sort for correctness and
operation count.

**Verify**: identical results; report the operation-count reduction.

---

## Exercise 5: Recall@k Harness (E)

Given 100 queries with gold ids, compute recall@1/5/10 and MRR@10 for an index
configuration.

**Verify**: recall is non-decreasing in k.

---

## Exercise 6: IVF Index (H)

Implement k-means training, cell assignment, and search with `nprobe`. Sweep
`nprobe` and plot recall@10 vs latency.

**Expected**: a clear knee; below it recall collapses.

---

## Exercise 7: HNSW Index (H)

Implement layered HNSW: insertion with `M`/`efConstruction`, greedy search with
`efSearch`, layer assignment by an exponentially decaying probability.

**Verify**: recall@10 > 0.95 with default parameters on 10k vectors.

---

## Exercise 8: HNSW Parameter Sweep (M)

Sweep `efSearch` in {16, 32, 64, 128, 256} and report recall@10, latency, and
operations. Mark the knee.

---

## Exercise 9: Quantization (M)

Implement int8 scalar quantization and PQ-8 compression. Report memory per vector and
recall@10 for each.

---

## Exercise 10: Filtering: Pre vs Post (H)

Add a `tenant` and a `year` filter. Implement pre-filter and post-filter variants and
compare recall, result count, and latency across selectivity levels.

**Expected**: post-filter returns fewer than k at high selectivity.

---

## Exercise 11: Filtered HNSW Traversal (H)

Implement HNSW traversal that skips disallowed nodes. Measure recall degradation as
filter selectivity increases.

**Expected**: graceful until the graph fragments, then collapse.

---

## Exercise 12: Multi-Tenancy Namespaces (M)

Implement namespaces keyed by `(tenant, corpusVersion, embedVersion)`. Write a test
that inserting into one namespace is invisible from another, and that changing the
embed version requires a rebuild.

---

## Exercise 13: Upsert and Tombstones (M)

Implement content-hash upserts and tombstones, plus compaction that reclaims deleted
pages.

**Verify**: a re-ingest of unchanged data inserts zero vectors.

---

## Exercise 14: Two-Stage Rerank (H)

Implement a cross-encoder-style reranker (term overlap + proximity heuristic) over the
top-50 and report the recall@5 delta and added latency.

---

## Exercise 15: Duplicate Suppression (M)

Detect and suppress near-duplicate chunks in results using an `inflateThreshold`
comparator (not a fixed epsilon).

**Verify**: repeated chunks appear once.

---

## Exercise 16: Index Benchmark Harness (H)

Benchmark flat, IVF, and HNSW across corpus sizes 1k/10k/100k/1M for recall@10 and
p50/p99 latency. Produce the comparison table.

---

## Exercise 17: Warmup and Cold Cache (M)

Measure cold vs warm query latency; implement a warmup routine over representative
queries.

---

## Exercise 18: Concurrent Search (H)

Run concurrent queries with a shared immutable index and per-thread buffers; verify
throughput scales and no corruption occurs.

---

## Stretch A: Disk-Backed Index (H)

Persist an index to disk with mmap-style reads; measure cold-start vs warm latency.

---

## Stretch B: Binary Quantization + Rerank (H)

Implement 1-bit-per-dimension quantization, retrieve with Hamming, rerank with exact
distances; report the quality/latency frontier.

---

## Stretch C: Graph Compression (H)

Implement HNSW neighbor pruning beyond `M` and measure recall/memory at fixed latency.

---

## Stretch D: Online/Incremental Indexing (M)

Insert vectors into HNSW continuously; measure the effect on recall and build time
versus batch builds.

---

## Stretch E: Query Caching (M)

Implement a query cache; measure the hit rate on a realistic query distribution and
the latency improvement.

---

## Stretch F: Hybrid Search (H)

Combine BM25 and dense retrieval with weighted fusion and RRF; measure the recall gain
on identifier-heavy queries.