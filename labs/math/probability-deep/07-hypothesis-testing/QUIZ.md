# Hypothesis Testing — Quiz (15 Questions with Worked Answers)

p-values, Type I/II errors, the Neyman–Pearson lemma, and the boundary failures of asymptotic theory.

---

## Q1 — The p-value is not P(H₀ true | data)
**Q.** What does a p-value actually compute, and what is the most common misreading?

**A.** The p-value is P(data at least as extreme as observed | H₀) — it conditions on H₀, not on the data. It is not P(H₀ | data). A small p-value means the observed data would be rare *if H₀ were true*; it says nothing directly about the probability that H₀ is true. The latter requires a prior over hypotheses (Bayes) or a different framework entirely. The practical consequence: "p = 0.03" does not mean "there is a 3% chance the effect is zero" — it means "if there were no effect, data this extreme would appear 3% of the time."

---

## Q2 — Type I vs Type II error
**Q.** Define α and β and state which is controlled by the test.

**A.** α = P(reject H₀ | H₀ true) — the false-positive rate, chosen by the analyst via the significance level. β = P(fail to reject H₀ | H₁ true) — the false-negative rate, determined by the effect size, sample size, and α. Power = 1 - β. The test controls α by construction; β is what you estimate in a power analysis *before* running the experiment, to choose n. A common confusion is to think "95% confidence" means "95% chance H₀ is true" — it does not; it means the procedure keeps the false-positive rate at 5% under H₀.

---

## Q3 — Neyman–Pearson lemma
**Q.** State the most powerful test for a simple H₀ vs simple H₁ and what it optimises.

**A.** For H₀: θ=θ₀ vs H₁: θ=θ₁, the most powerful level-α test rejects when L(θ₁)/L(θ₀) > k, with k chosen so P_{θ₀}(reject) = α. It maximises power among all tests with Type-I error ≤ α. So the rejection region is the high-likelihood-ratio set — "reject H₀ when the data is much more likely under H₁." This is the formal statement of intuition, and it extends to composite alternatives via the monotone-likelihood-ratio property, where the Karlin–Rubin theorem gives the UMP test.

---

## Q4 — p-value manipulation: peeking
**Q.** Why does checking a p-value every day and stopping at p<0.05 inflate the Type-I error?

