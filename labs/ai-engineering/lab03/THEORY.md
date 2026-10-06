# Lab 03: RAG System Architecture — Theory

## 1. The Pipeline

```
INGESTION (offline)                      QUERY (online)
-----------------                      ----------------
parse -> clean -> chunk                  rewrite -> embed
attach metadata                          -> dense search
contextual prefix                        -> lexical search
embed -> index upsert                    -> fusion
                                         -> rerank
                                         -> assemble -> generate
```

The offline/online split is architectural, not cosmetic: ingestion is expensive and
failure-prone; the query path has a latency budget measured in tens of milliseconds
before the model is even called. Never re-chunk at query time.

## 2. Chunking Is the Highest-Leverage Decision

Chunks must be **self-contained** (the reader needs the referent) and **small enough**
to coexist with the question and the answer.

| Strategy | Pros | Cons |
|----------|------|------|
| Fixed + overlap | Trivial, predictable | Splits sentences, breaks tables, loses referents |
| Sentence-aware | Preserves boundaries | Variable size, may exceed budget |
| Semantic | Best topical coherence | One embedding call per window |
| Recursive character | Respects a hard max | Boundary-blind |
| Structure-aware | Best for real documents | Needs a real parser |

Settings that work: 300-800 tokens with 10-20% overlap for prose. Never below ~50
tokens — at that size the chunk loses its subject and retrieval collapses. Always carry
metadata (`docId`, `sectionPath`, `page`, `chunkIndex`) so answers can cite.

**Contextual prefixes** (Anthropic's Contextual Retrieval) fix the decontextualization
problem: "revenue grew 3%" becomes scannable when prefixed with the document title and
section. Prepend to the text you *embed*; keep the original text for display and
citations.

## 3. Retrieval Stages

```
  dense ANN top-50  (recall ~0.95, ~2 ms)
  lexical BM25 top-50 (exact tokens, ~3 ms)
  fusion (RRF)
  rerank top-50 -> top-5 (cross-encoder, ~90 ms)
```

Why both: dense retrieval is weak on exact identifiers (part numbers, error codes,
proper nouns, dates) because those strings are near-unique and land in arbitrary
directions; BM25 is weak on paraphrase. Fusing recovers both. Reranking with a
cross-encoder (which attends over query and document jointly) recovers most of what
ANN recall gives up.

**Critical constraint**: ANN recall is a hard ceiling on end-to-end answer quality. If
the gold chunk is not retrieved, no prompt and no model fixes it.

## 4. Fusion

```
weighted:  score(d) = a * norm(dense) + (1-a) * norm(bm25)
RRF:       score(d) = sum_r 1 / (60 + rank_r(d))
```

Cosine lives in `[-1,1]` and BM25 in `[0,20]`, so unnormalized weighted fusion is
dominated by whichever scale is larger. RRF uses only ranks, so it needs no calibration
and cannot break when one retriever returns identical scores. RRF is the default;
weighted fusion is available for corpora where a specific mix measurably wins.

## 5. Context Assembly

```
budget = maxContext - systemTokens - queryTokens - maxNewTokens - schemaTokens
```

- Emit chunks in **ascending** score order so the strongest chunk lands nearest the
  question (models weight late context most strongly).
- Deduplicate near-identical chunks (syndicated documents are common).
- Number chunks and require inline `[n]` citations.
- Cap per-chunk tokens; a single huge chunk can consume the whole budget.
- Never truncate the schema or the question.

## 6. Grounding and Abstention

```
"Answer ONLY from the sources. If absent, reply exactly INSUFFICIENT_CONTEXT.
 Cite as [n]."
```

Then enforce in code: parse citations, verify each id exists in the supplied set, and
reject the sentinel. Add a retrieval-score threshold below which you abstain outright —
cheap insurance against confident fabrication.

## 7. Failure Taxonomy

| Failure | Symptom | Fix |
|---------|---------|-----|
| Bad chunking | Right doc, wrong chunk | Restructure chunking, add overlap |
| Embedding mismatch | Garbage everywhere | Same model+version for docs and queries |
| Top-k ceiling | Gold not in top-k | Hybrid, over-fetch, rerank |
| Context overflow | Truncated answers (`finish_reason=length`) | Smaller chunks, lower k |
| Stale index | Answers cite deleted docs | Freshness SLO, re-ingest |
| No abstention | Confident fabrication | Threshold + sentinel |
| Bad rerank | Plausible but wrong chunks | Tune k, better reranker |
| Too many chunks | Attention diluted, misattribution | Lower k; measure faithfulness not just recall |

**Rule: measure retrieval before touching the prompt.** recall@k first, always.

## 8. Evaluation

- **Retrieval**: recall@k, MRR, nDCG against gold chunk ids; report filtered and
  unfiltered separately.
- **Generation**: faithfulness (are claims supported by context?), answer relevance,
  exact match / token F1 vs gold, citation precision and recall.
- **End-to-end**: task metric plus p50/p99 latency and cost per query.
- **Unanswerable subset**: decline rate and false-decline rate, both.

## 9. Operational Design

- Namespace = `(corpusVersion, embedVersion)`; either changing means full re-ingest.
- Incremental upserts by content hash; tombstones for deletes; compaction.
- Embedding cache keyed by `(modelVersion, hash)` — often the largest cost line in
  ingestion.
- Freshness SLA per corpus with `index_age_hours` alerting.
- Per-stage latency instrumentation so a regression is attributable.
- Blue/green index swaps: build, verify recall, then flip.

## 10. Patterns Beyond Basic RAG

| Pattern | When | Cost |
|---------|------|------|
| Corrective RAG | Evaluate retrieved chunks, retrieve again if poor | 2x retrieval |
| Self-RAG | Model emits retrieval-necessity tokens | Model dependent |
| HyDE | Embed a hypothetical answer, not the query | 1 extra generation |
| Parent-child | Embed small chunks, return larger parents | Same index, bigger context |
| Multi-vector | Title + body + question embeddings per chunk | 3x storage |
| Late chunking | Embed the full document, pool per chunk | Model dependent |
| Graph RAG | Entities and relations as a graph | Much higher ingest cost |
| Query decomposition | Split multi-hop questions | Additional planning call |

Pick by measurement. Most production systems start with hybrid search + rerank, which
captures most of the gain at a fraction of the complexity.

## Key Equations

```
budget      = maxContext - system - query - maxNew - schema
cos(q,d)    = q.d / (|q||d|)
RRF(d)      = sum_r 1 / (60 + rank_r(d))
recall@k    = (1/|Q|) * sum_q [ gold_q ⊆ topk(q) ]
faithful    = (1/m) * sum_i 1[ entail(p, claim_i) >= tau ]
```