# llm-genai-deep — Mini Project

## Project: A Retrieval-Augmented Question Answering System with Evaluation and Guardrails

Build a complete RAG system in Java 21: a corpus ingester, four chunking strategies, three
embedding approaches, four index types including HNSW, a cross-encoder reranker, a stub LLM
with real prompt and guardrail layers, a two-stage evaluation harness, a retrieval failure
taxonomy, and an attack suite. No external services.

## Goal

`Main` ingests 100 documents, answers 200 questions, reports retrieval and generation
metrics separately, classifies every failure into the taxonomy, runs 100 prompt-injection
attacks with per-layer attribution, and writes `REPORT.md` with every number in one place.

## Requirements

### Phase 1: Corpus and Chunking
- [ ] Document store with 100 documents across 5 topics; each with headings and structure.
- [ ] Fixed-size chunking with overlap; record chunk boundaries.
- [ ] Semantic chunking by embedding-similarity split points.
- [ ] Structural chunking preserving the heading path **inside** the embedded text.
- [ ] Chunk quality assessment: find facts severed by each strategy and count them.
- [ ] Metadata retention: source, heading path, span offsets.

### Phase 2: Embeddings
- [ ] Deterministic stub embedder with a seeded projection; reproducible across runs.
- [ ] Sentence encoder: mean pooling over token vectors.
- [ ] Mean-centering and whitening; measure mean pairwise cosine before and after.
- [ ] Bi-encoder with a learned projection head, trained on a small query-document set.
- [ ] Measure query-distribution mismatch: train on questions, query with keywords.

### Phase 3: Indexes
- [ ] Flat (brute force) index — the exact recall baseline.
- [ ] LSH with random hyperplanes; recall versus table count.
- [ ] IVF with k-means centroids; recall versus `nprobe`.
- [ ] HNSW with configurable `M`, `efConstruction`, `efSearch`; build and search implemented.
- [ ] Comparison table: recall@10, build time, query latency, memory at `N` in {1k, 10k}.
- [ ] **Every index's recall measured against flat search.** No assumed numbers.

### Phase 4: Retrieval Pipeline
- [ ] Query embedding, ANN search, top-k fetch.
- [ ] Cross-encoder reranker over the top 20; blended with the bi-encoder score.
- [ ] Context assembly with configurable ordering; "lost in the middle" measured at three
      positions.
- [ ] End-to-end retrieval on 200 questions; recall@5.

### Phase 5: Generation
- [ ] Stub LLM with a deterministic template-based generator plus a seeded sampler.
- [ ] Prompt assembly: system policy, labelled context, question — with data labels and
      delimiters.
- [ ] Grounded generation: every sentence cites a context span.
- [ ] Abstention option: "the context does not say"; accuracy/coverage frontier.
- [ ] Temperature sampling; report samples at three temperatures.

### Phase 6: Retrieval Evaluation
- [ ] recall@k, precision@k, MRR, NDCG@k, MAP — each verified against a hand-computed case.
- [ ] 200-question evaluation set with graded relevance.
- [ ] **Retrieval and generation reported separately, always.**
- [ ] Chunking ablation: four strategies, recall and answer accuracy for each.
- [ ] Reranking ablation: none, bi-encoder, cross-encoder — accuracy and latency.

### Phase 7: Generation Evaluation
- [ ] BLEU-4, ROUGE-1, ROUGE-L implemented and verified on worked examples.
- [ ] Contextual similarity score with the stub embedder.
- [ ] Faithfulness by claim extraction; per-claim output.
- [ ] Answer relevance, context precision, context recall.
- [ ] Judge with a structured rubric; agreement with human labels; position-bias correction.
- [ ] Report BLEU and faithfulness side by side — and explain why the first can be high
      while the second is low.

### Phase 8: Failure Taxonomy
- [ ] Classify all 200 questions: not-in-corpus / not-retrieved / buried / ignored /
      contradicted.
- [ ] Report the distribution and the fix implied by each category.
- [ ] Contradiction handling: two documents disagreeing; design and test a policy.

### Phase 9: Guardrails
- [ ] Input layer: normalization, decode detection, length caps, rate limits.
- [ ] Tiered filter: cheap high-recall stage plus a precise classifier; confusion matrix.
- [ ] Output pipeline: eight stages, each instrumented, fail closed on exception.
- [ ] A stage made to throw deliberately, proving fail-closed.
- [ ] PII scrub with a re-scan assertion.

### Phase 10: Attack Suite and Attribution
- [ ] 100 direct prompt injections across 5 families.
- [ ] 40 indirect injections embedded in retrieved documents.
- [ ] 8 mutation operators applied to 20 base attacks.
- [ ] Per-layer attribution histogram with the uncaught count published.
- [ ] Data labelling effectiveness measured with and without labels.
- [ ] Every finding converted into a permanent regression test.

### Phase 11: Report
- [ ] `REPORT.md` with every table.

## Directory Layout

