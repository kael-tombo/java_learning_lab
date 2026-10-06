# Lab 02: Vector Database Integration — Math Foundation

## 1. Distance Identities

Expand squared L2:

```
|a - b|^2 = |a|^2 + |b|^2 - 2 a·b
```

For unit vectors (`|a| = |b| = 1`):

```
|a - b|^2 = 2 - 2(a·b) = 2 - 2cos(a,b)
```

Two consequences that determine whether a system is correct:

1. **Ranking equivalence**: minimizing `|a-b|^2` maximizes `cos`. An engine storing
   L2 returns correct cosine orderings for normalized input.
2. **Monotone transform**: cosine ranking is identical under `cos -> 2 - 2cos`, so any
   monotone conversion preserves the top-k set.

But **unnormalized** input breaks it: with `|a| = 10, |b| = 0.1`, cosine ranks by
direction while L2 ranks by magnitude. Always check whether vectors were normalized at
write time.

## 2. Brute-Force Cost

```
time = n * dim * cost_per_madd
```

With AVX2 (8 floats per instruction, 2 FMA/cycle, 3 GHz), effective throughput is
~48 GFLOP/s single-core:

```
n=1e6, dim=768:  2*1e6*768 / 4.8e10 = 32 ms single core
                 ~8 ms with 4 cores
                 ~2 ms with SIMD-optimized int8 kernels
```

Memory traffic is the real limit: `1e6 * 768 * 4 bytes = 3.07 GB` per query. At 50 GB/s
that is `61 ms` — memory bound, not compute bound. **This is the key insight**: brute
force is limited by reading every vector, which is exactly what ANN indexes avoid.

## 3. IVF Recall Model

Let the query's true nearest centroid have rank `r_c` among centroids (by probability of
containing a true neighbour):

```
P(recall) ~ P(true top-k all inside the nprobe nearest cells)
          ~ sum over subsets; approximated by:
recall(nprobe) ~ 1 - exp(- nprobe / rho)
```

with `rho` a corpus-specific concentration parameter. For `nprobe = 1, 4, 16` and
`rho = 5`: `0.18, 0.55, 0.96`. Note how steep the curve is — `nprobe = 1` is
unusable, and recall is essentially saturated by `4 * rho`.

Latency: `~ nprobe * (n/nlist) * dim * cost`. Doubling `nprobe` doubles latency exactly.

## 4. HNSW Search Cost

Search descends from the top layer, examining `efSearch` candidates per step and
maintaining a bounded max-heap:

```
hops ~ log_{M}(n)                      (exponential growth of neighborhoods)
candidates examined ~ efSearch * hops
distance computations ~ efSearch * M * log_M(n)
```

For `n = 1e6, M = 16, efSearch = 64`: `hops ~ log16(1e6) ≈ 5`, so `~64*16*5 = 5120`
distance computations versus `1e6` for flat — a 200x reduction in work.

## 5. HNSW Memory

```
bytes_per_vector = dim * 4 (float)  +  M * L * 4 (neighbor ids)  +  overhead
L ~ log_M(n)
```

For 768 dims, `M = 16`, `n = 1e6` (`L ≈ 5`):

```
768*4 + 16*5*4 = 3072 + 320 = 3392 bytes
vector alone   = 3072 bytes
overhead      = 10.4%
```

So the graph itself is cheap; the *vectors* dominate. That is why quantizing the
vectors (int8 -> 768 bytes) gives a 4x win while the graph stays the same.

## 6. HNSW Layer Assignment

```
level = floor( -ln(U) * mL )        U ~ Uniform(0,1),  mL = 1/ln(M)
```

Expected layers above level 0: `1/M + 1/M^2 + ... = 1/(M-1)`. For `M = 16`: `0.067`.
So only 6.7% of nodes appear above the bottom layer — the top layers stay small, which
is what makes descent fast.

## 7. Recall vs efSearch

Empirically, recall follows a saturating curve:

```
recall(ef) ~ 1 - c * exp(-ef / e0)
```

with `e0` depending on `M` and corpus. The practical consequence: doubling `efSearch`
buys a small recall improvement at 2x latency. Find the knee by plotting; do not raise
`efSearch` reflexively.

## 8. Quantization Error

Scalar int8 with a per-vector scale `s = (max - min)/255`:

```
MSE = s^2 / 12
relative_error = s / std(x)
```

For a Gaussian vector with 768 dims, `max ~ 3.7 sigma`:

```
s ~ 7.4*sigma/255 = 0.029*sigma
MSE ~ 7e-5 * sigma^2
SNR ~ 1.4e4 -> 41 dB
```

PQ with `m` subvectors and `b` bits each: the distortion grows as `2^(-2b)` per
subvector but reconstruction error compounds across subvectors, so effective SNR
degrades roughly `m`-fold in the worst case. Empirically PQ-64 (6 bits x 8 subvectors)
on 768 dims gives 48 bytes/vector with recall@10 around 0.85 before reranking.

