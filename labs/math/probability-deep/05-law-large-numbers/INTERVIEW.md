# Interview: Law of Large Numbers and CLT

### Q1. What is the difference between the LLN and the CLT?
**A.** The LLN says *where* X̄ converges (to μ): consistency of the average. The CLT says *how* it fluctuates around μ: (X̄ − μ)/(σ/√n) → N(0,1), giving the rate 1/√n and the Gaussian shape that yields confidence intervals. LLN alone cannot produce a 95% interval — it has no speed; the CLT alone doesn't guarantee convergence to the right value. SLLN (Kolmogorov 1930) is stronger still: P(lim X̄ₙ = μ) = 1 for the entire sequence, requiring only E|X| < ∞.

### Q2. A casino averages millions of bets. Does the CLT tell you its profit distribution?
**A.** Yes, under i.i.d. bets with finite variance: total profit after N bets ≈ N·E[profit per bet] ± √N·σ, so the *relative* deviation shrinks as 1/√N — that is the house's business model. The CLT says nothing about the *maximum* drawdown or the worst day (those need ruin theory/extreme-value methods), and if a bet type has infinite variance the Gaussian approximation fails and profits jump rather than drift.

### Q3. When does the CLT fail? Give three concrete cases.
**A.** (1) **Infinite variance** — Pareto with α ≤ 2 or St. Petersburg: sums converge to a non-Gaussian stable law (Lévy 1925), sample means wander with n^{1/α−1} speed instead of √n. (2) **Dependence** — averaging an AR(1) with ρ = 0.9 gives Var(X̄) = (σ²/n)(1 + 2Σρₖ) ≈ 19σ²/n; n_eff ≈ n/19, so the Gaussian approximation with the wrong scale under-covers. (3) **Dominant single term / non-identical summands** violating Lindeberg — e.g. one component is 99% of the sum's variance: the "sum" is essentially that one variable, and its shape rules, not normality.

### Q4. How would you verify a CLT assumption in code before quoting an interval?
**A.** Three checks: moments exist (tail index / QQ-plot on log of exceedances — or at minimum flag when sample kurtosis explodes); independence (ACF of the stream, then compute n_eff and use it); adequacy of n (Berry–Esseen bound C·ρ/(σ³√n) with best-known C ≤ 0.4748, or block-means QQ-plot). If any check fails: switch to t-interval, Chebyshev bound, or bootstrap rather than pretending the normal approximation applies.

### Q5. Two simulations of the same process: one's SE halves with 4n, the other's doesn't. What's wrong with the second?
**A.** Most likely the draws aren't independent — either the parallel workers reused a seed (identical streams), or the process is autocorrelated (use n_eff), or n silently saturated (buffer overflow/cap). Less exciting but common: summation drift in float32 hides the scaling. The test is mechanical: measure SE at n, 4n, 16n — it must fall as 1, 1/2, 1/4 for any valid LLN/CLT process; deviations localize the bug before any statistics are trusted.

### Q6. "How many samples do I need?" — give the full answer structure.
**A.** Three formulas, pick by what you're willing to assume. (1) Proportion, normal approximation: n ≥ z²·p(1−p)/e²; worst case p = 0.5 gives the blanket n ≥ 0.9604/e² — e = 0.02 → 2401, e = 0.03 → 1068. (2) Mean with known σ: n ≥ (1.96σ/e)². (3) No normality assumed: Chebyshev's n ≥ σ²/(e²δ), about 5× larger at the same e (384 vs 2000 for σ = 1, e = 0.1). Then state the assumptions out loud — independence (else n_eff), finite variance (else no 1/√n exists at all), and no selection across multiple metrics (else the nominal rate is fiction).

### Q7. Ten metrics monitored, one shows p = 0.03, leadership wants it shipped. What do you say?
**A.** Under the global null, P(at least one p < 0.05 of ten) = 1 − 0.95¹⁰ = 0.401 — a 3-in-10 chance of a "winner" from noise alone, and p = 0.03 wouldn't even survive Bonferroni (threshold 0.005). The CLT doesn't save you: it makes each *individual* test's null distribution right, and the error is in the selection across tests, not within any one. Pre-register the primary metric, or apply Holm's step-down, and quote the family-wise rate next to the p-value.

### Q8. What is Lindeberg's condition actually checking, in words?
**A.** That no single summand dominates: for every fixed ε > 0, the total variance carried by terms larger than ε√n must vanish. Lindeberg's 1922 theorem needs only that plus finite variances — identical distribution is *not* required. The failure case is intuitive: one measurement being 99% of the sum's variance means the "sum" is really that one variable, so its shape rules and no Gaussian emerges. Practical check: look at each component's variance share of the total; if the largest share isn't → 0 as n grows, the CLT citation is premature.

### Q9. How do you *know* your 95% interval is actually 95%?
**A.** You run the coverage experiment: R = 10 000 independent replications at the n you intend to publish, count how often the interval contains μ, and report 95.0% ± 0.43% (the √(0.95·0.05/R) Monte Carlo band). Two failure classes it exposes that no formula check does: undercoverage from dependence or estimated σ (→ t instead of z, n_eff instead of n), and overcoverage from a conservative bound quoted as an interval (Chebyshev at 1/k² covers *at least* — quoting it as "the probability" both misstates and overstates).

### Tips for this topic
- Lead with the assumption list (i.i.d., finite variance, n_eff) before quoting any ± figure — it signals you know the ± is conditional.
- Have one failure example ready: St. Petersburg (infinite mean) or AR(1) ρ = 0.9 (n/19) is enough.
- Quote √n as the punchline: half the error bar costs 4× the data. Anyone who has run a study feels that number.
