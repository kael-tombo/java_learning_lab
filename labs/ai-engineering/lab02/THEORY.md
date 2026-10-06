# Lab 02: Vector Database Integration — Theory

## 1. The Retrieval Problem

Vector databases answer one question fast: given a query vector, which stored vectors
are most similar? Everything else — storage, filtering, durability, multi-tenancy,
updates — exists to make that answer trustworthy in production.

```
similarity_search(query_vec, k, filter?) -> [(id, score), ...]
```

## 2. Embeddings

An embedding model maps text (or an image, or audio) to a fixed-dimensional vector.
Properties that matter:

- **Fixed dimension** for a given model; dimensions are not interchangeable across models.
- **Normalization**: if vectors are L2-normalized, cosine similarity equals the dot
  product, so search reduces to one multiply-add per dimension.
- **Metric must match training**: a contrastive model trained with cosine degrades if
  you rank by squared L2 on unnormalized vectors (or vice versa).
- **Version pinning**: the embedding model version is part of the index namespace.
  Re-embedding is a full rebuild.

## 3. Distance Metrics

| Metric | Formula | Use when |
|--------|---------|----------|
| Cosine | `1 - (a·b)/(|a||b|)` | Normalized embeddings; most common |
| Dot product | `a·b` | Models trained with dot product (e.g. some LLM embedders) |
| L2 (squared) | `|a-b|^2` | Euclidean geometry, non-normalized data |
| Hamming | popcount | Binary/one-hot data (legacy) |
| Angular | `1 - cos` | Cosine expressed as distance |

Important identity: **for unit vectors, `|a-b|^2 = 2 - 2cos(a,b)`**, so ranking by
squared L2 is identical to ranking by cosine. Many vector DBs store L2 and return
correct cosine orderings for normalized input. This is worth verifying rather than
assuming.

## 4. Index Structures

### Flat (brute force)
Compute the distance to every vector. Exact, `O(n)` per query, and with SIMD and
quantization it is competitive up to roughly 10^6 vectors for low-latency workloads.

**The insight many teams miss**: flat search is often the *right* answer at moderate
scale. ANN indexes buy speed you may not need while costing recall and memory.

### IVF (inverted file)
Cluster vectors into `nlist` cells with k-means; store a list per cell. A query
computes distances only against the `nprobe` nearest cells.

```
recall falls as nprobe -> 1;  latency falls as nprobe grows down
trained once, then cheap queries
good for: large static corpora, high QPS, memory-constrained
```

### HNSW (hierarchical navigable small world)
A multi-layer proximity graph. Top layer is sparse (long hops); bottom layer is dense
(short hops). Search starts at the top and greedily descends.

```
M              edges per node per layer (16-64 typical)
efConstruction  candidate list size during build (200+)
efSearch        candidate list size during search (50-200)
recall rises with efSearch; latency rises roughly linearly
great recall/latency; heavy memory per vector (~M * 4 bytes/layer)
```

### IVF-PQ (product quantization)
Split the vector into subvectors and replace each with a centroid index from a small
codebook. Memory collapses (e.g. 768 dims -> 96 bytes) with a recall cost.

### Quantization-only indexes
Scalar quantization (int8) keeps full-vector search but shrinks storage 4x. Binary
quantization is more aggressive, usually combined with reranking.

### Comparison

| Index | Recall | Latency | Memory | Build | Best for |
|-------|--------|---------|--------|-------|----------|
| Flat | 1.0 | O(n) | 1.0x | none | <= 1M vectors, exactness needed |
| IVF | 0.9-0.99 | low | 1.0x | k-means | large static corpora |
| HNSW | 0.95-0.999 | very low | 1.3-2x | incremental | high-recall retrieval |
| IVF-PQ | 0.8-0.95 | very low | 0.1-0.3x | k-means + PQ | memory-bound scale |
| SQ (int8) | ~0.98 | O(n) | 0.25x | none | cheap exact-ish search |

## 5. Filtering

Metadata filters (`tenant`, `date`, `type`) must be applied *before* scoring, otherwise
unauthorized or irrelevant vectors influence the ranking.

Three strategies:
- **Pre-filter**: restrict the candidate set first, then search. Best for high selectivity.
- **Post-filter**: search then filter. Fast but can return fewer than k results.
- **Filtered HNSW**: traverse the graph but skip disallowed nodes. Works when the
  filter retains a connected subgraph; degrades badly when it fragments the graph.

**Rule of thumb**: pre-filter when selectivity < 10%; post-filter when > 50%. In
between, measure.

## 6. Multi-Tenancy

```
namespace = (tenant, corpusVersion, embeddingModelVersion)
```

Changing the embedding model or the corpus invalidates the namespace and requires a
full re-ingest. Get this wrong and you serve silently meaningless results — the vectors
from different models are not comparable, but nothing errors.

Options: separate namespaces (isolation, more resources), shared index with a mandatory
tenant field (cheaper, risk of leakage if the filter is missing), or hybrid.

## 7. Durability and Consistency

- Write path: upsert with a content hash; deletions as tombstones, not physical removes.
- Visibility: strict (read-your-writes per tenant) or eventual with a lag bound.
- Compaction: deleted pages must be reclaimed or storage grows monotonically.
- Backups: index rebuildable from the chunk store; the source of truth is the chunk
  store, not the index.

## 8. The Rerank Pattern

The two-stage design that gives the best quality/latency tradeoff:

```
ANN search (fast, recall 0.95)  ->  rerank top-50 with a cross-encoder  ->  top-5
```

Because rerankers are much more accurate but ~100x more expensive per pair, `k` is a
tuning parameter with a clear knee: quality flattens around k=20-50 while latency keeps
rising.

## 9. Failure Modes

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Silent garbage | All results irrelevant | Embedding model version mismatch | Namespace pinning + test |
| Too few results | k results returned < k requested | Post-filter with selective filter | Pre-filter |
| High latency at low traffic | p99 spikes | Index not warm / cold cache | Warmup |
| Memory growth | Slow degradation | No tombstone compaction | Compaction |
| Filter fragmentation | Recall collapses with filters | Post-filter on selective HNSW | Pre-filter |
| Duplicates near top | Repeated chunks | Near-duplicate chunks ingested | Ingest-time dedup |
| Rerank kills latency | p99 explodes | k too large | Lower k, batch, cheaper model |
| Cross-tenant leak | Unauthorized chunk retrieved | Filter optional in API | Mandatory tenant field |

## 10. Choosing an Index

```
<= 1M vectors, latency budget 50ms+     -> flat (exact, simple, no tuning)
> 1M, high recall needed                 -> HNSW
> 10M+, memory constrained               -> IVF-PQ or quantized HNSW + rerank
high filter selectivity                  -> pre-filter + flat/IVF
filter rarely applied                    -> HNSW with post-filter
strict exactness required               -> flat (no ANN)
```

**Always rerank.** If you take only one thing from this lab: ANN recall of 0.95 means
5% of the right answers are missing; a reranker over the top 50 recovers most of them
at a latency cost you can afford.

## Key Equations

```
cos(a,b) = (a·b) / (|a||b|)
|a-b|^2 = |a|^2 + |b|^2 - 2 a·b           -> for |a|=|b|=1: 2 - 2cos
recall@k = (1/|Q|) * sum_q [ gold_q ⊆ topk(q) ]
RRF(d)    = sum_r 1 / (60 + rank_r(d))
latency_ivf ~ nprobe * cellsize * dim * cost_distance
memory_hnsw ~ n * (M * layers * 4 bytes) + n * dim * bytes
```