# Lab 04: RAG System Design — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Parametric memory | Knowledge compressed into weights; frozen, uncitable |
| 2 | Non-parametric memory | External document store queried at inference |
| 3 | RAG payoff | Updatable facts, citations, lower hallucination on private data |
| 4 | Ingestion vs query | Ingestion is offline and expensive; query is online and fast |
| 5 | Never re-chunk at query time | Chunks are indexed artifacts; changing them means re-ingest |
| 6 | Chunk size sweet spot | 300-800 tokens with 10-20% overlap for prose |
| 7 | Minimum chunk size | ~50 tokens; below that referents are lost |
| 8 | Fixed-size chunking | Simple, predictable, boundary-blind |
| 9 | Sentence-aware chunking | Preserves sentence boundaries, variable size |
| 10 | Semantic chunking | Split on embedding similarity dips; costs one embed per window |
| 11 | Structure-aware chunking | Headings/tables/lists; best for real documents |
| 12 | Chunk metadata | docId, sectionPath, page, chunkIndex — required for citations |
| 13 | Embedding | Dense vector map of text into R^d |
| 14 | Cosine similarity | `q.d / (|q| |d|)`, range [-1, 1] |
| 15 | Normalization trick | L2-normalized vectors make cosine equal to dot product |
| 16 | Model mismatch | #1 silent cause of "broken retriever" |
| 17 | Flat index | Exact brute force, O(n) per query, best under ~1M vectors |
| 18 | IVF | Inverted file: `nlist` cells, `nprobe` searched; recall/speed knob |
| 19 | HNSW | Layered navigable small world graph; log-scale search |
| 20 | HNSW knobs | `M`, `efConstruction`, `efSearch` |
| 21 | Product quantization | Compress vectors 10-100x, recall loss |
| 22 | Dense weakness | Exact tokens: part numbers, error codes, names, dates |
| 23 | BM25 | Lexical ranking with saturated TF and length normalization |
| 24 | BM25 params | `k1 = 1.2`, `b = 0.75` typical |
| 25 | BM25 IDF guard | Lucene form `ln(1 + (N-df+0.5)/(df+0.5))` avoids negatives |
| 26 | Hybrid search | Weighted fusion of dense and lexical scores |
| 27 | Why normalize scores | Cosine and BM25 live on different scales |
| 28 | RRF | `sum_r 1/(60 + rank_r(d))`, no calibration needed |
| 29 | Two-stage retrieval | Cheap ANN top-50..200, then precise cross-encoder rerank |
| 30 | Cross-encoder | Scores (query, doc) jointly; more accurate than bi-encoder |
| 31 | Rerank cost | O(k) forward passes; keep k at 20-50 |
| 32 | Context budget | `maxContext - overhead - maxNewTokens` |
| 33 | Chunk placement | Highest score nearest the question (late in context) |
| 34 | Dedupe chunks | Near-identical chunks waste budget and skew attention |
| 35 | Numbered chunks | Enables inline `[n]` citations |
| 36 | Grounding instruction | "Answer ONLY from the sources; else INSUFFICIENT_CONTEXT" |
| 37 | Sentinel enforcement | Parse and reject in code, not just in the prompt |
| 38 | Score threshold abstain | Cheap insurance against confident nonsense |
| 39 | Failure: chunking | Right doc, wrong chunk retrieved |
| 40 | Failure: embedding | Everything wrong at once -> suspect version mismatch |
| 41 | Failure: top-k ceiling | Gold chunk missing from top-k -> hybrid or larger k |
| 42 | Failure: overflow | finish_reason=length means context truncated |
| 43 | Failure: staleness | Deleted docs still retrievable -> freshness SLA |
| 44 | Failure: no abstain | Confident fabrication |
| 45 | Measure before prompting | Fix retrieval first; prompts cannot recover missing evidence |
| 46 | recall@k | Fraction of queries whose gold chunk appears in top k |
| 47 | MRR | Mean reciprocal rank of the first correct hit |
| 48 | nDCG | Rank-discounted, graded relevance across k |
| 49 | Faithfulness | Are answer claims supported by the context |
| 50 | Answer relevance | Is the answer worth responding to |
| 51 | Citation precision | Cited chunks that actually support the claim |
| 52 | Citation recall | Supporting chunks that were actually cited |
| 53 | Contextual embeddings | Prepend doc/section context to a chunk before embedding |
| 54 | Contextual BM25 | Same idea for lexical index: expand the indexed text |
| 55 | Index namespace | (corpusVersion, embeddingModelVersion) |
| 56 | Tombstones | Mark deleted chunks so they stop being retrievable |
| 57 | Content hashing | `sha256(docId + chunkText)` for idempotent ingest |
| 58 | Idempotent ingest | Second run must insert zero chunks |
| 59 | Freshness SLA | Alert on `index_age_hours` per corpus |
| 60 | Embedding cache | Same (model, text) -> vector; often the top cost line |
| 61 | Tenant isolation | Enforce in the index filter, not only the gateway |
| 62 | Metadata filtering | Pre-filter or post-filter; affects recall, test both |
| 63 | Multi-vector per chunk | Title/body/question embeddings improve recall, cost storage |
| 64 | Late chunking | Embed after full-document context, then mean-pool by chunk |
| 65 | Query rewriting | Normalize abbreviations, resolve pronouns before embedding |
| 66 | HyDE | Generate a hypothetical answer, embed that instead of the query |
| 67 | Parent-child index | Embed small chunks, return the larger parent for context |
| 68 | Summarization index | Store per-section summaries for broad questions |
| 69 | RAG vs fine-tune | Facts change -> RAG; behaviour/style -> fine-tune |
| 70 | Hybrid routing | Retrieval first, then fine-tuned answerer on retrieved text |

## Self-Check

55+ = solid, 45-54 = redo Exercises 7 and 12, below that reread THEORY 3-11.