# Lab 04: RAG System Design — Mini Project

## Project: End-to-End RAG Engine over a Local Document Set

Build a retrieval-augmented generation system in plain Java 21: ingest a folder of
documents, chunk them, embed them, index them, retrieve with hybrid search, assemble
a budgeted context, generate grounded answers with citations, and measure retrieval
and generation quality.

## Goal

A CLI that answers 30+ questions about a real document set with measurable
`recall@k`, citation precision, and an abstention curve — plus a report explaining
which design choices moved the numbers.

## Requirements

### Phase 1: Corpus & Chunking
- [ ] Ingest at least 20 markdown/text files (use a docs tree or a public-domain
      book split into chapters).
- [ ] Three chunkers: fixed+overlap, sentence-aware, heading-aware.
- [ ] Chunk records carry `docId`, `sectionPath`, `index`.
- [ ] Print a chunk statistics table (count, mean tokens, min/max) per strategy.
- [ ] Persist chunks as JSONL for reuse.

### Phase 2: Embedding
- [ ] `Embedder` interface with a deterministic stub implementation
      (hashed bag-of-words projected to 256 dims, L2-normalized) so runs reproduce.
- [ ] Optional adapter interface for a real embedding API (not required to run).
- [ ] Cache `(modelVersion, sha256(text)) -> vector` on disk.

### Phase 3: Index & Retrieval
- [ ] Flat index with quickselect top-k.
- [ ] BM25 index with Lucene-style IDF.
- [ ] Fusion: weighted normalized + RRF; compare both.
- [ ] Two-stage: ANN/flat top-50 then a heuristic reranker to top-5.
- [ ] Report recall@1/5/10 and MRR@10 for each configuration.

### Phase 4: Context Assembly
- [ ] Token budget enforcement with configurable `maxContext`, `maxNewTokens`.
- [ ] Worst-first ordering so the best chunk lands next to the question.
- [ ] Near-duplicate chunk suppression (cosine > 0.97).
- [ ] Numbered sources and grounding instruction with `INSUFFICIENT_CONTEXT`.

### Phase 5: Generation (stub model)
- [ ] Deterministic extractive "generator": select sentences from the top chunks
      that best match the query terms, compose an answer, emit `[n]` citations.
- [ ] Interface compatible with a real LLM call so the swap is a one-line change.
- [ ] `CitationChecker` rejecting out-of-range citation ids.

### Phase 6: Evaluation Harness
- [ ] 30+ gold questions with `goldDocIds` and short gold answers.
- [ ] Metrics: recall@k, MRR, nDCG@10, citation precision/recall, exact-match and
      token-F1 on answers, abstention coverage/accuracy.
- [ ] Threshold sweep producing the coverage/accuracy curve.
- [ ] Config sweep: chunker x chunk size x alpha (fusion weight) x rerank on/off.

## Directory Layout

```
lab04/
  src/com/genai/lab04/
    chunk/, embed/, index/, lexical/, retrieve/, assemble/, answer/, eval/, ingest/
  corpus/            (20+ docs)
  gold/eval.jsonl    (questions + gold)
  out/index/         (vectors, chunks)
  out/reports/
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — chunkers implemented; stats table written.
2. **M2** — flat index + BM25 both return non-empty results; recall@5 > 0.4.
3. **M3** — hybrid fusion beats both singles on the identifier query subset.
4. **M4** — reranker improves recall@5 by >= 5 points.
5. **M5** — budget packing never overflows; citations always valid.
6. **M6** — abstention sweep; choose a threshold and justify it.
7. **M7** — final config sweep + `REPORT.md`.

## Acceptance Criteria

- [ ] `java Main ingest` is idempotent (second run inserts 0 chunks).
- [ ] Hybrid recall@5 >= max(dense, bm25) recall@5 on the full eval set.
- [ ] 100% of generated citations resolve to a supplied chunk id.
- [ ] Coverage/accuracy curve plotted; operating point documented with reasoning.
- [ ] Every prompt/token/retrieval latency recorded per query.
- [ ] A `REPORT.md` section explains the single biggest win and the single biggest
      remaining weakness.

## Stretch Goals

- [ ] Contextual chunk prefixes; measure recall delta on decontextualized chunks.
- [ ] Query rewriting (pronoun resolution + synonym expansion).
- [ ] HyDE: embed a hypothetical answer instead of the raw query.
- [ ] Parent-child indexing: embed small chunks, return larger parents.
- [ ] Add a second corpus version and prove namespace isolation with a re-ingest.
- [ ] A tiny HNSW implementation with `efSearch` sweep vs flat recall/latency.
- [ ] Concurrent query handling to show cache behaviour under load.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Recall@5 low across the board | Embedding mismatch or bad chunk ids |
| Recall great, answers wrong | Context assembly or grounding prompt |
| Citation ids out of range | Parser not given the same chunk ordering used in the prompt |
| Budget always exhausted | Chunks too large or k too high |
| BM25 returns nothing | Tokenizer mismatch with the corpus language |
| Second ingest inserts everything | Content hash computed over unstable fields |

## Definition of Done

`REPORT.md` contains: chunk stats, metric tables for every config, the abstention
curve, latency percentiles per stage, five example traces (question -> retrieved
chunks -> final prompt -> answer), and a "what I would change next" section.