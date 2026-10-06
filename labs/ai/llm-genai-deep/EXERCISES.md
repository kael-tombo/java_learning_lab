# llm-genai-deep — Exercises

Difficulty: **E** easy, **M** medium, **H** hard. Java 21, no dependencies. Embeddings,
indexes, retrieval, evaluation, prompts, agent loops, LoRA, DPO, verification, and safety
are all implemented against deterministic stubs and test doubles — no network calls.

## Module 01 — Embeddings and Semantic Search

- [ ] **E1.1** Implement CBOW and skip-gram on a tiny corpus with negative sampling. Report
      the nearest neighbours of three words and sanity-check them.
- [ ] **E1.2** Implement GloVe as a weighted least-squares factorization of a co-occurrence
      matrix; report reconstruction error.
- [ ] **E1.3** Implement fastText with character n-grams; show it handles a typo and an
      unseen inflection where Word2Vec cannot.
- [ ] **M1.4** Cosine similarity versus dot product; show the ranking differs when norms
      vary widely.
- [ ] **M1.5** Centering and whitening embeddings; report the mean cosine similarity before
      and after. Demonstrate the anisotropy problem.
- [ ] **M1.6** Build a toy sentence encoder (mean of token embeddings); compare against a
      bi-encoder with a projection head.
- [ ] **H1.7** Bi-encoder versus cross-encoder retrieval on 200 query-document pairs. Report
      recall@10 for both and the cases where the cross-encoder wins.
- [ ] **H1.8** Query-distribution mismatch: train on questions, query with keywords. Report
      the recall drop and test mean-pooling as a mitigation.

## Module 02 — HNSW Indexing

- [ ] **E2.1** Build a flat (brute force) index; establish the exact recall@k baseline of
      1.0.
- [ ] **E2.2** Implement LSH with random hyperplanes; report recall@k versus the number of
      tables.
- [ ] **M2.3** Implement IVF with k-means centroids; report recall@k versus `nprobe`.
- [ ] **M2.4** Build a two-layer navigable small world graph by hand on 50 points; verify
      greedy descent reaches the true nearest neighbour.
- [ ] **M2.5** Full HNSW: `M = 16`, `efConstruction = 200`. Report recall@10 versus
      `efSearch` in {10, 50, 100, 200}.
- [ ] **M2.6** Report build time and query latency versus `N` in {1k, 10k, 100k}.
- [ ] **M2.7** Compare flat, LSH, IVF, and HNSW at `N = 50,000` on recall, latency, and
      memory.
- [ ] **H2.8** Filtered search: retrieve only within a tenant or date range. Show naive
      post-filtering drops recall and pre-filtering costs latency.
- [ ] **H2.9** Index staleness: measure the recall cost of an index that has not been
      updated after a batch of insertions.

## Module 03 — RAG Pipeline

- [ ] **E3.1** Corpus ingestion: parse, clean, and normalize 50 documents.
- [ ] **E3.2** Fixed-size chunking at 256 tokens with 10% overlap; print chunk boundaries and
      find a fact that gets split.
- [ ] **M3.3** Semantic chunking by embedding similarity; compare chunk quality on the split
      fact.
- [ ] **M3.4** Structural chunking with headings preserved; measure the retrieval gain.
- [ ] **M3.5** End-to-end retrieval on 50 questions; report recall@5.
- [ ] **M3.6** Implement a cross-encoder reranker over the top-20 candidates; report recall
      after reranking.
- [ ] **M3.7** Retrieval failure taxonomy on 50 questions: classify each failure as
      (a) not in corpus, (b) not retrieved, (c) buried, (d) ignored, (e) contradicted.
      Report the distribution.
- [ ] **H3.8** Context ordering: put the most relevant passage first, last, or middle.
      Report the accuracy for each — the "lost in the middle" effect, measured.
- [ ] **H3.9** Contradictory corpus: two documents disagreeing on the same fact. Report the
      system's behaviour and design a fix.

## Module 04 — RAG Evaluation

- [ ] **E4.1** Implement recall@k, precision@k, MRR, and NDCG@k; verify each against a
      hand-computed example.
- [ ] **M4.2** Build an evaluation set of 100 queries with graded relevance (0-3). Report
      recall@5, MRR, and NDCG@10 for the retriever.
- [ ] **M4.3** Implement BLEU-4 with brevity penalty; verify against a worked example.
- [ ] **M4.4** Implement ROUGE-1 and ROUGE-L; demonstrate the case where ROUGE rewards
      copying.
- [ ] **M4.5** Implement a contextual-similarity score with a stub embedding model; compare
      its behaviour against BLEU on a paraphrase and on a synonym swap.
