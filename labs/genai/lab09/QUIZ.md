# Lab 09: LLM Evaluation & Benchmarks — Quiz

**Q1.** The three questions evaluation must keep separate are...
- a) speed, cost, accuracy
- b) correctness, faithfulness, and quality/helpfulness
- c) precision, recall, F1
- d) input, output, total tokens

**Q2.** BLEU is primarily a...
- a) Recall metric with no brevity handling
- b) n-gram precision metric with a brevity penalty
- c) Embedding similarity metric
- d) Edit-distance metric

**Q3.** BLEU scores from different systems are not comparable if they use different...
- a) Prompts
- b) Tokenizers
- c) GPUs
- d) Seeds

**Q4.** A brevity penalty of 1 occurs when the candidate is...
- a) Shorter than the reference
- b) At least as long as the reference
- c) Empty
- d) Untokenizable

**Q5.** ROUGE is recall-oriented, so a verbose candidate...
- a) Is penalized heavily
- b) Can score well
- c) Always scores 1.0
- d) Cannot be computed

**Q6.** BERTScore's advantage over BLEU/ROUGE is...
- a) It is cheaper
- b) It matches on contextual embeddings, tolerating paraphrase
- c) It requires no references
- d) It produces an integer score

**Q7.** BERTScore is a poor measure of correctness because...
- a) It is slow
- b) A fluent paraphrase of a wrong answer scores well
- c) It ignores order
- d) It only works on short texts

**Q8.** LLM judges exhibit position bias, meaning...
- a) They prefer longer answers only
- b) The first-presented option wins more often
- c) They prefer their own outputs
- d) They refuse often

**Q9.** The fix for position bias is to...
- a) Always present A first
- b) Randomize order and check both-order consistency
- c) Use a 1-10 scale
- d) Increase temperature

**Q10.** Why do LLM judges cluster on 3-4 scale values rather than 1-10?
- a) The API truncates scores
- b) Judges are low-resolution near the middle of the scale
- c) 1-10 scores are illegal
- d) Temperature affects scores

**Q11.** Judge-human agreement must be re-measured periodically because...
- a) Humans drift
- b) A drifted judge silently invalidates every metric computed with it
- c) The judge gets slower
- d) Prompts change

**Q12.** Intrinsic hallucination is detected best by...
- a) String matching against a corpus
- b) Entailment of answer claims by the provided context
- c) Length checks
- d) Repetition detection

**Q13.** The highest-value items in an evaluation suite are often...
- a) Easy questions
- b) Unanswerable questions, which test abstention
- c) Long documents
- d) Multilingual items only

**Q14.** Demographic parity compares...
- a) True positive rates across groups
- b) Positive prediction rates across groups
- c) Calibration across groups
- d) Error rates overall

**Q15.** Demographic parity holding while equal opportunity fails means...
- a) No bias exists
- b) The group with a lower base rate has a higher TPR
- c) The model is unbiased
- d) Sample size was too small

**Q16.** Marginal parity checks can hide...
- a) Sampling noise
- b) Intersectional gaps
- c) Prompt bugs
- d) Tokenization issues

**Q17.** Refusal rate and over-refusal rate must be reported together because...
- a) They are the same number
- b) Guardrail tuning moves them in opposite directions
- c) Only one is measurable
- d) They cancel out

**Q18.** Splitting a benchmark by user/session rather than by query prevents...
- a) Slower evaluation
- b) Near-duplicate leakage between train and test
- c) Judge drift
- d) Cost overruns

**Q19.** Paired comparisons have lower variance because...
- a) They use more items
- b) Both systems are evaluated on identical items
- c) They avoid bootstrapping
- d) They use a stronger model

**Q20.** Benchmark contamination invalidates a score because the model may have...
- a) Memorized the benchmark
- b) Used a different tokenizer
- c) Run at higher temperature
- d) Used more retrieval

---

## Answers

1. **b** — conflating them is how misleading claims get made.
2. **b** — clipped n-gram precision, geometric mean, brevity penalty.
3. **b** — n-gram counts depend on the tokenization.
4. **b** — `BP = 1` when `|cand| >= |ref|`.
5. **b** — recall rewards coverage; hence report length alongside.
6. **b** — contextual embeddings match paraphrases.
7. **b** — semantic similarity is not truth.
8. **b** — first position wins disproportionately.
9. **b** — randomize and require agreement in both orders.
10. **b** — judges are low-resolution in the middle of wide scales.
11. **b** — the metrics look fine while meaning nothing.
12. **b** — NLI/entailment is the direct test of support.
13. **b** — confident answers to unanswerable questions are the worst failure.
14. **b** — `P(yhat=1)` equality across groups.
15. **b** — a lower base rate with the same positive rate implies a higher TPR.
16. **b** — aggregate parity can coexist with large subgroup gaps.
17. **b** — tightening a filter raises refusal and over-refusal together.
18. **b** — paraphrases of the same query otherwise straddle the split.
19. **b** — item difficulty cancels.
20. **a** — the score then measures recall, not capability.

## Score Guide

18-20: ready for ai-engineering labs 07 and 08.
14-17: redo Exercises 3, 8, 13.
0-13: reread THEORY sections 2-8.