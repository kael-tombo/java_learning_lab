# Lab 03: RAG System Architecture — Math Foundation

## 1. Cosine Similarity

```
cos(q, d) = q.d / (|q| |d|)
```

With L2-normalized vectors, `cos(q,d) = q.d`, so retrieval is one dot product per
document. Normalization is therefore a write-time decision that removes work from the
query path.

**Consequence**: many teams store unnormalized vectors and pay a `sqrt` per comparison
at query time, then wonder why their latency is worse than the published benchmarks.

## 2. BM25

```
score(q,d) = sum_{t in q} IDF(t) * tf(t,d) * (k1+1)
             / ( tf(t,d) + k1*(1 - b + b*|d|/avgdl) )

IDF(t) = ln( 1 + (N - df(t) + 0.5) / (df(t) + 0.5) )
```

Properties:
- **Saturation**: as `tf -> inf`, the score tends to `k1+1`. The 100th occurrence of a
  word matters far less than the first. This is the anti-spam property.
- **Length normalization**: `b` controls how strongly document length is penalized.
  `b = 0` disables it.
- **Always-positive IDF**: the Lucene `ln(1 + ...)` form is positive for all terms; the
  textbook `ln(N/df)` form goes negative for terms in more than half the corpus, which
  makes a matching document score worse than a non-matching one.

## 3. Score Fusion

Weighted fusion requires commensurate scales:

```
fused(d) = a * (s_dense(d) - min_dense) / (max_dense - min_dense)
         + (1-a) * (s_bm25(d) - min_bm25) / (max_bm25 - min_bm25)
```

Degenerate case: if `max_dense == min_dense` (all documents equally similar — common
for a generic query), the denominator is zero. Correct handling: assign all documents
the same dense score and let the lexical term decide. Implementations that skip this
produce NaN, which then sorts unpredictably and silently degrades ranking.

RRF avoids the problem by using only ranks:

```
RRF(d) = sum_r 1 / (k + rank_r(d)),    k = 60
```

Invariant under any monotone transform of `s_r`, and finite for every document with a
rank.

## 4. Recall@k and the Rerank Ceiling

```
recall@k = (1/|Q|) * sum_q [ gold_q ⊆ topk(q) ]
```

Let ANN return top-`m` with the gold present with probability `p_m`, and let the
reranker be perfect. Then:

```
end_to_end_recall@5 <= p_m
```

For a typical HNSW at `k=10`: `p_10 = 0.95` -> ceiling 0.95. At `k=50`:
`p_50 = 0.99` -> ceiling 0.99. So over-fetching from 10 to 50 buys 4 points of
maximum quality, at the cost of 5x the rerank latency. That trade is the central
tuning decision in a RAG pipeline.

## 5. Retrieval vs Faithfulness Trade-off

Empirically, adding chunks increases recall and can decrease faithfulness:

```
recall(k)     increases with k (diminishing)
faithful(k)   can peak around k=3-6 then decline
```

Why: more context dilutes attention, and the model attributes claims to the wrong
chunk. The metric to optimize is therefore **not** recall@k but the end-to-end answer
metric, with faithfulness as a guardrail. Reporting only recall leads to systems that
retrieve more and answer worse.

## 6. Information Density

With `D` documents stuffed and one relevant:

```
signal_density = relevant_tokens / total_context_tokens = 1/D
```

`D = 50` -> 2%. Retrieval of 2 chunks -> near 100% at 1/25 the tokens. Two effects
compound: fewer tokens (cost, TTFT, cache) and higher density (accuracy). This is the
quantitative case against stuffing.

## 7. Context Budget Arithmetic

```
usable = maxContext - systemTokens - queryTokens - maxNewTokens - schemaTokens
kept   = chunks added in descending score while sum(len) <= usable
```

Truncation granularity matters. Cutting a chunk mid-sentence wastes tokens *and*
confuses the reader. Better: skip whole low-scoring chunks until the next one fits.
Truncation should never touch the schema or the question.

## 8. Citation Metrics

```
citation_precision = |cited ∩ supporting| / |cited|
citation_recall    = |cited ∩ supporting| / |supporting|
```

Range checks (`n` within `[1, k]`) are the cheapest bug detector in this pipeline: an
out-of-range citation almost always means the prompt listed chunks in a different
order than the citation parser assumes.

## 9. Abstention Trade-off

Let `a(p)` = accuracy given the top score exceeds threshold `p`, `c(p)` = coverage:

```
E[correct](p) = c(p) * a(p)
```

Maximize `E[correct]`, not coverage. A system answering 100% at 78% accuracy versus
60% at 95% yields `E[correct]` of 0.78 versus 0.57 — the abstaining system is worth far
more even though it "fails" 40% of queries. Report the operating point and the
rationale, because product teams consistently prefer higher coverage until they see
this arithmetic.

