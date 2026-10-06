# Lab 02: Vector Database Integration — Mini Project

## Project: In-Memory Vector Database with Hybrid Search

Build a vector database in Java 21 — flat, IVF, and HNSW indexes; scalar and product
quantization; pre/post filtering; namespaces; tombstones and compaction; a rerank
stage; and a benchmark harness — then pick an index with evidence.

## Goal

A searchable store with 1M vectors, hybrid dense+BM25 retrieval, a cross-encoder
rerank stage, per-tenant isolation, and a benchmark report justifying the index
configuration for two different corpus sizes.

## Requirements

### Phase 1: Core Math
- [ ] `Vector` with normalize, dot, cosine, squared L2.
- [ ] Unit-vector identity `|a-b|^2 = 2 - 2cos` verified numerically.
- [ ] Guard: reject zero vectors and dimension mismatches.

### Phase 2: Flat Index
- [ ] add/update/delete/tombstone; normalize at write time.
- [ ] Quickselect top-k rather than full sort; operation counts reported.
- [ ] Search returns true nearest neighbours.

### Phase 3: IVF
- [ ] k-means with k-means++ seeding; verify cell balance.
- [ ] `nprobe` sweep: recall@10 vs latency curve; identify the knee.
- [ ] Show that `nprobe=1` is unusable.

### Phase 4: HNSW
- [ ] Layered graph with `M`, `efConstruction`, `efSearch`, exponential level
      assignment.
- [ ] Degree-capped back-edges; verify recall@10 > 0.95.
- [ ] `efSearch` sweep with the knee marked.

### Phase 5: Compression
- [ ] int8 scalar quantization; bytes/vector and recall reported.
- [ ] PQ-8 (or PQ-64 with 6 bits) compression; same.
- [ ] Verify the recomposition error is within the expected bound.

### Phase 6: Filtering
- [ ] Pre-filter and post-filter implementations.
- [ ] Selectivity sweep 1% / 10% / 50% / 90%: result count, recall, latency.
- [ ] Filtered HNSW traversal; node-visit counts reported.
- [ ] Post-filter over-fetch measured and shown to be worse than pre-filter.

### Phase 7: Namespaces and Isolation
- [ ] Namespace = `(tenant, corpusVersion, embedVersion)`; required in the API.
- [ ] Randomized cross-tenant isolation test.
- [ ] Verify that changing `embedVersion` requires a new namespace.

### Phase 8: Durability
- [ ] Content-hash upserts; second ingest inserts zero vectors.
- [ ] Tombstones plus compaction; measure reclaimed storage.
- [ ] Persist/restore index state.

### Phase 9: Hybrid Search and Rerank
- [ ] BM25 index over the same corpus.
- [ ] Weighted normalized fusion and RRF; compare on identifier-heavy queries.
- [ ] Rerank stage (term overlap + proximity) over the top 50.
- [ ] Report the ANN recall ceiling effect explicitly.

### Phase 10: Benchmark and Selection
- [ ] 1k / 10k / 100k / 1M corpora; flat, IVF, HNSW, quantized variants.
- [ ] recall@1/5/10, p50/p99 latency, memory, build time.
- [ ] Select an index for 100k and for 1M with a written justification.

## Directory Layout

```
lab02/
  src/com/aiengineering/lab02/{vec,index,filter,namespace,store,rerank,eval,bench}/
  out/bench/results.csv
  out/bench/selection.md
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — core math; identity verified.
2. **M2** — flat index; top-k via quickselect; exact results.
3. **M3** — IVF built; `nprobe` sweep with the knee.
4. **M4** — HNSW recall > 0.95 at default parameters.
5. **M5** — `efSearch` sweep; memory per vector computed.
6. **M6** — quantization; recall and memory deltas reported.
7. **M7** — filtering sweep; pre-filter chosen for low selectivity.
8. **M8** — namespaces; isolation test green.
9. **M9** — idempotent ingest and compaction verified.
10. **M10** — hybrid search beats dense-only on identifier queries.
11. **M11** — rerank stage; recall ceiling demonstrated.
12. **M12** — full benchmark table; index selected with justification.

## Acceptance Criteria

- [ ] Flat search returns true nearest neighbours.
- [ ] Quickselect reduces operation count versus full sort.
- [ ] HNSW recall@10 > 0.95 with default parameters on 100k vectors.
- [ ] `nprobe` and `efSearch` sweeps show a knee; the knee is used.
- [ ] int8 reduces memory ~4x with recall within 0.03 of fp32.
- [ ] Pre-filter returns exactly k results at 1% selectivity; post-filter does not.
- [ ] Cross-tenant isolation test passes; it fails if the namespace is removed.
- [ ] Second ingest inserts zero vectors.
- [ ] Compaction reclaims deleted storage.
- [ ] Rerank improves recall@5; the ANN ceiling is measured and stated.
- [ ] Index selected per corpus size with a written reason.

## Stretch Goals

- [ ] Binary quantization plus exact reranking; quality/latency frontier.
- [ ] Neighbor pruning beyond `M` at fixed latency.
- [ ] Incremental vs batch index building; recall and build-time comparison.
- [ ] Disk-backed index with cold vs warm latency.
- [ ] Query result cache with a hit rate on a realistic distribution.
- [ ] Concurrent search throughput with per-thread buffers.
- [ ] Cross-encoder stand-in with a tuned weight for proximity vs overlap.
- [ ] k-means++ vs random seeding comparison on cell balance.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Recall collapses at 1% selectivity | Post-filter without over-fetch |
| HNSW recall low | Back-edges not degree-capped, or `efSearch` too low |
| IVF cells very unbalanced | Random k-means seeding |
| Search slower than flat | Index overhead exceeds savings at small n |
| Compression changes rankings | Vector reconstruction error not accounted for |
| Cross-tenant hit | Namespace missing from a search call |
| Storage grows after deletes | Compaction not run |
| Second ingest duplicates | Upsert not keyed on content hash |
| Rerank adds latency with no gain | k too large, or the reranker is weak |

## Definition of Done

`REPORT.md` contains: the search stack diagram, the distance identity verification, the
flat-vs-ANN cost analysis, IVF and HNSW parameter sweeps with knees marked, memory per
vector for every configuration, the filtering sweep table, the isolation test result,
the compaction measurement, the hybrid fusion comparison, the rerank result with the
ANN ceiling stated, the full benchmark table for 1k/10k/100k/1M, and the index
selection for two corpus sizes with justification.