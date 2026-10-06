# Lab 09: LLM Evaluation & Benchmarks — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Exact Match and Normalized Match (E)

Implement `exactMatch(pred, gold)` and `normalizedMatch` (lowercase, strip
punctuation, collapse whitespace, optional article removal).

**Verify**: `"The  Cat."` vs `"cat"` matches normalized, not exact.

---

## Exercise 2: Token F1 (E)

Implement token-level precision, recall, and F1 with multiset intersection
(counts, not set membership).

**Verify**: `"a b c"` vs `"b c d"` gives P=2/3, R=2/3, F1=2/3.

---

## Exercise 3: BLEU-4 from Scratch (H)

Implement:
1. n-gram clipped precision for n=1..4.
2. Brevity penalty with a configurable closest reference length.
3. Geometric mean of precisions.

**Verify**: identical strings give BLEU-4 = 1.0; a 2-word candidate against a
10-word reference gives a non-zero BP and low score.

---

## Exercise 4: BLEU Traps (M)

Demonstrate two known traps:
1. BLEU changes when the tokenizer changes (character vs whitespace vs a mock BPE).
2. Corpus BLEU != mean sentence BLEU.

**Expected**: report both values; explain why published BLEU numbers state the
tokenizer.

---

## Exercise 5: ROUGE-N and ROUGE-L (M)

Implement clipped n-gram recall for ROUGE-1/2 and LCS-based ROUGE-L (F-measure with
`beta = 1.2`). Compute ROUGE-Lsum for a 3-sentence summary.

**Verify**: a verbose candidate scores well on ROUGE — report length alongside.

---

## Exercise 6: BERTScore Proxy (M)

Since no model is available, implement BERTScore using a deterministic embedding
(character 3-gram hashing to 256 dims) with greedy matching.

**Expected**: high score for a paraphrase, low for a semantically different answer —
demonstrating the paraphrase tolerance that n-gram metrics lack.

---

## Exercise 7: Length Bias in Overlap Metrics (M)

Compute F1 and ROUGE-L for candidates of length 5, 10, 20 containing the gold
answer plus padding.

**Expected**: both metrics inflate with padding; report the inflation factor.

---

## Exercise 8: Hallucination Detection with Claim Splitting (M)

Split an answer into atomic claims, then score each against evidence using
exact + normalized substring matching plus a token-overlap threshold. Return
`faithfulness`, `supported`, and `unsupported` lists.

**Verify**: a claim stating a price absent from the evidence is unsupported.

---

## Exercise 9: Self-Consistency Voting (M)

Sample k answers at temperature 0.7, extract the final answer, and compute the
agreement rate. On a set with 20% unanswerable questions, measure how often the
majority wrongly answers an unanswerable item.

**Expected**: agreement rate is a usable confidence proxy; document the threshold.

---

## Exercise 10: Unanswerable Detection (H)

Build an abstention policy from evidence-support fraction and agreement rate. Sweep
the threshold; report coverage vs accuracy-on-answered.

**Expected**: a curve with a clear operating point (Exercise 12 in Lab 04 style).

---

## Exercise 11: Bias Metrics (M)

Implement demographic parity, equal opportunity, and bias ratio for a binary
classifier. Evaluate on a synthetic set with controlled group skew.

**Verify**: report all three per group; identify a case where demographic parity
holds but equal opportunity does not.

---

## Exercise 12: Intersectional Analysis (M)

Extend Exercise 11 to two attributes (4 groups). Find a case where every marginal
parity check passes but an intersectional gap is large.

**Expected**: this is the standard "marginals hide" result.

---

## Exercise 13: Judge Position Bias (M)

Run a stub judge on 100 pairs; count A-wins vs B-wins. Then run with order reversed.

**Expected**: a consistent bias. Implement order-randomized judging with both-order
consistency checks.

---

## Exercise 14: Judge-Human Agreement (M)

Score the same items with a rubric judge and a hand-written "human" function (an
intent classifier with deliberate mistakes). Report agreement, and simulate judge
drift by degrading the judge over time.

**Expected**: show that metrics computed with a drifted judge become meaningless
without anyone noticing.

---

## Exercise 15: Refusal vs Over-Refusal (M)

Build two sets: 100 disallowed prompts and 100 benign lookalikes (e.g. "how do I
kill a process" vs "how do I murder a character"). Measure refusal rates.

**Expected**: report both numbers; show that tuning to reduce one inflates the other.

---

## Exercise 16: Jailbreak Success Rate (M)

Implement 10 attack transformations (prefix injection, role play, base64 payload,
leetspeak, many-shot, instruction override, encoding, hypothetical framing,
split request, translation). Measure compliance rate before/after each guardrail.

---

## Exercise 17: Statistical Significance (M)

Implement a paired bootstrap test over per-item score deltas. Report the 95% CI and
whether it excludes zero.

**Expected**: a 3-point difference on 100 items often has a CI spanning zero;
a 10-point difference does not.

---

## Exercise 18: Benchmark Builder + Regression Runner (H)

Implement a JSONL benchmark format (query, gold, category, unanswerable flag,
allowed_sources) and a runner that evaluates a system, writes per-category metrics,
and diffs against a baseline run.

**Verify**: a deliberate regression in one category is localized in the report.

---

## Stretch A: Entailment Scorer (H)

Implement a lexical-entailment scorer (hypothesis tokens must be covered by premise
tokens with a threshold) and compare it against exact matching for detecting
contradictions.

---

## Stretch B: Toxicity Classifier (M)

Train a small classifier on synthetic labeled toxicity data; report AUC and the score
distribution; inspect the top false positives manually.

---

## Stretch C: Contamination Check (H)

Implement a n-gram overlap detector between your benchmark and a reference corpus.
Report the fraction of items with suspicious 13-gram overlap.

---

## Stretch D: Prompt Variance (M)

Run the same benchmark across 5 prompt phrasings and report per-item variance.

**Expected**: prompt variance rivals model-to-model differences on small deltas.

---

## Stretch E: Multi-Turn Evaluation (H)

Extend the benchmark to multi-turn with conversation-level success criteria
(does the final turn satisfy the original goal). Report per-turn and end-to-end.

---

## Stretch F: Cost-Quality Frontier (H)

For a set of configurations (model tier, retrieval k, rerank on/off), plot cost per
request against quality. Mark the knee point.