- [ ] **M4.6** Faithfulness metric: split an answer into claims and check each against the
      context. Report faithfulness on 50 generated answers.
- [ ] **M4.7** Diagnose a low answer score: show a case with recall@5 = 0.95 and low answer
      score. Identify it as a generation problem, not a retrieval problem.
- [ ] **H4.8** LLM-as-judge with a structured rubric. Measure judge agreement with human
      labels on 100 pairs; report the confusion matrix.
- [ ] **H4.9** Judge position bias: present pairs in both orders and report the agreement
      rate. Correct for the bias.

## Module 05 — Prompt Engineering

- [ ] **E5.1** Zero-shot versus 3-shot versus 6-shot on a structured extraction task. Report
      format adherence and accuracy.
- [ ] **M5.2** Demonstrate that example ordering matters: permute the few-shot examples and
      report the variance in accuracy.
- [ ] **M5.3** Chain-of-thought on a multi-step arithmetic problem; report accuracy with and
      without.
- [ ] **M5.4** Self-consistency: sample 5 chains at temperature 0.7 and majority-vote. Report
      the gain and the 5x cost.
- [ ] **M5.5** ReAct loop with a stub tool environment; run to a correct answer and log
      every observation.
- [ ] **M5.6** Failure of ReAct without real observations: replace tool output with model
      hallucinated output and report the accuracy collapse.
- [ ] **M5.7** Automatic prompt engineering: generate 20 candidate prompts, evaluate on a
      validation set, select the best. Report the gain over the hand-written prompt.
- [ ] **H5.8** Prompt injection via a retrieved document into a naive concatenation prompt;
      demonstrate the attack and the fix with data labelling.
- [ ] **H5.9** Context-window experiment: fixed 8k window, vary the prompt from 500 to 6000
      tokens. Report accuracy versus prompt length and the degradation point.

## Module 06 — LLM Agents

- [ ] **E6.1** Agent loop with a tool registry: observe, reason, act, repeat. Verify
      termination on a bounded step budget.
- [ ] **M6.2** Tool calling with a typed schema; verify argument validation rejects malformed
      calls.
- [ ] **M6.3** Role-scoped registries: a read-only role with no write tools registered.
      Verify a write attempt fails at the registry, not the model.
- [ ] **M6.4** Error compounding: build a task with 10 steps at 5% per-step error. Report
      end-to-end success at `0.95^10`.
- [ ] **M6.5** Bounded side effects: a step budget, a side-effect budget, and an idempotency
      key per action.
- [ ] **M6.6** Replanning on observation: perturb the environment mid-task and measure the
      recovery rate with and without replanning.
- [ ] **M6.7** Memory: short-term scratch plus a retrieval-backed long-term store. Report
      recall of a fact stored 50 turns earlier.
- [ ] **M6.8** Two-agent decomposition: planner plus executor. Report the success rate against
      a single agent on the same tasks.
- [ ] **H6.9** Termination criteria: implement and measure how often each of four criteria
      (task complete, step budget, no progress, repeated action) fires first.
- [ ] **H6.10** Full agent with a sandboxed environment, an audit log, and a replay
      determinism test.

## Module 07 — Fine-Tuning

- [ ] **E7.1** LoRA on a single linear layer; implement `W + B A` with `A` zero-initialized.
      Verify the adapter starts as an exact no-op.
- [ ] **E7.2** Parameter count for `d = 4096`, rank `r` in {4, 8, 16, 32}. Report the ratio
      to full fine-tuning.
- [ ] **M7.3** Train LoRA on a small task; report the loss curve against full fine-tuning
      with matched steps.
- [ ] **M7.4** QLoRA: simulate 4-bit NF4 quantization of the frozen base (quantize-dequantize
      in double precision). Verify the reconstruction error bound.
- [ ] **M7.5** NF4 versus a uniform 4-bit grid on a Gaussian weight distribution; report
      mean squared error for each.
- [ ] **M7.6** Double quantization of the constants; report the additional error and the
      memory saved.
- [ ] **M7.7** DoRA: implement the magnitude-vector decomposition; report the delta over LoRA
      at matched rank.
- [ ] **M7.8** Merge LoRA into the base weights; verify the merged model produces identical
      logits.
- [ ] **H7.9** Multi-adapter serving: load two adapters, verify logits match each
      single-adapter model.
- [ ] **H7.10** PEFT decision experiment: three tasks (style, format, factual knowledge).
      Report which RAG versus fine-tuning wins for each and why.

## Module 08 — RLHF

- [ ] **E8.1** Bradley-Terry preference model: `loss = -log sigma(r_w - r_l)`. Train on a
      synthetic preference dataset; report accuracy.
