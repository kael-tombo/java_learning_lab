# Interview: Hypothesis Testing

### Q1. Your p-value is 0.01. What can you say? What can't you say?
**A.** Can: "Assuming H₀ and the model, data this extreme or more occur with probability 1%." Cannot: P(H₀ | data) = 0.01, "there's a 1% chance the null is true," or "the effect is large/practically important." p mixes effect size and n: with n = 10⁵ a 0.1σ difference gives p < 0.01. Report p with the effect estimate and its interval (lab 06), or go Bayesian (lab 08) if you need P(H₀ | data).

### Q2. Why does 20 tests at α = 0.05 give a 64% false-positive rate, and what are the fixes?
**A.** FWER = 1 − (1 − α)^m = 1 − 0.95²⁰ = 0.6415 under the global null (independence). Fixes by goal: **FWER** control — Bonferroni α/m (valid under any dependence, via the union bound) or Holm's step-down (same validity, uniformly more power); **FDR** — Benjamini–Hochberg at q when you expect many true signals (genomics, large A/B platforms). Best: reduce m by declaring one primary endpoint up front, correct only the exploratory tail.

### Q3. We peek at our A/B test daily and stop at p < 0.05. What's wrong?
**A.** The nominal α assumes one look at fixed n. Repeated looks multiply opportunities to cross the boundary, and stopping depends on the data, so realized FWER ≫ 0.05 — with continuous monitoring a fixed boundary is eventually crossed even under H₀ (a random walk crosses any fixed level a.s.). Fixes: group-sequential boundaries (O'Brien–Fleming spends α slowly at early looks), the SPRT (Wald's likelihood-ratio boundaries with error controlled under optional stopping), or α-spending functions over a planned number of looks.

### Q4. Student's t vs Welch vs permutation — which do you use?
**A.** Default **Welch** for two-sample means: it doesn't assume σ₁² = σ₂², and Student's pooled version is badly liberal when the smaller group has the larger variance (SE underestimated ~1.7×, size ~26% in the classic n₁ = 10/σ₁² = 4σ₂² setup). Use **permutation** when n is small and distributions are visibly non-normal (valid under exchangeability, exact by enumeration for tiny n), and **Student** only when equal variances are justified (e.g. by design). For proportions far from 0.5 or tiny counts: exact (Fisher) instead of χ².

### Q5. Design a study to detect a 2% conversion lift on a 10% baseline. What do you specify before collecting data?
**A.** (1) **Effect**: δ = 0.02 absolute (relative 20%); (2) **α and power**: 0.05 two-sided, 0.80; (3) **n per arm** from the two-proportion formula: n ≈ (z₀.₀₂₅√(2p̄(1−p̄)) + z₀.₂₀√(p₁(1−p₁)+p₂(1−p₂)))²/δ² with p̄ = 0.11, p₁ = 0.10, p₂ = 0.12 — roughly 3 500–3 600 per arm; (4) **primary metric and correction** for any guardrail metrics; (5) **stopping rule** (fixed n or pre-planned sequential), analysis date, and exclusion rules. Anything chosen after data collection belongs in a new, clearly-labeled analysis.

### Q6. p = 0.03 came from a dashboard with 20 metrics. Now what?
**A.** First, reconstruct the actual family: if all 20 were inspected with equal standing, FWER = 1 − 0.95²⁰ = 0.6415 and Bonferroni requires p ≤ 0.0025 — 0.03 does not survive; Holm is uniformly more powerful and still won't save it; BH at q = 0.05 keeps a p = 0.03 only if 0.03 ≤ 0.05·k/20, i.e. k ≥ 12 — twelve of the twenty metrics must be that significant. If instead one primary endpoint was pre-registered and 19 were exploratory, the primary stands uncorrected and the others are labeled hypothesis-generating. The answer that gets hired: state which scenario held *before* quoting any number.

### Q7. Your test rejects, but the 95% CI is [0.01, 0.02] on an effect nobody cares about. What do you tell the PM?
**A.** That the p answered "is it exactly zero?" — a question no product decision asks — and the interval answers the real one: the effect is between 0.1% and 2% with 95% confidence. Decision framing: at n = 100 000, a 0.001σ difference clears α = 0.05 routinely (z ≈ 3.16), so significance is a *sample-size* report, not an importance report. Recommendation: define the smallest effect worth shipping (MDE), check whether the interval's band lies above it — if [0.01, 0.02] straddles your relevance threshold, the honest verdict is "real but undecidable at this n," and the cost of n vs the value of δ decides whether to run more.

### Q8. Sequential testing: your SPRT colleague stops at n = 40; you must justify fixed n = 63.
**A.** Both control Type I at α; they differ in *when* error is spent. The SPRT stops as soon as the log-likelihood ratio crosses ±log((1−β)/α): expected sample size ≈ (boundary)/KL(p₀‖p₁) — O(1/KL), so easy cases stop early and hard cases approach the fixed-n requirement. Fixed n = 63 buys a *pre-computable* power (0.80 at λ = 2.81) and simpler reporting; the cost is data from every unit regardless. Choose SPRT when the effect is usually large or data is expensive (adverse-event monitoring); choose fixed n (or group-sequential O'Brien–Fleming) when regulators or reviewers need a single pre-declared sample size. What you cannot do: peek at fixed-n data and stop early — that reverts to the unbounded-FPR random walk.

### Q9. Two studies, same effect, opposite verdicts — p = 0.04 and p = 0.08. Reconcile.
**A.** Don't compare p's: compare *estimates and intervals*. Two 95% intervals for the same quantity overlap heavily whenever the p's straddle 0.05 — the discrepancy is threshold noise, not evidence of heterogeneity. The correct reconciliation: pool or meta-analyze the estimates (fixed effect if same design, random effects if not), which is mathematically equivalent to testing the *combined* evidence rather than demanding each study individually cross 1.96. Then say what each study's interval contributed: the narrower one carries more information regardless of which side of 0.05 its point estimate sat on.

### Tips for this topic
- Have the family-size arithmetic instant: 1 − 0.95²⁰ = 0.6415 and Bonferroni 0.0025 — it demonstrates the point faster than any explanation.
- Default answers with a named procedure: Welch (not pooled t), Holm (not raw Bonferroni), permutation (small skewed n), Fisher (expected < 5).
- Whenever asked "is it significant?", answer with an interval first — interviewers are testing whether you've escaped the star habit.
