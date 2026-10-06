# Lab 07: AI Testing & Evaluation — Quiz

**Q1.** The test pyramid for AI differs from classical testing because...
- a) AI has no bugs
- b) There is no oracle for free-form output, so deterministic assertions must be pushed down
- c) AI tests are faster
- d) AI needs less coverage

**Q2.** Which component can be tested with a pure round-trip property?
- a) Answer quality
- b) A tokenizer
- c) Faithfulness
- d) Helpfulness

**Q3.** A scripted LLM client should throw when its script is exhausted because...
- a) Scripts are short
- b) It proves the loop converged within the planned steps
- c) It saves memory
- d) Providers return errors

**Q4.** Golden sets must be split by...
- a) Query text
- b) User or session
- c) Category
- d) Date

**Q5.** Splitting by query rather than by user causes...
- a) Higher cost
- b) Near-duplicate leakage between train and test
- c) Slower runs
- d) Judge drift

**Q6.** Property-based tests are valuable because they find...
- a) Slow stages
- b) Input classes hand-written cases miss
- c) Memory leaks only
- d) Cost regressions

**Q7.** The most valuable items in an eval suite are often...
- a) Easy questions
- b) Unanswerable questions
- c) Long documents
- d) Multilingual items

**Q8.** Mutation testing proves...
- a) The code is well written
- b) The suite actually detects behavioural changes
- c) Coverage is high
- d) Performance is fine

**Q9.** A suite that survives a deliberate mutation is...
- a) Well designed
- b) Not testing the behaviour it claims to
- c) Too slow
- d) Redundant

**Q10.** Reports must be per category because...
- a) Categories are cheaper
- b) An aggregate can hide a collapse in one intent
- c) Aggregates are invalid
- d) Judges prefer them

**Q11.** A missing canary metric should be treated as...
- a) A pass
- b) A breach
- c) A warning
- d) A retry

**Q12.** Judge-human agreement must be re-measured because...
- a) Humans drift
- b) A drifted judge silently invalidates every metric computed with it
- c) The judge gets slower
- d) Prompts change

**Q13.** Proxy metrics (schema validity, refusal) are used for gating because...
- a) They are more accurate
- b) They are cheap enough for 100% coverage
- c) They require no data
- d) They are free of bias

**Q14.** Judge-based metrics are used for trending because...
- a) They are cheap
- b) They are more accurate but too expensive for 100% coverage
- c) They are deterministic
- d) They need no rubric

**Q15.** Paired testing is more sensitive because...
- a) It uses more items
- b) Item difficulty cancels out
- c) It avoids bootstrap
- d) Judges improve

**Q16.** "Within noise" is a valid result because...
- a) It saves time
- b) The CI included zero; claiming a win would be false
- c) It is common
- d) The judge was unsure

**Q17.** Refusal and over-refusal must be reported together because...
- a) They are the same number
- b) Guardrail tuning moves them in opposite directions
- c) Only one is measurable
- d) They must sum to 1

**Q18.** The sampled offline evaluation loop exists to...
- a) Reduce cost only
- b) Keep the golden set representative of production
- c) Increase traffic
- d) Replace the golden set

**Q19.** Every production incident should produce...
- a) A post-mortem only
- b) A new golden regression case
- c) A new prompt
- d) A config change

**Q20.** pass@k means...
- a) The probability the first sample is correct
- b) The probability that at least one of k samples is correct
- c) The percentage of passing tests
- d) The k-th percentile of latency

---

## Answers

1. **b** — no oracle means assertions must be deterministic where possible.
2. **b** — `decode(encode(s)) == s` needs no judgement.
3. **b** — extra turns mean the loop did not converge.
4. **b** — paraphrase overlap must not straddle the split.
5. **b** — leak-free evaluation requires user-level splits.
6. **b** — nulls, unicode, huge inputs, interleavings.
7. **b** — they test abstention, which is the worst failure mode.
8. **b** — detection is the property under test.
9. **b** — it is asserting nothing about behaviour.
10. **b** — averages hide regressions by construction.
11. **b** — fail closed.
12. **b** — metrics keep being produced and stop meaning anything.
13. **b** — 100% coverage is only affordable for cheap signals.
14. **b** — accuracy per item is far higher.
15. **b** — differences on identical items are much less noisy.
16. **b** — a claim inside the CI is a false claim.
17. **b** — tightening raises both.
18. **b** — a frozen suite drifts out of distribution.
19. **b** — that is how a bug stays fixed.
20. **b** — `1 - C(n-c,k)/C(n,k)`.

## Score Guide

18-20: ready for lab 08 and lab 10.
14-17: redo Exercises 7, 8, 11.
0-13: reread THEORY sections 2-8.