- [ ] **M8.2** SFT stage: train on demonstrations; report the loss curve.
- [ ] **M8.3** Reward model training; report pairwise accuracy on held-out preferences and
      its calibration.
- [ ] **M8.4** Implement PPO-lite for a single-token policy with a KL penalty; report the
      reward trajectory.
- [ ] **E8.5** DPO loss implementation. Verify it against the reward-model formulation on
      the same pairs: report KL between the two implicit rewards.
- [ ] **M8.6** Derive the optimal policy form
      `pi* = pi_ref exp(r/beta) / Z` and verify it numerically by substituting into the DPO
      objective.
- [ ] **M8.7** Reward over-optimization: train against the reward model for many steps.
      Report reward-model score rising while true quality falls — plot both.
- [ ] **M8.8** KL penalty sweep over `beta`; report the reward-quality frontier.
- [ ] **H8.9** DPO hyperparameters: `beta` in {0.05, 0.1, 0.5, 1.0}. Report the margin
      distribution and stability for each.
- [ ] **H8.10** Reward hacking demonstration: construct a reward model exploitable by a
      length bias; show the policy exploiting it.

## Module 09 — Hallucination Mitigation

- [ ] **E9.1** Hallucination taxonomy: build 100 answers with labelled failure types. Report
      the distribution.
- [ ] **M9.2** Grounded generation: force every sentence to cite a context span. Report
      faithfulness before and after.
- [ ] **M9.3** Self-consistency: sample 5 answers, majority vote. Report the accuracy gain
      and 5x cost.
- [ ] **M9.4** Chain-of-verification: draft, generate verification questions, answer against
      the source, revise. Report faithfulness gain at ~2x cost.
- [ ] **M9.5** Abstention: allow "not in the context". Report the accuracy/coverage
      frontier — accuracy rises and coverage falls; plot both.
- [ ] **M9.6** Self-consistency plus verification; report whether the combination is
      additive.
- [ ] **M9.7** Citation validation: generate citations, verify each against the corpus,
      report the fabricated-citation rate.
- [ ] **H9.8** Numeric claim verification: extract numbers from the answer and check each
      against the source. Report the failure rate.
- [ ] **H9.9** Retrieval-augmented faithfulness versus closed-book: report faithfulness and
      the hallucination types each produces.

## Module 10 — AI Safety

- [ ] **E10.1** Input layer: normalization, invisible-character stripping, length caps.
- [ ] **M10.2** Decode detector for base64, hex, URL-encoding; depth-bounded with a cycle
      guard.
- [ ] **M10.3** Injection signature detection on 100 direct attack prompts; report the
      detection rate.
- [ ] **M10.4** Data labelling in the prompt: measure compliance with and without explicit
      delimiters and labels.
- [ ] **M10.5** Indirect injection via a retrieved document containing instructions.
      Measure compliance before and after data labelling.
- [ ] **M10.6** Tool gate with the seven ordered checks; verify a read-only role is denied
      before argument work.
- [ ] **M10.7** Arg-scoped approvals with expiry; verify timeout denies.
- [ ] **M10.8** Output pipeline: eight stages, each instrumented, fail closed on exception.
      Make one stage throw deliberately and verify the block.
- [ ] **M10.9** Base rate arithmetic: compute precision at several disallowed rates for a
      given TPR/FPR.
- [ ] **M10.10** Two-stage filtering: cheap high-recall filter plus a precise classifier.
      Report the false-refusal reduction.
- [ ] **M10.11** Canary token test over 1,000 requests; report the leak probability.
- [ ] **H10.12** Per-layer attribution across 100 attacks; report the uncaught count and the
      weakest layer.
- [ ] **H10.13** Mutation testing of the attack suite: apply 8 mutation operators to base
      attacks and report evasion per operator per layer.
- [ ] **H10.14** Audit log with a hash chain and an external anchor; verify tamper detection.

## Cross-Module

- [ ] **X1** End-to-end RAG evaluation harness: 100 queries, retrieval and generation
      reported separately, with failure taxonomy.
- [ ] **X2** Chunking ablation: fixed, overlap, semantic, structural. Report recall@5 and
      answer accuracy for each.
- [ ] **X3** Reranking ablation: no rerank, bi-encoder rerank, cross-encoder rerank. Report
      accuracy and latency.
- [ ] **X4** Attack suite integration: 200 attacks across 8 families, per-layer attribution,
      every finding converted to a regression test.
- [ ] **X5** Decision matrix: for 10 scenarios, choose among prompt-only, RAG, fine-tune,
      and agent — with a written justification each.
