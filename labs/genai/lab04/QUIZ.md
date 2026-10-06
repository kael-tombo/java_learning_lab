# Lab 04: RAG System Design — Quiz

## Questions

**Q1.** RAG primarily adds which kind of memory?
- a) Parametric / compressed weight memory
- b) Non-parametric external document memory
- c) KV cache
- d) Prompt cache

**Q2.** Which chunking approach best preserves self-contained meaning?
- a) Fixed 512-char with no overlap
- b) Sentence- or structure-aware chunking
- c) One chunk per document
- d) Word-count-based with 0 overlap

**Q3.** Query and document embeddings must come from...
- a) Any model with the same dimension
- b) The same model and version
- c) The largest available model
- d) Different models for better diversity

**Q4.** Cosine similarity equals dot product when vectors are...
- a) Zero-mean
- b) L2-normalized
- c) Integer-valued
- d) Sparse

**Q5.** Dense retrieval's classic weakness is...
- a) Latency
- b) Exact-token matches like part numbers and error codes
- c) Memory footprint
- d) Multilingual support

**Q6.** Why min-max normalize before mixing dense and BM25 scores?
- a) To make them faster
- b) Cosine in [-1,1] and BM25 in [0,20] are not commensurable
- c) To remove duplicates
- d) To sort the results

**Q7.** Reciprocal Rank Fusion's advantage is...
- a) It always ranks better than BM25
- b) It needs no score calibration
- c) It uses embeddings
- d) It is exact

**Q8.** A cross-encoder reranker is more accurate than a bi-encoder because it...
- a) Runs on fewer documents
- b) Scores query and document jointly
- c) Is trained on more data
- d) Uses smaller vectors

**Q9.** Where should the highest-scoring chunk sit in the context?
- a) First, always
- b) Anywhere
- c) Near the question (late in the context)
- d) Only in the system message

**Q10.** The correct first debugging step when RAG answers are wrong is to...
- a) Rewrite the prompt
- b) Measure retrieval recall@k
- c) Switch to a bigger model
- d) Lower the temperature

**Q11.** `INSUFFICIENT_CONTEXT` sentinels enable...
- a) Faster decoding
- b) Abstention when evidence is absent
- c) Better tokenization
- d) Larger batches

**Q12.** What should the index namespace include?
- a) Only the collection name
- b) Corpus version and embedding model version
- c) The tenant id only
- d) The user's locale

**Q13.** Fixed-size chunks that are too small cause...
- a) Higher latency
- b) Lost context and worse retrieval
- c) Tokenizer errors
- d) Duplicate hits

**Q14.** Adding a small retrieval-score threshold improves a system mainly by...
- a) Increasing coverage
- b) Increasing accuracy on answered queries via abstention
- c) Reducing index size
- d) Improving embedding quality

**Q15.** Faithfulness measures whether the answer...
- a) Matches the reference answer string exactly
- b) Is supported by the retrieved context
- c) Is grammatically correct
- d) Is fast to produce

---

## Answers

1. **b** — RAG is non-parametric memory; weights are the parametric part.
2. **b** — sentence and structure boundaries keep chunks self-contained.
3. **b** — mismatched embedding spaces make cosine meaningless.
4. **b** — with `|v| = 1`, cosine reduces to the dot product.
5. **b** — near-duplicate vector neighbours mask exact lexical matches.
6. **b** — unnormalized fusion is dominated by whichever scale is larger.
7. **b** — rank-based fusion is immune to score scale differences.
8. **b** — cross-attention between query and document needs both at once.
9. **c** — recency effects make late context weigh more.
10. **b** — if the gold chunk is not retrieved, no prompt fixes it.
11. **b** — the model can decline instead of fabricating.
12. **b** — either changing requires full re-ingest.
13. **b** — sub-50-token chunks lose referents ("it", "the company").
14. **b** — you trade coverage for precision on answered items.
15. **b** — faithfulness is support-by-context; relevance is answer-worthiness.

## Score Guide

14-15: ready for ai-engineering lab02/lab03.
11-13: redo Exercises 5, 7, 12.
0-10: reread THEORY sections 3-10.