**A.** The Type-I error guarantee α holds for a *single* look at the final dataset. If you check repeatedly and stop at the first p<0.05, you are performing a sequential test with a random number of looks; the *overall* Type-I error can be much larger than α — up to 2-3× for a few dozen peeks with continuous monitoring. The guarantee is restored by spending the α budget across looks (alpha-spending functions, Pocock/O"Brien–Fleming boundaries), or by fixing the sample size in advance. "Peeking" is the informal name for the same inflation; the formal name is the multiple-comparisons-over-time problem.

---

## Q5 — Neyman–Pearson needs a simple alternative
**Q.** What replaces the MP test when H₁ is composite?

**A.** When H₁: θ > θ₀ is composite, no single MP test exists in general. Two tools: (1) the UMP test from the Karlin–Rubin theorem when the family has monotone likelihood ratio — the same rejection region {L(θ)/L(θ₀) > k} is most powerful for *every* θ₁ > θ₀ simultaneously, hence UMP; (2) when the MLR property fails, fall back to likelihood-ratio tests with asymptotic size control via Wilks, or accept a non-UMP test and report power. For H₁: θ ≠ θ₀, UMP generally fails and the two-sided t-test is the practical default.

---

## Q6 — Multiple testing: Bonferroni vs BH
**Q.** When you run m tests, what does Bonferroni control, what does Benjamini–Hochberg control, and when do you use which?

**A.** Bonferroni rejects each hypothesis at level α/m, controlling the family-wise error rate (FWER) = P(≥1 false positive) ≤ α. It is conservative but valid for any number of tests and any dependence. Benjamini–Hochberg controls the false discovery rate (FDR) = E[false discoveries / total discoveries] ≤ α, a much weaker error measure that tolerates a controlled fraction of false positives among the discoveries. Use FWER when a single false positive is costly (e.g. one wrong drug approval); use FDR for screening studies with many hypotheses (genomics). The correction grows with m in the FWER case, only logarithmically in the FDR case.

---

## Q7 — Confidence intervals from the same machinery
**Q.** Why is a 95% CI equivalent to a two-sided test at α=0.05?

**A.** Define the CI as the set of parameter values not rejected by a two-sided α-test. Then 95% coverage ⟺ P(θ₀ ∈ CI) ≥ 0.95 ⟺ P(reject θ₀ at α=0.05) ≤ 0.05 — the same event, read from two sides. So the CI is the dual of the test: a value inside the CI is one you would not reject at α, and vice versa. This is why inverting a hypothesis test gives a CI, and why a 95% CI excludes exactly the values a 5% test would reject.

---

## Q8 — Power of a test: what it does and does not tell you
**Q.** State power and a common mistake when interpreting a non-significant result.

**A.** Power = P(reject H₀ | H₁ true) — the probability the test detects the effect if it exists. It depends on the effect size, sample size, variance, and α. A common misreading of p > 0.05: "accept H₀." This is wrong — failing to reject H₀ says the data is insufficient to distinguish H₀ from the alternatives sampled, not that H₀ is true. Under low power, even a large effect can give p > 0.05. The right statement under a non-significant result is "the confidence interval is wide" or "the study was under-powered to detect the claimed effect."

---

## Q9 — A p-value is uniform under H₀
**Q.** What distribution does the p-value follow under H₀, and how does that enable the KS-style calibration check?

**A.** If H₀ is true and the test is continuous, U = p-value ~ Uniform(0,1). So a histogram of p-values from many independent runs of the experiment should look uniform. A U-shaped distribution indicates the test is mis-calibrated (too many small and large p-values); a flat-top at 1 indicates conservatism; a U-shape at 0 indicates an anti-conservative test or heavy multiple-testing. This is the basis of p-value histograms in large-scale testing, and the theoretical justification for treating p ≤ 0.05 as a 5% false-positive rate procedure.

---

## Q10 — The likelihood-ratio test and Wilks
**Q.** State the LRT statistic and its asymptotic distribution; when does it fail?

**A.** Λ = 2(ℓ(θ̂) - ℓ(θ̃)) where θ̂ is the unconstrained MLE and θ̃ is the MLE under H₀. Wilks: under H₀, Λ ⇒ χ²_k with k the number of constraints. Failure modes: (1) boundary parameters — testing a variance = 0 puts the null on the edge of the parameter space and the χ² is replaced by a 50:50 mixture of χ²₀ and χ²₁; (2) non-identifiability under the null — the parameter under H₁ is not estimable under H₀, and the LRT needs a modified distribution; (3) small samples — the χ² approximation is asymptotic, poor for n < 30 in skewed families with a sup-norm bound.

---

## Q11 — A/B test: two-proportion Z-test
**Q.** State the test statistic and the null distribution.

**A.** For two groups with proportions p̂₁, p̂₂ and sizes n₁, n₂, H₀: p₁ = p₂. Under H₀ the pooled proportion p̃ = (x₁+x₂)/(n₁+n₂), and Z = (p̂₁ - p̂₂)/√(p̃(1-p̃)(1/n₁ + 1/n₂)) ~ N(0,1) asymptotically. The Z-statistic measures how many pooled-standard-errors separate the two sample proportions. A common error is to use the unpooled standard error for the test: that is the right choice for a *confidence interval* on the difference, but the hypothesis test under H₀ pools, because the null already specifies a common value. The CI and the test use different standard errors on purpose.

---

## Q12 — Multiple looks, one test: the sequential probability ratio test
**Q.** Why does the Wald SPRT need no p-value correction?

**A.** Because the Type-I / Type-II error budget is enforced *per sample*, not per look: at every step you stop when the likelihood ratio crosses a threshold set so that the overall error probabilities stay at α and β. No peeking correction is needed because the rule is the test — unlike the naive "stop at p<0.05", which is a data-dependent sample size that breaks the fixed-n guarantee. The SPRT is optimal in the sense of minimising the expected sample size for given (α, β), which is the practical win over fixed-sample testing.

---

## Q13 — Confidence interval for a proportion: Wald vs Wilson
**Q.** Why is Wald p̂ ± 1.96√(p̂(1-p̂)/n) unreliable for extreme p?

**A.** The Wald interval uses the normal approximation to the sampling distribution of p̂, which is poor when p̂ is near 0 or 1 — the distribution is skewed, and the interval can fall outside [0,1] or have near-zero coverage. The Wilson interval (score-based) is derived directly from the Z-statistic and stays in [0,1] by construction. At p̂ = 0.5 the two agree; near the boundaries Wilson is dramatically better. The general principle is the same as likelihood-ratio intervals for MLEs — inverting the test respects the shape of the sampling distribution.

---

## Q14 — Why "the data agrees with H₀" is unfalsifiable as stated
**Q.** What is the right way to conclude "the effect is negligible"?

**A.** A non-significant result only says "we failed to reject"; it does not bound the effect. The right tool is an *equivalence test* (TOST — two one-sided tests): declare the effect negligible only if the confidence interval sits entirely inside a pre-specified equivalence margin [-δ, δ]. If the 95% CI on the effect is contained in that interval, you conclude the effect is smaller than δ with 95% confidence — a positive statement, not the absence of evidence. TOST reverses the roles of H₀ and H₁, so the "burden of proof" moves to the claim of equivalence, which is where it belongs.

---

## Q15 — The t-test needs normality — but of what?
**Q.** The t-test assumes the data is normal; is that the right statement?

**A.** Not exactly. The t-test assumes the *sample mean* is (approximately) normally distributed. By the CLT this is approximately true for large n regardless of the underlying distribution, as long as the variance exists. For small n, the sampling distribution of X̄ tracks the data distribution, so the normality assumption matters. So the requirement is not "the data is normal" but "the mean's sampling distribution is approximately normal" — and for heavy-tailed data (e.g. Cauchy) that fails because the variance itself does not exist.

---