## 10. End-to-End Quality Math

Define the pipeline quality as a product of stage reliabilities:

```
P(correct) ~ P(retrieval hit) * P(rerank keeps) * P(answer grounded) * P(parse ok)
```

With 0.95 retrieval, 0.98 rerank preservation, 0.93 grounding, 0.99 parse:
`P(correct) ~ 0.855`. Each stage is a multiplier, so a 5-point loss anywhere costs 5
points overall — and the stages are not independent, so the true value is usually lower.
This is why improving chunking (which lifts stage 1) often beats tuning the prompt.

## 11. Cost Model

```
cost_per_query = c_embed * 1
               + c_dense * 1
               + c_lexical * 1
               + c_rerank * k_rerank
               + c_gen * (queryTokens + sum(kept chunkTokens) + outputTokens)
```

At `c_gen = $15/M`, 4 chunks x 400 tokens = 1,600 context tokens plus 200 output:
`$0.027`. Reducing k from 6 to 4 saves `$0.006` (22%). Reducing chunk size from 400 to
250 saves `$0.009` (33%) at some recall cost. **Chunk selection is a cost lever**, not
only a quality one, and that is frequently underappreciated.

## 12. Entailment-Based Faithfulness

Split the answer into `m` atomic claims, score each against the context:

```
faithfulness = (1/m) * sum_i 1[ entail(p, c_i) >= tau ]
```

Information-weighted variant, so a wrong number counts more than a filler adjective:

```
faithful_w = sum_i I(c_i) * 1[entail >= tau] / sum_i I(c_i),   I(c) = -log p(c)
```

Practical: detect numeric claims separately and verify them by exact match against the
context, because a wrong number is the failure that causes real damage.

## 13. Retrieval Latency Budget

```
total = t_embed + t_dense + t_lexical + t_fusion + t_rerank
```

Typical: 12 + 2 + 3 + 0.1 + 90 = 107 ms. The reranker is 84% of the budget. Options,
in order: lower `k_rerank`, batch the reranker, use a smaller reranker, cache rerank
scores for repeated queries, skip reranking for low-risk query classes. Skipping
reranking entirely is the last resort — it is the quality lever.

## 14. Multi-Query Fan-Out

Decompose a question into `m` sub-queries, retrieve for each, fuse:

```
RRF_multi(d) = sum_{j=1..m} 1 / (k + rank_j(d))
```

Recall improves on multi-hop questions because different sub-queries surface different
supporting chunks. Cost: `m` dense searches and `m` embedding calls. For `m = 3` the
retrieval cost triples but is still ~9 ms — negligible next to rerank. Use it only
when the question is genuinely multi-hop; a router decides.

## Worked Numbers

Budget: `maxContext = 8192`, system 200, query 40, schema 120, maxNew 400.
`usable = 8192 - 760 = 7432` tokens.

| k | chunk size | context tokens | gen cost | recall@5 | faithful |
|---|-----------|----------------|----------|----------|----------|
| 3 | 400 | 1,200 | $0.021 | 0.88 | 0.94 |
| 5 | 400 | 2,000 | $0.033 | 0.93 | 0.93 |
| 8 | 400 | 3,200 | $0.051 | 0.95 | 0.89 |
| 12 | 400 | 4,800 | $0.075 | 0.96 | 0.83 |
| 5 | 250 | 1,250 | $0.022 | 0.91 | 0.93 |
| 5 | 600 | 3,000 | $0.048 | 0.95 | 0.92 |

Reading: recall saturates near k=8 but faithfulness falls monotonically, so the honest
optimum is around k=5. Smaller chunks (250) give up 2 points of recall for a 33% cost
cut. Chosen configuration: k=5, 400-token chunks, rerank top-50 -> 5: cost $0.033,
recall 0.93, faithfulness 0.93.

With ANN recall@50 = 0.99 and a strong reranker, the ceiling becomes 0.99, so the
bottleneck shifts from retrieval to grounding — which is where the next engineering
effort should go.

## Self-Check Questions

1. Compute BM25 for `tf=3`, `|d|=20`, `avgdl=30`, `N=1000`, `df=5`, `k1=1.2`, `b=0.75`.
2. Show what happens to min-max fusion when all dense scores are 0.42.
3. Derive the end-to-end ceiling for ANN recall@10 = 0.93 and rerank `m` = 30 with
   `p_30 = 0.98`.
4. Compute `E[correct]` for coverage 0.6/accuracy 0.95 and coverage 1.0/accuracy 0.78.
5. Show that a 5-point loss at any single stage costs 5 points end to end.