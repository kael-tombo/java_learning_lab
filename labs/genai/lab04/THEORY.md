# Lab 04: RAG System Design — Theory

## 1. Why Retrieval

LLM weights are **parametric memory**: compressed, lossy, frozen at training time,
and unable to cite sources. RAG adds a **non-parametric memory**: an external
document store queried at inference time. Three properties follow directly:

1. Facts can be updated without retraining.
2. Answers can cite the exact passage.
3. Hallucination on "what does our contract say" drops sharply, because the
   answer is copied from retrieved text rather than recalled.

## 2. The Pipeline

```
INGESTION (offline)                         QUERY (online)
-----------------                         ----------------
parse (pdf/html/md)                         embed query
  -> clean / normalize                       -> ANN search (top-k)
chunk (fixed | semantic)                     -> (optional) hybrid + rerank
  -> attach metadata                         -> build context block
embed chunks                                 -> prompt with citations
  -> upsert index                            -> generate
  -> eval set from gold QA                     -> cite + abstain
```

The offline/online split matters: ingestion is expensive and failure-prone,
query must be fast. Never re-chunk at query time.

## 3. Chunking

The single highest-leverage decision. Chunks should be **semantically
self-contained** and small enough to fit alongside the question and answer.

| Strategy | Pros | Cons |
|----------|------|------|
| Fixed size + overlap | Trivial, predictable | Splits sentences, breaks tables |
| Sentence/paragraph aware | Preserves boundaries | Variable size, can be too large |
| Semantic (embedding similarity) | Best topical coherence | Needs an embedding call per window |
| Recursive character split | Respects a max size hard | Still boundary-blind |
| Structure-aware (headings, tables, list items) | Best for docs | Requires a real parser |

Practical settings: 300-800 tokens with 10-20% overlap for prose; never chunk
below ~50 tokens or retrieval quality collapses. Always carry metadata
(`docId`, `sectionPath`, `page`, `chunkIndex`) so answers can cite.

## 4. Embeddings and Similarity

An embedding model maps text to a dense vector `e in R^d`. Retrieval by cosine
similarity:

```
cos(q, d) = (q . d) / (|q| |d|)
```

If vectors are L2-normalized, `cos(q,d) = q . d`, so one dot product suffices.
Choose the metric to match the training objective: contrastive models trained with
cosine similarity degrade if you rank by raw dot product.

Embed **the query with the same model as the documents** — a mismatch is the
number-one silent cause of "the retriever is broken".

## 5. Search Structures

- **Flat / brute force**: exact, O(n) per query, unbeatable under ~1M vectors.
- **IVF (inverted file)**: cluster into `nlist` cells, probe `nprobe`; recall
  trades for speed. Requires training.
- **HNSW**: layered navigable small-world graph, log-scale search, strong recall,
  memory-hungry. `M`, `efConstruction`, `efSearch` are the knobs.
- **PQ (product quantization)**: compresses vectors, 10-100x memory reduction,
  recall loss.

An ANN library is a hard dependency in production; know the knobs anyway
(`ai-engineering/lab02` and `llm-genai-deep/02-hnsw-indexing` go deeper).

## 6. Hybrid Search

Dense retrieval is weak on **exact tokens**: part numbers, error codes, proper
names, dates. Lexical search (BM25) is weak on paraphrase. Hybrid = weighted
score fusion:

```
score(d) = alpha * norm(denseScore(d)) + (1 - alpha) * norm(bm25Score(d))
```

Normalization matters — cosine in [-1,1] and BM25 in [0, ~20] are not
commensurable without min-max or z-scoring per query. Reciprocal Rank Fusion is
the robust alternative: `RRF(d) = sum_r 1 / (k + rank_r(d))` with `k = 60`,
no score calibration needed.

## 7. Reranking

Two-stage retrieval is the standard quality lever:
1. Retrieve top-50 to 200 cheaply (ANN).
2. Rerank with a cross-encoder that scores `(query, chunk)` jointly — far more
   accurate than bi-encoder dot products because it sees both texts at once.

Cost: reranking is O(k) forward passes. Keep k small (20-50).

## 8. Context Assembly

- Budget: `maxContext - promptOverhead - maxNewTokens`.
- Order: put the highest-scoring chunk **closest to the question** (models weight
  the end of context most strongly), or place a citation instruction after the
  context.
- Deduplicate near-identical chunks; they waste budget and distort attention.
- Number chunks and require inline citations `[3]` so answers are attributable.
- Cap per-chunk tokens; truncate mid-sentence if a chunk is huge.

## 9. Grounding and Abstention

Prompt to force grounding:

```
Answer ONLY from the sources below. If the answer is absent, reply exactly:
INSUFFICIENT_CONTEXT
Cite sources as [n].
```

Then enforce it in code: parse citations, verify each cited chunk id exists, and
check the answer is not the refusal sentinel. Also compute a retrieval score
threshold below which you abstain — cheap insurance against confident nonsense.

## 10. Failure Taxonomy (debug this first)

| Failure | Symptom | Fix |
|---------|---------|-----|
| Bad chunking | Right doc, wrong chunk retrieved | Restructure chunking, add overlap |
| Embedding mismatch | Garbage results across the board | Same model for docs and queries |
| Wrong top-k ceiling | Correct doc not in top-k | Add hybrid search, increase k |
| No rerank | Plausible but wrong chunks | Add cross-encoder rerank |
| Context overflow | Truncated answers, finish_reason=length | Shrink chunks, lower k |
| Stale index | Answers cite deleted docs | Re-ingest pipeline + freshness SLA |
| No abstention | Confident fabrication | Threshold + INSUFFICIENT_CONTEXT |

**Rule: measure retrieval before touching the prompt.** If recall@k is bad, the
prompt cannot save it.

## 11. Evaluation

- **Retrieval**: recall@k, MRR, nDCG against gold passage ids.
- **Generation**: faithfulness (are claims supported by context?), answer
  relevance, exact match / F1 vs gold, citation precision and recall.
- **End-to-end**: task metric plus latency percentiles and cost per query.

## 12. Operational Design

- Index namespace = `(corpusVersion, embeddingModelVersion)`. Both changes mean
  full re-ingest.
- Incremental upserts by content hash; tombstones for deletes.
- Tenant isolation in the filter, not only in the ACL layer.
- Freshness SLA per corpus; alert on `index_age_hours`.
- Cache embeddings for identical (model, text) pairs — embedding calls are
  frequently the top cost line.

## Key Equations

```
cos(q, d) = q.d / (|q| |d|)
RRF(d)    = sum_r 1 / (k_RRF + rank_r(d))
budget    = maxContext - promptOverhead - maxNewTokens - maxChunkTokens
```