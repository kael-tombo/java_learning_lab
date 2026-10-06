# Lab 07: AI Testing & Evaluation — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Deterministic Doubles (E)

Implement `ScriptedLlmClient` (throws when exhausted), `HashingEmbedder`, `SeededRng`,
`FakeClock`.

**Verify**: two runs with the same seed produce identical output.

---

## Exercise 2: Tokenizer Round-Trip Property (E)

`decode(encode(s)) == s` for 1,000 generated strings including unicode, emoji,
whitespace, and empty input.

**Verify**: zero failures; note that empty input needs an explicit case.

---

## Exercise 3: Metric Unit Tests (E)

Hand-compute BLEU-4, ROUGE-L, token F1, and IoU for known inputs; assert the
implementation matches to 1e-9.

---

## Exercise 4: Golden Set Loader (M)

JSONL format with `{id, input, gold, category, unanswerable, allowed_sources}`;
content hash; frozen semantics (editing a gold requires a version bump).

---

## Exercise 5: Property-Based Parser Test (H)

Generate malformed inputs; assert `parse` returns a typed error and never throws.

**Verify**: 10,000 generated inputs, zero uncaught exceptions.

---

## Exercise 6: Property Invariants Across Stages (H)

No nulls, bounded sizes, no PII in outputs, chunkers never emit empty chunks.

---

## Exercise 7: Evaluation Runner (M)

Run a suite; produce per-category accuracy, format validity, refusal, faithfulness;
compare against a baseline with regression flags.

**Verify**: a single-category collapse is localized.

---

## Exercise 8: Paired Statistics (H)

Paired bootstrap over item deltas; Wilson intervals for rates; verify a fake
improvement is reported as within noise.

---

## Exercise 9: Sample Size Calculator (E)

`n = 960/d^2` plus the absolute-change variant; report ladder feasibility at a traffic
rate.

---

## Exercise 10: Retrieval Recall Harness (M)

recall@k, MRR, nDCG against a labelled chunk set; filtered and unfiltered separately.

---

## Exercise 11: Safety Suite (M)

Disallowed and benign-lookalike sets; refusal and over-refusal both reported; jailbreak
success rate.

---

## Exercise 12: Abstention Test (M)

Unanswerable set; decline rate and false-decline rate reported separately.

---

## Exercise 13: Judge Calibration Harness (H)

Judge vs hand-labelled set; agreement rate; simulate drift and show metrics become
uninterpretable.

---

## Exercise 14: Mutation Testing (H)

Apply 8 deliberate mutations; verify the suite fails for each. Report the detected
count.

---

## Exercise 15: Flakiness Detection (H)

Run the suite 20 times; report any test with variable outcomes; fix by injecting
doubles.

---

## Exercise 16: Leakage and Contamination Check (M)

Detect near-duplicate queries across train/eval splits and n-gram overlap with
reference corpora.

---

## Exercise 17: Sampled Offline Evaluation (H)

Sample production traffic with a documented strategy; score offline; feed failures into
the golden set; report the loop's effect on coverage.

---

## Exercise 18: Benchmark Latency Harness (M)

Measure p50/p95/p99 and tokens/request; detect a latency regression between baselines.

---

## Stretch A: Hypothesis Tests for Multiple Systems (H)

Holm correction across 5 systems; report which survive.

---

## Stretch B: Differential Testing (H)

Compare two pipeline versions on random inputs; report behavioural divergences.

---

## Stretch C: Fuzzing the Agent Loop (H)

Generate random tool outputs; assert the loop terminates and stays within budget.

---

## Stretch D: Fairness Regression Suite (H)

Per-group metrics per category; alert on intersectional gaps.

---

## Stretch E: Shadow Evaluation at Scale (H)

Mirror traffic to a candidate; score both; report paired deltas at zero user risk.

---

## Stretch F: Golden Set Auto-Refresh (H)

Detect drift between the golden set and traffic; propose new cases; verify the
proposals are valid and non-duplicate.