# llm-genai-deep — Quiz

15 multiple-choice questions across the ten modules. Answer key and score guide at the
bottom.

## Questions

**Q1.** Why does a RAG system use a bi-encoder for retrieval and a cross-encoder for
  reranking?
- A) Bi-encoders are more accurate
- B) A bi-encoder encodes query and document independently, so the index can be
      precomputed; a cross-encoder models their joint interaction, which is more accurate
      but too slow to run over the whole corpus
- C) Cross-encoders use less memory
- D) Bi-encoders cannot be used for search

**Q2.** Which single change most reliably improves RAG answer quality in practice?
- A) A larger embedding model
- B) Better chunking, including structural awareness and overlap
- C) Higher generation temperature
- D) A longer prompt template

**Q3.** In HNSW, which parameter can be tuned at query time without rebuilding the index?
- A) `M`
- B) `efConstruction`
- C) `efSearch`
- D) The dimensionality

**Q4.** You measure recall@10 = 0.95 but the answer is wrong. What is the right conclusion?
- A) Retrieval is failing
- B) The fact was retrieved; this is a generation or grounding problem. Retrieval and
      generation must be evaluated separately
- C) The embedding model is too small
- D) Re-chunk the corpus

**Q5.** Which metric is most appropriate when relevance is graded?
- A) Recall@k
- B) NDCG@k
- C) Accuracy
- D) BLEU

**Q6.** Why do RAG systems place the highest-relevance passage in the middle of the context
  as often as at the start?
- A) Token limits require it
- B) Attention is most sensitive to the beginning and end of a long context — the
      "lost in the middle" effect, measured rather than assumed
- C) The retriever produces it in that order
- D) It improves perplexity

**Q7.** LoRA adds which parameters to a weight matrix?
- A) A full-rank correction of the same size
- B) Low-rank factors `A` and `B` with `W + delta W = W + BA`, `rank(A,B) << rank(W)`
- C) A scalar bias per row
- D) A quantized copy of `W`

**Q8.** QLoRA's 4-bit NF4 is called "information-theoretically optimal" because:
- A) It uses fewer bits than every other format
- B) For normally distributed weights, its quantization points are placed to minimize
      expected quantization error
- C) It is lossless
- D) It compresses the activations instead of the weights

**Q9.** DPO's advantage over RLHF's PPO pipeline is that it:
- A) Requires no preference data
- B) Skips the explicit reward model and the RL loop, turning preference learning into a
      classification problem on chosen/rejected pairs
- C) Guarantees no over-optimization
- D) Works without a reference model

**Q10.** Reward over-optimization occurs because:
- A) The learning rate is too high
- B) As the policy moves against the reward model it enters regions where the reward model
      is inaccurate, so its score rises while true quality falls
- C) The KL penalty is too weak a hyperparameter only
- D) The reference model is too small

**Q11.** A plausible-looking citation to a paper that does not exist is best described as:
- A) A faithfulness failure
- B) Fabrication — and it requires citation validation with a structured mechanism, not
      better prompting
- C) A retrieval failure
- D) An over-generalization

**Q12.** Which mitigation measurably reduces hallucination at roughly 2x cost by separating
  generation from checking?
- A) Self-consistency
- B) Chain-of-verification
- C) Higher `top_k`
- D) Greedy decoding

**Q13.** Why must the RAG failure taxonomy distinguish "not in the corpus" from "not
  retrieved"?
- A) For reporting clarity only
- B) They need different fixes: one requires corpus expansion, the other requires better
      retrieval. Conflating them sends the work in the wrong direction
- C) They have different metrics
- D) Only one is measurable

**Q14.** At a 0.1% disallowed rate with 1% FPR and 95% recall, roughly what share of safety
  flags are false positives?
- A) About 5%
- B) About 50%
- C) About 91%
- D) About 99%

**Q15.** Why is the tool layer the only structural safety boundary in an agentic system?
- A) It is the slowest layer
- B) Capability is decided by code there: a read-only role has no write tool registered, so
      there is nothing to inject into. Other layers raise cost or detect; they do not
      prevent
- C) It is the only layer with a model in it
- D) It runs after generation

## Answer Key

| Q | Answer | Why |
|---|--------|-----|
| 1 | B | Independent encoding makes the index precomputable; joint encoding is accurate but O(corpus). |
| 2 | B | Chunking determines whether the answer-bearing span is retrievable at all. |
| 3 | C | `M` and `efConstruction` are build-time; `efSearch` is a pure query-time dial. |
| 4 | B | High recall with a wrong answer localizes the fault to generation or grounding. |
| 5 | B | NDCG discounts by rank and accommodates graded relevance labels. |
| 6 | B | U-shaped position sensitivity is measured on long contexts. |
| 7 | B | Parameter count becomes `2dr` instead of `d^2`. |
| 8 | B | NF4 places quantiles of a normal distribution, minimizing expected error. |
| 9 | B | DPO rearranges the Bradley-Terry likelihood of the optimal policy into a binary loss. |
| 10 | B | Goodhart's law: optimizing a proxy moves off the proxy's valid domain. |
| 11 | B | Fabricated citations need verification against the corpus, not better prompting. |
| 12 | B | Generate, then generate verification questions answered against the source, then revise. |
| 13 | B | Corpus expansion and better retrieval are opposite responses to different problems. |
| 14 | C | Precision `= 0.95*0.001 / (0.95*0.001 + 0.01*0.999) ≈ 0.087`; ~91% are wrong. |
| 15 | B | Registered capability is a code-level property; prompt-level controls are probabilistic. |

## Score Guide

| Score | Verdict |
|-------|---------|
| 15/15 | Ready to design and review production LLM systems. Push into modules 08 and 10. |
| 12-14 | Solid. Revisit your misses against THEORY.md. |
| 9-11 | Knows the techniques, not the trade-offs. Redo Q1, Q4, Q9, Q13, Q15. |
| 6-8 | Re-read THEORY.md, then redo EXERCISES for modules 01, 03, 07. |
| 0-5 | Restart with modules 01, 03, and 04 before fine-tuning and RLHF. |

## Scoring Notes

- Single answer per question; no partial credit.
- Retake after re-reading the relevant module.
- Mastery threshold: 13/15 with no misses on Q1, Q4, Q9, Q13, Q14.
