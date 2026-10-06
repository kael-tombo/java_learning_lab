# Lab 03: RAG System Architecture — Quiz

**Q1.** The offline/online split exists because...
- a) Ingestion is faster
- b) Ingestion is expensive and failure-prone; the query path has a latency budget
- c) Models require it
- d) Indexes are cheaper offline

**Q2.** The highest-leverage retrieval decision is...
- a) The index type
- b) Chunking
- c) The embedding model
- d) The generator model

**Q3.** Chunks below ~50 tokens fail mainly because...
- a) They are slow to embed
- b) They lose their referent and stop being self-contained
- c) The index rejects them
- d) They cost more per byte

**Q4.** Contextual prefixes fix decontextualized chunks by...
- a) Making them longer
- b) Prepending document/section context to the text that is embedded
- c) Splitting them further
- d) Removing overlap

**Q5.** Dense retrieval's classic weakness is...
- a) Latency
- b) Exact identifiers like part numbers and error codes
- c) Memory
- d) Multilingual support

**Q6.** Why is RRF preferred over weighted fusion by default?
- a) It is always more accurate
- b) It needs no score calibration between cosine and BM25
- c) It is faster
- d) It supports filters

**Q7.** Weighted fusion fails when...
- a) k is too large
- b) Score scales are not commensurable, or all scores in a list are equal
- c) The corpus is large
- d) BM25 is used

**Q8.** A cross-encoder reranker beats the bi-encoder because it...
- a) Uses less memory
- b) Scores query and document jointly with full attention
- c) Runs at query time only
- d) Supports filters

**Q9.** The strongest evidence should be placed...
- a) First in the context
- b) Last, nearest the question
- c) In the middle
- d) In the system message

**Q10.** `INSUFFICIENT_CONTEXT` enables...
- a) Faster decoding
- b) Abstention when evidence is absent
- c) Better tokenization
- d) Larger batches

**Q11.** `finish_reason == length` usually means...
- a) The model refused
- b) The context was truncated
- c) The index is stale
- d) Temperature was 0

**Q12.** ANN recall@10 of 0.95 caps end-to-end answer quality at...
- a) 1.00
- b) 0.95
- c) 0.85
- d) 0.50

**Q13.** Over-fetching before reranking helps because...
- a) It is faster
- b) It raises the probability the gold chunk is available to the reranker
- c) It reduces cost
- d) It improves chunking

**Q14.** The correct first debugging step when answers are wrong is to...
- a) Rewrite the prompt
- b) Measure retrieval recall@k
- c) Switch models
- d) Lower temperature

**Q15.** A namespace must include the embedding model version because...
- a) It speeds up search
- b) Vectors from different models are not comparable
- c) It reduces memory
- d) Providers require it

**Q16.** HyDE works by...
- a) Splitting the query
- b) Embedding a hypothetical answer instead of the query
- c) Using a larger k
- d) Reranking twice

**Q17.** Parent-child indexing means...
- a) Indexing parents, returning children
- b) Indexing small children, returning larger parents for context
- c) Two indexes
- d) Hierarchical clustering

**Q18.** Citation validation should check that cited ids...
- a) Exist in the supplied chunk set
- b) Are the highest scoring
- c) Are unique
- d) Are short

**Q19.** The unanswerable subset exists to measure...
- a) Speed
- b) Abstention quality: decline rate and false-decline rate
- c) Index size
- d) Rerank accuracy

**Q20.** `index_age_hours` is alerted on because...
- a) Stale indexes are slower
- b) Stale indexes silently degrade answer quality
- c) They cost money
- d) They break the namespace

---

## Answers

1. **b** — the query path cannot afford to re-parse and re-chunk.
2. **b** — chunking determines whether the right evidence is even retrievable.
3. **b** — "revenue grew 3%" without a subject is not a retrievable unit.
4. **b** — the embedded text differs from the displayed text.
5. **b** — near-unique strings land in arbitrary directions.
6. **b** — ranks need no calibration, and RRF cannot divide by a zero range.
7. **b** — min-max normalization divides by zero when all scores match.
8. **b** — full attention over both texts.
9. **b** — recency effects weight late context most strongly.
10. **b** — the model can decline instead of fabricating.
11. **b** — the prompt exceeded the context budget.
12. **b** — a chunk never retrieved cannot be used.
13. **b** — the reranker can only reorder what it receives.
14. **b** — if the gold chunk is absent, no prompt fixes it.
15. **b** — mixing spaces yields meaningless similarities with no error.
16. **b** — the hypothetical answer lives closer to the answer region.
17. **b** — precision for retrieval, context for the generator.
18. **a** — range checks catch a real ordering bug class.
19. **b** — confident answers to unanswerable questions are the worst failure.
20. **b** — nothing errors; answers just quietly get worse.

## Score Guide

18-20: ready for lab 07 (evaluation) and lab 08 (observability).
14-17: redo Exercises 5, 8, 12.
0-13: reread THEORY sections 2-8.