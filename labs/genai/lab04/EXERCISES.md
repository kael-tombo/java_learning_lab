# Lab 04: RAG System Design — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Cosine Similarity with Normalization (E)

Implement `double cos(double[] a, double[] b)` and `double[][] normalize(double[][] vs)`.
After normalization assert `cos(a,b) == dot(a,b)` within 1e-9.

**Hint**: guard `|a| == 0`.

---

## Exercise 2: In-Memory Flat Index (E)

Build `FlatIndex` with `add(String id, double[] vec)` and `List<Hit> search(double[] q, int k)`
returning id + score, sorted descending.

**Verify**: brute force returns the true nearest neighbour.

---

## Exercise 3: Top-K Recall Harness (E)

Given 50 queries with gold doc ids, compute `recall@1`, `recall@5`, `recall@10` and
`mrr@10`.

**Expected**: recall is non-decreasing in k.

---

## Exercise 4: Three Chunker Strategies (M)

Implement:
- `fixedChunk(text, size, overlap)` — character-based with overlap.
- `sentenceChunk(text, maxTokens)` — split on `[.!?]`, greedily pack.
- `headingChunk(text)` — split on markdown `#` levels, keep the path.

**Verify**: fixed chunking splits at least one sentence mid-way; sentence chunking
never does; heading chunking preserves `sectionPath` in metadata.

---

## Exercise 5: Contextual Chunk Prefixing (M)

Given a chunk plus its parent document, prepend
`"[Document: {title} | Section: {path}] "` to the text before embedding.
Measure `recall@5` before and after on the eval set.

**Expected**: recall improves for chunks that are decontextualized
("revenue grew 3%") because the prefix restores the subject.

---

## Exercise 6: BM25 From Scratch (M)

Implement BM25 with `k1 = 1.2`, `b = 0.75`:
- IDF with the Lucene-style `ln(1 + (N - df + 0.5)/(df + 0.5))` guard.
- Length normalization `tf * (k1+1) / (tf + k1*(1 - b + b*dl/avgdl))`.

**Verify**: a rare term scores higher than a common term in the same document.

---

## Exercise 7: Hybrid Search with Score Normalization (M)

Combine dense and BM25 scores two ways:
- (a) min-max normalize each per query, then `0.6*dense + 0.4*bm25`.
- (b) Reciprocal Rank Fusion with `k = 60`.

**Verify**: (a) breaks when all dense scores are equal (division by zero) — handle
the degenerate case; (b) needs no normalization and is stable.

---

## Exercise 8: Keyword-Heavy Query Set (M)

Build 20 queries containing exact identifiers (`ERR-4021`, `SKU-99812`) and
measure recall@5 for dense-only vs hybrid.

**Expected**: dense-only is weaker on exact ids; hybrid closes the gap.

---

## Exercise 9: Cross-Encoder Reranker Simulation (H)

Implement a `Reranker` that scores `(query, chunk)` with a term-overlap +
proximity heuristic (a stand-in for a real cross-encoder). Rerank the top-50 ANN
hits down to top-5 and report recall@5 delta and added latency.

**Expected**: recall@5 improves; latency roughly doubles.

---

## Exercise 10: Context Budget Packer (M)

Given `maxContext`, `promptOverhead`, `maxNewTokens`, and scored chunks, select
and order chunks to fit the budget: highest score first, but emit the
**lowest-scoring** kept chunk last so it sits nearest the question.

**Verify**: never exceeds the budget; every emitted chunk id is preserved.

---

## Exercise 11: Citation Parsing and Verification (M)

Generate answers with `[n]` citations. Write `CitationChecker` that:
1. Extracts all `[n]`.
2. Rejects any `n` not in the provided chunk set.
3. Returns `citationPrecision` and `citationRecall` vs gold supporting chunks.

**Verify**: an answer citing `[9]` with only 5 chunks is rejected.

---

## Exercise 12: Abstention Threshold (H)

Sweep a retrieval-score threshold from 0 to 1. For each threshold report coverage
(fraction answered) and accuracy (fraction of answered that are correct).

**Expected**: a curve with a clear operating point; e.g. answering 60% of queries
at 95% accuracy beats answering 100% at 78%.

---

## Exercise 13: Incremental Ingest with Hashing (M)

Store `sha256(chunkText + docId)`; on re-ingest, insert only new chunks and mark
missing ones as tombstoned. Report counts of inserted, skipped, tombstoned.

**Verify**: re-running the ingest is a no-op the second time.

---

## Exercise 14: End-to-End Pipeline with Trace (H)

Wire ingest -> embed -> index -> retrieve -> assemble -> generate (stub model) and
emit a trace per query showing chunk count, tokens used, retrieval score, latency
per stage.

**Verify**: sum of stage latencies equals total (within 5%).

---

## Stretch A: Query Expansion (H)

Expand a short query into 3 variants (synonym substitution from a small map,
question rephrasing with a template, decomposition) and fuse the result lists.
Report recall@5 lift.

---

## Stretch B: Multi-Document Answer Synthesis (H)

Allow up to 5 chunks from different docs; require the generator to reconcile
conflicting numbers and cite both. Write a conflict detector that flags when two
chunks state different values for the same entity+attribute.

---

## Stretch C: Freshness Test (M)

Simulate a deleted policy section, re-ingest, and assert the retriever no longer
returns the tombstoned chunk — and that answers citing it are rejected.