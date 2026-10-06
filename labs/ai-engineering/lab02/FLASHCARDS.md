# Lab 02: Vector Database Integration — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Vector DB's job | Similarity search, plus everything to make it trustworthy |
| 2 | Embedding | Fixed-dimension vector from text/image/audio |
| 3 | Dimension | Fixed per model; not interchangeable across models |
| 4 | L2 normalization | Makes cosine equal to the dot product |
| 5 | Metric must match training | Cosine-trained models degrade under raw dot product |
| 6 | Cosine | `a·b / (|a||b|)`, range [-1,1] |
| 7 | Dot product | `a·b`; correct for dot-trained embedders |
| 8 | Squared L2 | `|a-b|^2`; expands to `|a|^2+|b|^2-2a·b` |
| 9 | Unit-vector identity | `|a-b|^2 = 2 - 2cos` -> L2 ranking equals cosine ranking |
| 10 | Angular | `1 - cos`, cosine as a distance |
| 11 | Flat index | Brute force, exact, O(n) |
| 12 | Flat scale limit | Roughly 1M vectors for a 50ms budget |
| 13 | Flat advantage | No tuning, exact, often correct answer |
| 14 | IVF | k-means cells; probe `nprobe` nearest |
| 15 | IVF params | `nlist` (cells), `nprobe` (searched) |
| 16 | IVF recall/latency | Higher `nprobe` -> better recall, higher latency |
| 17 | IVF requires | A training pass before serving |
| 18 | IVF best for | Large static corpora, high QPS |
| 19 | HNSW | Layered navigable small world graph |
| 20 | HNSW layers | Sparse top (long hops), dense bottom (short hops) |
| 21 | HNSW `M` | Edges per node per layer (16-64) |
| 22 | HNSW `efConstruction` | Build-time candidate list (200+) |
| 23 | HNSW `efSearch` | Search-time candidate list (50-200) |
| 24 | HNSW recall | 0.95-0.999; strong by default |
| 25 | HNSW cost | Memory ~`M * layers * 4` bytes per vector |
| 26 | Layer assignment | Exponential decay: `P(level) = 1/mult * P(level-1)` |
| 27 | IVF-PQ | Subvectors replaced by codebook indices |
| 28 | PQ memory | 768 dims -> ~96 bytes; 8x reduction |
| 29 | Scalar quantization | int8; 4x memory, small recall loss |
| 30 | Binary quantization | 1 bit/dim; needs reranking |
| 31 | Pre-filter | Filter before scoring |
| 32 | Post-filter | Search then discard |
| 33 | Pre-filter threshold | Selectivity < 10% |
| 34 | Post-filter threshold | Selectivity > 50% |
| 35 | Filtered HNSW | Traverse graph, skip disallowed nodes |
| 36 | Graph fragmentation | Selective filters disconnect HNSW; recall collapses |
| 37 | Namespace | `(tenant, corpusVersion, embedVersion)` |
| 38 | Why namespace | Mixing embedding spaces fails silently |
| 39 | Shared index risk | Tenant filter must be mandatory, not optional |
| 40 | Source of truth | Chunk store; index is derived |
| 41 | Upsert | Content hash; identical content is a no-op |
| 42 | Tombstone | Logical delete |
| 43 | Compaction | Reclaims deleted pages |
| 44 | No compaction | Storage grows monotonically; reads slow down |
| 45 | Strict consistency | Read-your-writes per tenant |
| 46 | Eventual consistency | Lagged visibility with a bound |
| 47 | Rerank | Cross-encoder over query+document jointly |
| 48 | Rerank `k` | 20-50; quality flattens, latency linear |
| 49 | Always rerank | Recovers the 5% ANN misses |
| 50 | recall@k | Gold id present in top k, averaged over queries |
| 51 | MRR@10 | Mean reciprocal rank of the first hit |
| 52 | nDCG | Rank-discounted, graded relevance |
| 53 | inflateThreshold | Duplicate comparator with relative tolerance |
| 54 | Naive duplicate check | Fixed epsilon flags too many items |
| 55 | Cold cache | First queries slow; warmup needed |
| 56 | Warmup | Run representative queries after start |
| 57 | Concurrency | Immutable index + per-thread buffers |
| 58 | Shared mutation | Unsafe; copy-on-write or lock |
| 59 | BM25 strength | Exact tokens, ids, codes |
| 60 | Dense strength | Paraphrase |
| 61 | Hybrid fusion | Weighted normalized or RRF |
| 62 | RRF | Rank-based; no score calibration |
| 63 | Index choice rule | Flat < 1M; HNSW high recall; IVF-PQ at memory limits |
| 64 | Exactness required | Flat; no ANN |
| 65 | High filter selectivity | Pre-filter + flat/IVF |
| 66 | Rare filtering | HNSW + post-filter |
| 67 | Corpus churn | Incremental HNSW or frequent rebuilds |
| 68 | Build time | HNSW build dominates for large corpora |
| 69 | Memory guardrail | Measure bytes/vector, not just index type |
| 70 | Health metric | Recall@10 on a fixed eval set, per index config |

## Self-Check

55+ = solid, 45-54 = redo Exercises 10 and 14, below that reread THEORY 2-8.