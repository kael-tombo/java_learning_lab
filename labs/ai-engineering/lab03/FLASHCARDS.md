# Lab 03: RAG System Architecture — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | RAG | Retrieval at inference to ground generation |
| 2 | Parametric memory | Weights; frozen, lossy, uncitable |
| 3 | Non-parametric memory | External store queried per request |
| 4 | Offline vs online | Ingest is batch; query is per-request |
| 5 | Never re-chunk at query | Chunking is an indexed artifact |
| 6 | Chunking leverage | Highest-leverage retrieval decision |
| 7 | Chunk size | 300-800 tokens, 10-20% overlap |
| 8 | Minimum chunk size | ~50 tokens |
| 9 | Fixed chunking | Simple; boundary-blind |
| 10 | Sentence-aware | Preserves boundaries; variable size |
| 11 | Semantic chunking | Split on similarity dips |
| 12 | Structure-aware | Headings/tables/lists; needs a parser |
| 13 | Chunk metadata | docId, sectionPath, page, index |
| 14 | Contextual prefix | Doc title + section prepended before embedding |
| 15 | Decontextualization | "revenue grew 3%" with no subject |
| 16 | Keep text vs embeddingText | Citations use text; search uses the prefix |
| 17 | Dense retrieval | Bi-encoder; paraphrase-strong |
| 18 | Lexical retrieval | BM25; exact-token-strong |
| 19 | Weakness of dense | Exact ids, codes, names, dates |
| 20 | Weakness of BM25 | Paraphrase |
| 21 | Hybrid | Union of both strengths |
| 22 | RRF | `sum 1/(60+rank)`, no calibration |
| 23 | Weighted fusion | Needs comparable scales |
| 24 | Degenerate scores | Min-max divides by zero |
| 25 | Two-stage retrieval | ANN top-50, then rerank to top-5 |
| 26 | Cross-encoder | Joint attention over query and document |
| 27 | Rerank k | 20-50; quality flattens, latency linear |
| 28 | ANN recall ceiling | Hard cap on end-to-end quality |
| 29 | Over-fetch | Raises gold availability to the reranker |
| 30 | Context budget | `maxContext - system - query - maxNew - schema` |
| 31 | Evidence ordering | Ascending score; best lands last |
| 32 | Dedupe chunks | Syndicated docs waste budget |
| 33 | Numbered chunks | Enables inline `[n]` citations |
| 34 | Grounding instruction | "Only from sources; else INSUFFICIENT_CONTEXT" |
| 35 | Sentinel enforcement | Parse in code, not just prompt |
| 36 | Score threshold | Abstain below a retrieval score |
| 37 | Citation validation | Cited id must be in the supplied set |
| 38 | finish_reason=length | Context was truncated |
| 39 | Failure: chunking | Right doc, wrong chunk |
| 40 | Failure: embedding mismatch | Garbage everywhere; check versions |
| 41 | Failure: top-k ceiling | Gold absent from candidates |
| 42 | Failure: overflow | Too many/too large chunks |
| 43 | Failure: staleness | Deleted docs still retrievable |
| 44 | Failure: no abstention | Confident fabrication |
| 45 | Measure before prompting | recall@k first |
| 46 | recall@k | Gold chunk in top k |
| 47 | MRR | Reciprocal rank of the first hit |
| 48 | nDCG@10 | Rank-discounted graded relevance |
| 49 | Faithfulness | Claims supported by the context |
| 50 | Citation precision | Cited chunks that support the claim |
| 51 | Citation recall | Supporting chunks that were cited |
| 52 | Unanswerable set | Abstention quality measurement |
| 53 | Decline vs false-decline | Both must be reported |
| 54 | Namespace | corpusVersion + embedVersion |
| 55 | Idempotent ingest | Content hash; second run inserts nothing |
| 56 | Tombstone | Logical delete + compaction |
| 57 | Embedding cache | `(modelVersion, hash) -> vector` |
| 58 | Freshness SLA | `index_age_hours` alerting |
| 59 | Blue/green index | Build, verify recall, flip |
| 60 | Per-stage latency | Make regressions attributable |
| 61 | Corrective RAG | Grade chunks, re-retrieve if poor |
| 62 | HyDE | Embed a hypothetical answer |
| 63 | Parent-child | Index children, return parents |
| 64 | Multi-vector | Title + body + question per chunk |
| 65 | Late chunking | Embed the document, pool per chunk |
| 66 | Query decomposition | Sub-queries, per-sub-query retrieval |
| 67 | Graph RAG | Entities and relations; much higher ingest cost |
| 68 | Graph RAG tradeoff | Better multi-hop, far more ingest complexity |
| 69 | RAG vs fine-tune | Facts change -> RAG; behaviour -> fine-tune |
| 70 | Cost driver | Retrieved context tokens dominate the bill |

## Self-Check

55+ = solid, 45-54 = redo Exercises 5 and 8, below that reread THEORY 2-8.