# Interview: Probability Axioms

### Q1. Monty Hall — should you switch?
**A.** Yes; switching wins 2/3. Your initial pick is wrong with probability 2/3, and when it is wrong the host's constrained reveal leaves the car behind the other door. Formally: P(car behind initial) = 1/3, P(car behind other | host opened a goat door) = 2/3, because the host's action is uninformative only in the branch where you had already won (he must open a goat door either way).

### Q2. P(A|B) or P(B|A)? Base rate 1%, sensitivity 99%, specificity 95%.
**A.** The 99% is P(+|D); the question asks P(D|+). Split: P(+) = 0.01·0.99 + 0.99·0.05 = 0.0594, so P(D|+) = 0.0099/0.0594 = 1/6 ≈ 16.7%. Equivalently prior odds 1:99 × likelihood ratio 19.8 = posterior odds 0.2:1 → posterior 1/6. This is the single most common probability error in product interviews.

### Q3. Are mutually exclusive events independent?
**A.** Never, when both have positive probability. Disjoint means P(A ∩ B) = 0; independence requires P(A ∩ B) = P(A)P(B) > 0. They cannot both hold. The intuition test: knowing A occurred *tells* you B did not — maximal information transfer, i.e. dependence.

### Q4. Why does P(A ∪ B) subtract the intersection, and what about three events?
**A.** Because A ∩ B is counted once in each marginal. |A ∪ B| = |A| + |B| − |A ∩ B|. For three: sum the singles, subtract all three pairwise intersections (each double-counted), add back the triple intersection (removed three times, counted once). Sanity anchor: P = 1 exactly when the three events cover Ω.

### Q5. P(X = 0.5) = 0 for a continuous X — can you condition on {X = 0.5}?
**A.** Not by the definition P(A|B) = P(A ∩ B)/P(B), which is 0/0. Two standard answers: (i) condition on a shrinking interval P(A | X ∈ [x, x+ε]) and take the limit ε → 0, which yields the density-based version; (ii) the regular conditional distribution — a version of P(A|X = x) defined for almost every x, unique only almost everywhere. In practice, code uses the density/PDF value (or the posterior at a point), which is why densities can exceed 1 while probabilities cannot.

### Q6. Follow-up: how would you test this in code?
**A.** Assert normalization after every operation (|Σp − 1| < 1e-12), compare double results against a `BigInteger` rational oracle on small spaces, and simulate the analytic cases: Monty Hall → 0.666… ± 1/(2√N), two-dice union → 14/36, medical test → 1/6.

## Whiteboard tips

- Name the rule before you write symbols (product rule, total probability, Bayes, inclusion–exclusion).
- Substitute numbers only after the symbolic step; the structure is what gets graded.
- Sanity-bound first: a posterior must sit between the prior and what the likelihood ratio can afford.

### Q7. P(A ∩ B) = 0.3, P(A) = 0.5, P(B) = 0.6 — independent? disjoint?
**A.** P(A)·P(B) = 0.30 = P(A ∩ B), so the events are *exactly independent* — and definitely not disjoint (a disjoint pair would have intersection 0). The two properties can co-exist only if at least one event has probability zero.

### Q8. Why countable additivity rather than just finite?
**A.** Finite additivity permits non-principal ultrafilter charges on infinite sets: a distribution where every finite subset has probability 0 yet the whole space has probability 1 — an "equally likely" distribution on ℕ that puts mass nowhere. Countable additivity forces P(⋃ₙ Aₙ) = Σₙ P(Aₙ), making infinite sequences behave like Lebesgue measure, which is precisely what the almost-sure convergence results in lab 05 consume.

### Q9. How would you unit-test a probability library?
**A.** Property tests (every distribution sums to 1; complements and unions consistent; conditioning preserves total mass), then analytic oracles computed by hand: two-dice P(sum ≥ 9) = 10/36, Monty Hall switch = 2/3, medical-test posterior = 1/6, and a BigInt rational path cross-checked against doubles to 1e-12.
