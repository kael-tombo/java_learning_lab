# Lab 03: RAG System Architecture — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Three Chunkers (M)

Implement `fixedChunk(text, size, overlap)`, `sentenceChunk(text, maxTokens)`, and
`headingChunk(text)` with metadata on every chunk.

**Verify**: fixed chunking splits mid-sentence; sentence chunking does not; heading
chunking preserves `sectionPath`.

---

## Exercise 2: Contextual Prefix (M)

Given a chunk and its parent document, prepend
`"[Document: {title} | Section: {path}] "` to the text used for embedding. Keep the
display text unmodified.

**Verify**: recall@5 improves on a decontextualized query set (e.g. "revenue grew 3%").

---

## Exercise 3: Flat Dense Retrieval (E)

Build a `FlatIndex` over normalized embeddings; implement cosine top-k.

**Verify**: exact nearest neighbours returned.

---

## Exercise 4: BM25 From Scratch (M)

Implement BM25 with `k1=1.2`, `b=0.75` and the Lucene IDF form
`ln(1 + (N-df+0.5)/(df+0.5))`.

**Verify**: a rare term outscores a common term in the same document.

---

## Exercise 5: Hybrid Fusion (M)

Implement weighted normalized fusion and RRF (`k=60`).

**Verify**: weighted fusion breaks when all dense scores are equal (handle it); RRF is
stable.

---

## Exercise 6: Identifier Query Set (M)

Build 30 queries containing exact ids (`ERR-4021`, `SKU-99812`) and compare
recall@5 for dense-only, bm25-only, and hybrid.

**Expected**: hybrid wins on the identifier subset.

---

## Exercise 7: Rerank Stage (H)

Implement a cross-encoder stand-in (term overlap + proximity) over the top 50;
report the recall@5 delta and added latency.

---

## Exercise 8: Context Budget Packer (H)

Given a budget, pack chunks so the highest-scoring chunk is emitted last. Never drop
the schema or the question. Report what was dropped.

**Verify**: budget never exceeded; every emitted id is real.

---

## Exercise 9: Citation Verification (M)

Parse `[n]` citations; reject any id outside the supplied chunk set. Report citation
precision and recall against gold supporting chunks.

---

## Exercise 10: Abstention and Threshold Sweep (M)

Sweep a retrieval-score threshold; report coverage (fraction answered) and accuracy
(accuracy on answered). Choose an operating point.

---

## Exercise 11: Faithfulness Check (M)

Split answers into atomic claims; score each against the retrieved context; report
faithfulness and the unsupported claim list.

---

## Exercise 12: Idempotent Ingest (M)

Upsert by `sha256(docId + chunkText)`; tombstone missing ids; verify the second run
inserts zero chunks.

---

## Exercise 13: Per-Stage Latency Trace (E)

Instrument ingest, embed, dense search, lexical, fusion, rerank, generation. Verify the
stage sum matches the total within 5%.

---

## Exercise 14: Evaluation Harness (H)

Build 50 gold questions with gold chunk ids; compute recall@1/5/10, MRR, nDCG@10.

---

## Exercise 15: Config Sweep (H)

Sweep chunker x chunk size x fusion weight x rerank on/off; report the quality
frontier and mark the knee.

---

## Exercise 16: HyDE (H)

Generate a hypothetical answer per query, embed that instead of the query, and measure
the recall delta.

---

## Exercise 17: Parent-Child Index (M)

Index child chunks, return the parent for context. Compare tokens used and answer
quality.

---

## Exercise 18: Corrective RAG (H)

Grade the retrieved chunks (relevance, support) and re-retrieve once when the grade is
low. Measure the recall gain and the latency cost.

---

## Stretch A: Multi-Vector per Chunk (H)

Store title, body, and inferred-question embeddings per chunk; query all three. Measure
the recall gain versus 3x storage.

---

## Stretch B: Query Decomposition (H)

Split multi-hop questions into sub-queries, retrieve per sub-query, fuse. Measure
recall and answer quality on multi-hop questions.

---

## Stretch C: Late Chunking (H)

Embed the whole document, then mean-pool per chunk span. Compare against early chunking
on a corpus where context matters.

---

## Stretch D: Index Freshness Test (M)

Simulate a deleted section, re-ingest, verify it stops being retrievable and that
answers citing it are rejected.

---

## Stretch E: Cost Model (H)

Compute cost per query: embed + search + rerank + generation (chunk tokens dominate).
Sweep k and chunk size; report the quality/cost frontier.

---

## Stretch F: Adversarial Corpus (H)

Insert documents containing prompt-injection instructions. Verify the guardrail
catches them and that answers citing them are flagged.

---

## Stretch G: Multi-Index Routing (M)

Route queries to per-corpus indexes based on intent; measure the recall gain and the
routing accuracy.

---

## Stretch H: Cache Layers (M)

Cache embeddings, query embeddings, and rerank scores; measure hit rates on a
repeated-query workload.