## 9. Pre- vs Post-Filter Math

Let `s` = selectivity (fraction of the corpus allowed), `n` = corpus size.

```
pre-filter:  candidates = s*n       latency ~ s * flat_latency
post-filter: candidates = n         latency ~ flat_latency
             results = expected k' where P(a result survives) = s
```

For `s = 0.01` and `k = 10`: expected surviving results `= 10 * 0.01 = 0.1`. **Post-filter
returns essentially nothing.** For `s = 0.5`: expected `= 5`, so you get 5 results when
you asked for 10.

Over-fetching post-filter to compensate:

```
k_fetch = k / s       latency ~ flat_latency (no saving), memory scanned same
```

so post-filter with over-fetch has all the cost of pre-filter and worse recall. **This is
the clearest argument for pre-filtering at low selectivity.**

## 10. Filtered Graph Connectivity

In a navigable small-world graph, each node has ~`M` random long-range edges.
Removing a fraction `1-s` of nodes removes fraction `1-s` of every edge:

```
P(edge survives both endpoints) = s^2
```

For `s = 0.1`: `0.01` — the graph becomes nearly disconnected. Traversal that skips
disallowed nodes then needs many more hops and eventually returns few results. This is
why "filtered HNSW" degrades sharply below ~30% selectivity, and why pre-filter is
mandatory for tenant isolation.

## 11. Duplicate Detection

Exact equality fails on floating point. Two options:

```
absolute: |cos - 1| < eps_abs              (breaks when magnitude is small)
relative: |cos(a,b) - cos(a,a)| < eps * cos(a,a)   (inflateThreshold)
```

`inflateThreshold` scales the tolerance by the vector's own norm, so it behaves the
same for short and long vectors. Values around `1e-3` work for text chunks.

## 12. Hybrid Fusion

```
weighted:  score(d) = a * norm(dense(d)) + (1-a) * norm(bm25(d))
RRF:       score(d) = sum_r 1 / (k + rank_r(d)),  k = 60
```

Why RRF is the default: it uses only ranks, so it is invariant to any monotone score
transform. That means you can combine dense cosine (in [-1,1]) with BM25 (in [0,20])
without calibration, and it does not degrade when one retriever returns degenerate
scores (min-max normalization divides by zero when all scores are equal).

## 13. Recall Budget Math

Suppose ANN recall@10 is `r`. With reranking over the top `m`, if the reranker is
near-perfect but can only recover items that were retrieved:

```
recall@5_after_rerank <= r * (fraction of gold in top-m)  <= r
```

So `recall@10 = 0.95` caps final recall at 0.95 **no matter how good the reranker is.**
This is the argument for over-fetching: with `m = 50`, if gold is present in the top-50
at rate `0.99`, final recall can be 0.99. **ANN recall is a hard ceiling on end-to-end
quality.**

## 14. Cost Model

```
cost_per_query = cost_embedding (amortized)
               + cost_index_search
               + cost_rerank * m * cost_cross_encoder
```

Cross-encoder cost dominates: a small reranker at ~1ms per pair over 50 pairs is 50ms,
versus 2ms for ANN search. The reranker is the latency budget; the index is not.

## Worked Numbers

Corpus: 10M chunks, 768 dims, fp32 = `30.7 GB`.

| index | memory | recall@10 | p50 latency | notes |
|-------|--------|-----------|--------------|-------|
| Flat | 30.7 GB | 1.00 | 61 ms | exact; too slow |
| Flat int8 | 7.7 GB | 0.98 | 18 ms | memory traffic / 4 |
| HNSW M=16 ef=64 | 33.9 GB | 0.97 | 1.2 ms | 5.7k distance computations |
| HNSW + int8 | 10.9 GB | 0.94 | 0.9 ms | vectors dominate memory |
| IVF-PQ 64x6bit | 1.6 GB | 0.85 | 0.6 ms | needs rerank |
| IVF-PQ + rerank 50 | 1.6 GB | 0.95 | 55 ms | **the practical choice** |

Read the last row: the memory-efficient index plus a reranker beats the exact index on
both memory (10x) and latency (slightly) while giving up 5 points of recall. The
pipeline, not the index, is the design.

Scale contrast: at 100k vectors, flat takes `6.1 ms` and is exact — the right answer.
The same index choice is wrong at 10M. **Index selection is a scale decision.**

## Self-Check Questions

1. Show that a vector of norm 2.0 and one of norm 0.1 rank differently under L2 vs
   cosine with the same direction.
2. Compute `bytes_per_vector` for HNSW at `dim=1024, M=32, n=1e9`.
3. Compute the expected surviving results for post-filter at `s=0.05, k=20`.
4. Show edge survival probability at `s=0.2` and explain the recall consequence.
5. Explain why ANN recall caps end-to-end recall, and compute the ceiling.