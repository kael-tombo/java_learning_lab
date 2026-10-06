# Law of Large Numbers — Quiz (15 Questions with Worked Answers)

Convergence modes, the strong/weak laws, Borel–Cantelli, and the gap between "almost surely" and "in expectation."

---

## Q1 — Convergence modes: a ⇒ P a ⇒ L¹ a ⇒ L² ⇏ the reverse
**Q.** State the chain of implications between modes of convergence and give a counter-example to the strongest one.

**A.** Almost-sure ⇒ in probability ⇒ in L¹; L² ⇒ L¹; almost-sure does NOT imply L¹ in general. Classic counter-example: X_n = n·1_{[0,1/n]} on [0,1]. X_n → 0 a.s. (for every ω>0 eventually X_n(ω)=0), but E|X_n| = 1 for all n. So a.s. convergence does not upgrade to L¹. Conversely L¹ ⇒ convergence in probability (Markov: P(|X_n-X|>ε) ≤ E|X_n-X|/ε). The strictness is the whole point: "converges a.s." only controls the typical outcome, not the average.

---

## Q2 — Weak vs strong law: why the difference matters
**Q.** The weak law gives "for every ε, P(|S̄_n - μ| > ε) → 0"; the strong law gives "P(S̄_n → μ) = 1". What extra does the strong law give?

**A.** The weak law controls each n separately: for any *fixed* n you cannot say S̄_n is near μ, only that the probability of a large gap is small. It allows |S̄_n - μ| > ε to happen infinitely often, as long as the n where it happens become rarer. The strong law says the *entire sequence* S̄_n converges — the set of sample paths along which the gap fails to vanish has measure zero. For an algorithm that must be right on the run it executes (not just on average over runs), the strong law is the relevant statement.

---

## Q3 — Chebyshev proof of the weak law
**Q.** Prove the weak law for i.i.d. X_i with variance σ² via Chebyshev.

**A.** S̄_n = (1/n)ΣX_i. Var(S̄_n) = σ²/n. Chebyshev: P(|S̄_n - μ| ≥ ε) ≤ Var(S̄_n)/ε² = σ²/(nε²) → 0. So for every ε > 0, P(|S̄_n-μ| ≥ ε) → 0 — weak convergence. The proof is one line, but it only needs finite variance; the strong law needs the sharper Kolmogorov argument with sub-sequence control.

---

## Q4 — Kolmogorov's SLLN conditions
**Q.** State the Kolmogorov strong law and why E|X| < ∞ is needed.

**A.** If X_i are i.i.d. with E|X_1| < ∞, then S̄_n → E[X_1] a.s. The condition E|X_1| < ∞ is necessary: if the mean does not exist, S̄_n does not converge to any finite limit — e.g. the Cauchy distribution, for which S̄_n has the same Cauchy distribution for every n. Kolmogorov's proof bootstraps the weak law on a geometric subsequence n_k = α^k and uses Borel–Cantelli to control the gaps. The bounded-variance version is easier but too strong for practice.

---

## Q5 — Borel–Cantelli and divergence
**Q.** State both Borel–Cantelli lemmas and when one can be upgraded to "occurs infinitely often."

**A.** BC1: If Σ P(A_n) < ∞ then P(A_n i.o.) = 0. BC2: If the A_n are *independent* and Σ P(A_n) = ∞, then P(A_n i.o.) = 1. So for independent events, "Σ P(A_n) = ∞" is exactly the threshold: the events occur infinitely often if and only if the sum diverges. Example: independent coin flips of a fair coin produce a head infinitely often, since Σ 1/2 = ∞; flipping a coin with success 1/n² produces finitely many successes, since Σ 1/n² < ∞. Independence is essential for BC2 — for dependent events only BC1 survives.

---

## Q6 — The LLN needs independence — how badly?
**Q.** Does the LLN hold for a stationary, ergodic process?

**A.** Not in the i.i.d. statement, but a version survives: for a stationary ergodic sequence, S̄_n → E[X_1 | I] a.s. where I is the invariant σ-algebra. If the process is *strictly* stationary and ergodic, S̄_n → E[X_1] a.s. So the i.i.d. assumption is a convenience, not the load-bearing one; ergodicity is. For a Markov chain, S̄_n → the stationary expectation for the same reason. Without ergodicity — e.g. two regimes chosen by a one-time coin flip — S̄_n converges to a *random* limit instead.

---

## Q7 — LLN for unbounded variance
**Q.** Does the weak law hold if Var(X) = ∞ but E|X| < ∞?

**A.** Yes — the weak law needs only E|X| < ∞. The Chebyshev proof fails (Var is infinite), but the truncation argument goes through: truncate at n, apply the bounded-variance weak law to the truncated variables, and show the truncation error vanishes in probability. So "finite variance" is sufficient for the weak law but not necessary. For the strong law the sharp condition is exactly E|X| < ∞.

---

