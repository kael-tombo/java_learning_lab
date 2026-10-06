# Lab 04: RAG System Design — Math Foundation

## 1. Vector Similarity

```
dot(a,b)   = sum_i a_i b_i
|a|         = sqrt(sum_i a_i^2)
cos(a,b)   = dot(a,b) / (|a| |b|)
```

If `a_hat = a/|a|` and `b_hat = b/|b|` then `cos(a,b) = dot(a_hat, b_hat)`.
Normalizing once at write time makes every query a single dot-product scan.

## 2. Why Normalize: Gradient of Cosine

`d cos(a,b)/d a = (1/|a|) ( b/|b| - cos(a,b) * a/|a| )`. The second term is the
component of `b_hat` along `a_hat`. Normalizing removes the radial degree of
freedom, so similarity depends on direction only — exactly what "semantic
relevance" should mean.

## 3. Distance/Similarity Equivalences

```
L2^2(a,b) = |a|^2 + |b|^2 - 2 a.b
```

For unit vectors, `L2^2 = 2 - 2cos`, so ranking by squared L2 is **identical** to
ranking by cosine. This is why some vector DBs store L2 and return correct cosine
orderings for normalized input.

## 4. BM25

```
score(q, d) = sum_{t in q} IDF(t) * TF(t,d) * (k1 + 1)
              / ( TF(t,d) + k1 * (1 - b + b * |d| / avgdl) )

IDF(t) = ln( 1 + (N - df(t) + 0.5) / (df(t) + 0.5) )
```

- The `ln(1 + ...)` (Lucene) variant is always positive, unlike raw IDF which goes
  negative for terms in > half the corpus.
- As `tf -> inf` the score saturates at `k1 + 1`: the 100th occurrence of a term
  matters far less than the 1st.
- `b` controls length penalty; `b = 0` disables it.

## 5. Score Fusion

Linear fusion requires commensurable scales:

```
score_fused(d) = alpha * (s_dense(d) - min_dense) / (max_dense - min_dense)
               + (1 - alpha) * (s_bm25(d) - min_bm25) / (max_bm25 - min_bm25)
```

Degenerate case: if `max == min` (all identical scores) the denominator is 0 —
return all candidates with equal fused score instead of NaN.

Reciprocal Rank Fusion avoids scores entirely:

```
RRF(d) = sum_r 1 / (k_RRF + rank_r(d)),    k_RRF = 60
```

Only ranks matter, so RRF is invariant to any monotone score transform.

## 6. Top-k Selection as Partial Sort

Full sort is `O(n log n)`; partial selection is `O(n)` expected via quickselect.

```
expected_cost(quickselect, k) = n + 2 * C(n,2)/k
```

For k=50, n=1e6, quickselect touches far less memory than sorting — this is the
single biggest latency lever in a flat index.

## 7. Approximate Search Error

Define recall loss for an index that returns set `A` when the true neighbours are `T`:

```
recall_loss = 1 - |A ∩ T| / |T|
```

HNSW search cost:

```
cost ≈ efSearch * (M * log_2(N) / M) hops,  each hop = M distance computations
```

Doubling `efSearch` roughly halves the miss rate at linear cost — the knob to reach
for when recall@k is short.

## 8. Context Budget Arithmetic

```
usable = maxContextTokens - systemTokens - queryTokens - maxNewTokens
kept   = greedily add chunks while sum(len(chunk_i)) <= usable
```

Truncation granularity matters: cutting mid-sentence costs tokens AND confuses the
reader. Better: fill greedily, then drop whole low-scoring chunks.

## 9. Metric Definitions

```
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
F1        = 2 * precision * recall / (precision + recall)
MRR       = (1/|Q|) * sum_q 1 / rank_of_first_relevant(q)
recall@k  = (1/|Q|) * sum_q [gold_q ⊆ topk(q)]        (set recall)
nDCG@k    = DCG@k / IDCG@k,  DCG@k = sum_i rel_i / log2(i + 1)
```

Prefer **set recall@k** when one gold passage suffices, nDCG when there are graded
relevance levels.

## 10. Abstention Trade-off

Let `a(p)` = accuracy given the top score exceeds threshold `p`, and
`c(p)` = coverage. The system objective is expected correctness:

```
E[correct] = c(p) * a(p)
```

Sweep `p`, plot both curves, and pick the knee. Coverage alone is a vanity metric;
report `E[correct]` and accuracy-on-answered.

## 11. Cost Model Per Query

```
cost = c_embed * 1 (query embed)
     + c_search * nprobe_equiv
     + c_rerank * k_rerank
     + c_gen * (queryTokens + sum(len(kept chunks)) + outputTokens)
```

The generation term usually dominates because retrieved context is the largest
token block — chunk selection is therefore a *cost* lever, not only a quality one.

## 12. Information-Theoretic View of Grounding

Let `C` be retrieved context and `A` the answer. Faithfulness bounds the
unsupported mass:

```
P(supported | A, C)  vs  P(A | no C)
```

Reporting `KL(P(A|C) || P(A))` as a "context sensitivity" score is a cheap,
model-agnostic hallucination proxy: large divergence means the answer is actually
conditioned on the evidence.

## Worked Numbers

Corpus: 200k chunks x 768 dims, fp32 = `200000 * 768 * 4 = 614 MB`.

- Flat search: 614 MB read per query -> ~120 ms at 5 GB/s. Too slow.
- PQ-8x96 (96 bytes/vector): 19 MB -> ~4 ms, recall@10 ~0.85.
- HNSW `M=32, efSearch=128`: ~2 ms, recall@10 ~0.97, ~1.2 GB index.
- Rerank 50 with a small cross-encoder: +90 ms — dominates the budget.
- Answer with 4 x 400-token chunks: +1600 prompt tokens per call.

Conclusion: the cross-encoder, not the ANN search, is the latency story.

## Self-Check Questions

1. Show L2 ranking equals cosine ranking for unit vectors.
2. Compute BM25 for a doc of length 20, avgdl 30, tf 3, k1 1.2, b 0.75.
3. Why can raw IDF be negative, and what does that break?
4. Sketch the abstention curve you would expect for a 90%-accurate classifier.