```
llm-genai-deep/
  src/com/ailab/genai/
    corpus/{Doc,Docs,Chunker}.java
    embed/{StubEmbedder,SentenceEncoder,BiiEncoder,Whitening}.java
    index/{FlatIndex,LshIndex,IvfIndex,Hnsw}.java
    rag/{Retriever,Reranker,ContextBuilder,RagPipeline}.java
    eval/{RetrievalMetrics,GenerationMetrics,Faithfulness,Judge,Taxonomy}.java
    safety/{Sanitizer,DecodeDetector,TieredFilter,OutputPipeline,PiiScrubber}.java
    attacks/{AttackSuite,Mutations,Attribution}.java
    Main.java
  out/eval_report.txt
  out/attribution.json
  REPORT.md
```

## Milestones

1. **M1** — document store and four chunking strategies with severed-fact counts.
2. **M2** — stub embedder, centering, whitening, anisotropy measurement.
3. **M3** — flat index; exact recall baseline established.
4. **M4** — LSH and IVF with measured recall.
5. **M5** — HNSW built and searched; recall verified against flat at four `efSearch`.
6. **M6** — retriever plus cross-encoder reranker; blended score.
7. **M7** — context ordering experiment quantifying lost-in-the-middle.
8. **M8** — stub LLM generation with grounding and abstention.
9. **M9** — retrieval metrics verified against hand computation.
10. **M10** — 200-question evaluation set with graded relevance.
11. **M11** — generation metrics; BLEU, ROUGE, faithfulness, judge agreement.
12. **M12** — chunking and reranking ablations.
13. **M13** — failure taxonomy across all 200 questions.
14. **M14** — contradiction policy implemented and tested.
15. **M15** — input layer and tiered filter with a confusion matrix.
16. **M16** — eight-stage output pipeline with fail-closed proven.
17. **M17** — attack suite with per-layer attribution.
18. **M18** — every finding converted to a regression test.
19. **M19** — `REPORT.md` written.

## Acceptance Criteria

- [ ] Every index's recall@10 measured against exact flat search and reported.
- [ ] Anisotropy measured before and after centering, with the improvement shown.
- [ ] Structural chunking beats fixed chunking on recall@5 by a stated margin.
- [ ] Heading text included in the embedded string, verified by inspection.
- [ ] Reranking improves recall by a stated margin at a stated latency cost.
- [ ] Context position experiment run; the best position identified empirically.
- [ ] Retrieval and generation metrics reported separately for every question.
- [ ] Failure taxonomy covers all 200 questions with a distribution.
- [ ] BLEU verified against a hand-computed example.
- [ ] Faithfulness reported per claim, with unsupported claims identified.
- [ ] Abstention frontier: accuracy and coverage at three thresholds.
- [ ] Tiered filter confusion matrix reported; precision computed at the real base rate.
- [ ] Output stage exception blocks (fail-closed verified).
- [ ] Data labelling measurably reduces indirect-injection compliance.
- [ ] Per-layer attribution sums correctly with the uncaught count published.
- [ ] Reverting a guardrail fix causes the attack suite to fail.
- [ ] Re-running `Main` reproduces identical metrics (seeded throughout).

## Stretch Goals

- [ ] Filtered vector search: pre-filter versus post-filter recall comparison.
- [ ] Index staleness: recall cost of an un-updated index after bulk insertion.
- [ ] Hybrid retrieval: dense plus BM25-style lexical, fused by reciprocal rank.
- [ ] Query decomposition: split a multi-hop question into sub-queries.
- [ ] Self-consistency at 5 samples with the accuracy/cost frontier.
- [ ] Chain-of-verification implemented against the stub generator.
- [ ] LoRA implemented on the stub model and evaluated on a formatting task.
- [ ] DPO loss implemented and its implicit reward inspected.
- [ ] HNSW with a filtered search path (tenant-scoped) and recall measured.
- [ ] A deliberate numerical bug injected and located with the metric suite.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| HNSW recall reported without a baseline | Assumed rather than measured |
| All embeddings look similar | Anisotropy; no centering |
| Retrieved chunk lacks context | Heading in metadata only, not in the embedded string |
| Facts split across chunks | No overlap, or overlap not included in the step size |
| Low answer score with high recall@5 | Generation or grounding problem, not retrieval |
| BLEU high, faithfulness low | Metric mismatch; n-gram overlap rewards copying |
| Safety flags mostly wrong | Single classifier at a low base rate; needs tiering |
| Guardrail passes after an exception | try/catch that logs and continues instead of failing closed |
| Indirect injection succeeds | Untrusted content concatenated into policy without labels |
| Re-running gives different numbers | Unseeded randomness in sampling, shuffling, or attacks |
| Abstention reported as accuracy only | Coverage hidden |

## Definition of Done

`REPORT.md` contains: corpus statistics and the four chunking strategies with severed-fact
counts, embedding results with the anisotropy before/after numbers, the four index
comparison table with measured recall, the reranking ablation with latency, the context
ordering experiment, the generation configuration and samples at three temperatures, the
retrieval metrics table (recall@k, precision@k, MRR, NDCG, MAP) for every configuration,
the generation metrics table (BLEU, ROUGE, faithfulness, relevance, context precision) with
the BLEU-versus-faithfulness example, the judge agreement matrix and the position-bias
correction, the failure taxonomy distribution with the fix implied per category, the
contradiction policy results, the tiered filter confusion matrix with precision at the real
base rate, the output pipeline results including the fail-closed proof, the attack suite
results with per-layer attribution and the uncaught list, the data-labelling effectiveness
numbers, the ablation summary, and a list of residual risks accepted with reasons.
