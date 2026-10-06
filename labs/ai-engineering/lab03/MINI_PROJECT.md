# Lab 03: RAG System Architecture — Mini Project

## Project: RAG Pipeline with Measured Retrieval and Grounding

Build a complete RAG system in Java 21 — chunking, embedding stubs, hybrid retrieval,
fusion, reranking, budgeted assembly, grounded generation with citations, and an
evaluation harness that proves where quality comes from.

## Goal

A CLI that answers 50+ questions about a local document set with measurable
recall@5, citation validity, faithfulness, and an abstention frontier — plus a report
naming the single biggest quality lever.

## Requirements

### Phase 1: Corpus and Chunking
- [ ] Ingest 20+ markdown/text files.
- [ ] Three chunkers: fixed+overlap, sentence-aware, heading-aware.
- [ ] Chunk statistics table (count, mean tokens, min/max) per strategy.
- [ ] Contextual prefix applied to `embeddingText` only.
- [ ] Idempotent re-ingest by content hash.

### Phase 2: Retrieval
- [ ] Deterministic hashed-embedding stub (char n-grams -> 256 dims, normalized).
- [ ] Flat dense index with cosine.
- [ ] BM25 index from scratch.
- [ ] RRF fusion (default) and weighted fusion (with the degenerate guard).
- [ ] Rerank stage (overlap + proximity) over the top 50.

### Phase 3: Assembly and Answering
- [ ] Budget packer; best chunk emitted last; never drop schema or question.
- [ ] Grounded prompt with `INSUFFICIENT_CONTEXT` sentinel.
- [ ] Extractive "generator" stub: compose an answer from top chunks with `[n]`.
- [ ] `CitationChecker` rejecting out-of-range ids.
- [ ] Faithfulness check with numeric-claim emphasis.

### Phase 4: Evaluation
- [ ] 50+ gold questions with gold chunk ids and short answers.
- [ ] recall@1/5/10, MRR@10, nDCG@10.
- [ ] Citation precision/recall, token-F1 on answers.
- [ ] Abstention coverage/accuracy sweep; operating point chosen.
- [ ] Per-stage latency; sum verified against wall clock.

### Phase 5: Configuration Sweep
- [ ] Sweep chunker x chunk size x fusion weight x rerank on/off.
- [ ] Report quality and cost per configuration; mark the knee and dominated configs.

### Phase 6: Advanced Patterns (choose at least two)
- [ ] HyDE, parent-child, query decomposition, corrective RAG, multi-vector.
- [ ] Report the recall delta and latency cost of each.

### Phase 7: Robustness
- [ ] Freshness test: delete a section, re-ingest, verify it stops being retrieved.
- [ ] Injection canaries in the corpus; verify the guardrail flags them.
- [ ] 20 cache fixtures; verify the schema and question survive truncation.

## Directory Layout

```
lab03/
  src/com/aiengineering/lab03/{chunk,store,lexical,retrieve,assemble,answer,eval,ingest}/
  corpus/
  gold/eval.jsonl
  out/reports/metrics.json
  out/reports/sweep.csv
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — three chunkers with statistics.
2. **M2** — contextual prefix; recall improvement on decontextualized queries.
3. **M3** — dense + BM25 both functional; recall@5 > 0.40 baseline.
4. **M4** — fusion: RRF beats both singles on the identifier subset.
5. **M5** — rerank improves recall@5 by >= 3 points.
6. **M6** — assembly never exceeds budget; citations 100% valid.
7. **M7** — faithfulness report with the unsupported claim list.
8. **M8** — abstention frontier; operating point documented.
9. **M9** — full sweep; knee and dominated configs marked.
10. **M10** — two advanced patterns implemented with deltas.
11. **M11** — freshness, injection, and truncation tests green.
12. **M12** — report written with the biggest lever named.

## Acceptance Criteria

- [ ] Second ingest inserts zero chunks.
- [ ] Hybrid recall@5 >= max(dense, lexical) on the full set.
- [ ] Rerank improves recall@5 measurably.
- [ ] Budget never exceeded; schema and question always present.
- [ ] 100% of citations resolve to supplied chunk ids.
- [ ] Faithfulness reported with the failure list.
- [ ] Abstention operating point chosen with `E[correct]` reasoning.
- [ ] Weighted fusion handles the all-equal-scores case without NaN.
- [ ] Stage latency sum within 5% of wall clock.
- [ ] Freshness test removes deleted content from retrieval.

## Stretch Goals

- [ ] Multi-vector per chunk (title/body/question) with a storage/recall trade.
- [ ] Late chunking comparison.
- [ ] Corrective RAG with a relevance grader.
- [ ] Query decomposition for multi-hop questions.
- [ ] Cost model with a quality/cost frontier.
- [ ] Cache layers (embeddings, query embeddings, rerank scores).
- [ ] Per-corpus index routing.
- [ ] Adversarial corpus with injection payloads and a defense report.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Recall low everywhere | Embedding mismatch or bad chunk ids |
| Dense-only misses ids | Expected; hybrid required |
| NaN in rankings | Weighted fusion degenerate case |
| Citations out of range | Prompt ordering differs from checker assumption |
| Faithfulness low, answers fluent | Model answering from priors, not context |
| Budget always exhausted | Chunks too large or k too high |
| Stage sum != wall clock | Double-counted instrumentation |
| Second ingest duplicates | Hash over unstable fields |
| Deleted content still retrieved | Missing tombstone or late filtering |
| Sweep shows no improvement | Eval set too small to resolve the delta |

## Definition of Done

`REPORT.md` contains: the pipeline diagram, chunk statistics per strategy, the
contextual-prefix effect, retrieval metric tables for each configuration, the fusion
comparison on identifier queries, the rerank delta, the assembly worked example with
drop reporting, the faithfulness report, the abstention frontier with the chosen
operating point, the sweep table with dominated configs marked, the per-stage latency
breakdown, the robustness test results, and a "what is the single biggest quality lever
and why" section.