## Q8 — A.s. convergence does not imply uniform rate
**Q.** S̄_n → μ a.s. — is the rate always n^{-1/2}?

**A.** No — the rate depends on the distribution and the mode. In probability with finite variance, the typical deviation is σ/√n (CLT). With heavy tails (Pareto with exponent α ∈ (1,2)), the typical deviation is n^{-(α-1)/α}, slower than n^{-1/2}. With only finite first moment, the deviation can be arbitrarily slow. So the LLN guarantees convergence, not a rate; if you need a rate you need either finite variance plus Chebyshev/CLT, or a large-deviation theorem under stronger conditions.

---

## Q9 — Law of the iterated logarithm
**Q.** State the LIL and how it sharpens the CLT's n^{-1/2}.

**A.** For i.i.d. with mean 0, variance σ², and finite (2+δ) moment: limsup (S_n)/(√(2n log log n)) = σ a.s. The LIL says the typical fluctuation is not exactly σ√n; the running maximum over n grows like √(2n log log n). It is the precise a.s. rate, sitting between the CLT (distributional, fixed n) and the strong law (no rate). A common misuse is to apply CLT-style ±2σ intervals to the *running maximum* — the LIL says that misses the true envelope by a √(2 log log n) factor.

---

## Q10 — LLN for non-identical distributions
**Q.** Poisson(λ_n) variables with λ_n growing — does S̄_n/n concentrate?

**A.** Not necessarily. The LLN needs a control on the variance of the average, which follows from the variances being summable after normalisation: Var(S_n) = Σ Var(X_i), and S̄_n/n concentrates iff Var(S_n)/n² → 0. For independent Poisson(λ_i), Var(S_n) = Σ λ_i, so Var(S_n)/n² = (Σλ_i)/n² — this vanishes iff (Σλ_i)/n² → 0, i.e. the average rate λ̄_n = (Σλ_i)/n grows slower than n. If λ_n grows like n, the average variance stays Θ(1) and S_n/n does not concentrate to its mean.

---

## Q11 — LLN vs CLT: what is the real distinction?
**Q.** Why do both sound like "the average converges," yet one has a rate and one does not?

**A.** The LLN identifies the *limit*: S̄_n → μ. The CLT identifies the *shape* of the fluctuation around that limit: √n(S̄_n - μ) ⇒ N(0, σ²). The CLT is the rate statement. The LLN alone is consistent with arbitrarily slow convergence; the CLT pins the deviation to order n^{-1/2}. In practice you use the LLN to justify using the sample mean at all, and the CLT to build confidence intervals around it.

---

## Q12 — Ergodic averages in simulation
**Q.** Why is "run the Markov chain for T steps and average" a LLN statement, and how is the variance estimated?

**A.** By the ergodic theorem, the time average (1/T)Σf(X_t) converges to E_π[f] as T → ∞. The variance of the estimate is Var(f)/T times the integrated autocorrelation time τ_int — correlated samples inflate the effective variance by τ_int. Practical implication: the standard error is not σ/√T but σ√(τ_int/T). Methods like batch means estimate τ_int by averaging over non-overlapping batches. Ignoring autocorrelation under-estimates the error bar, sometimes badly.

---

## Q13 — Strong law implies convergence in probability
**Q.** Why?

**A.** A.s. convergence implies convergence in probability by a standard argument: P(|S̄_n-μ|>ε) ≤ P(limsup |S̄_n-μ|>ε), and the latter is 0 when S̄_n→μ a.s. (the limsup set is contained in the non-convergence set, which has measure 0). So the strong law is the stronger statement, and the weak law is the weaker corollary. In a problem asking "does S̄_n converge to μ?", the strong law answers it; the weak law answers a different—weaker—question about each fixed n.

---

## Q14 — A.s. convergence of S̄_n to a random limit
**Q.** When can S̄_n converge to a *non-constant* limit?

**A.** When the X_i are not identically distributed enough to pin the mean down — e.g. a mixture: with probability 1/2 all X_i ~ N(0,1), with probability 1/2 all ~ N(10,1). S̄_n → N(0,1)-mean 0 on the first event and → 10 on the second, so the limit is the random variable 0 or 10 with probability 1/2 each. This is the non-ergodic case: a one-time random choice propagates to the average. The fix is to condition on the regime (the invariant σ-algebra), which is exactly Kolmogorov's E[X_1 | I] statement.

---

## Q15 — LLN in the generalised sense: Birkhoff
**Q.** State Birkhoff's ergodic theorem and what it adds to Kolmogorov's.

**A.** Birkhoff: for a measure-preserving transformation T on a probability space and f ∈ L¹, the time average (1/n)Σ f(Tᵏx) converges a.s. to E[f | I], the conditional expectation given the invariant σ-algebra. Kolmogorov's SLLN is the special case where T is the shift on i.i.d. sequences (I is trivial, so E[f|I] = E[f]). Birkhoff is the version used in statistical mechanics and Markov chains, where the invariant measure replaces the i.i.d. structure.

---

