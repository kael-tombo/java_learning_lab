# Common Mistakes: Probability Axioms

### 1. Assuming outcomes are equally likely
P(A) = |A|/|Ω| holds only when the measure on Ω is uniform. A loaded die still has sample space {1,…,6} but P({6}) = 1/2. "There are 6 options, so 1/6" is a modeling assumption, not an axiom.

### 2. Adding probabilities of overlapping events
P(A ∪ B) = P(A) + P(B) − P(A ∩ B). With P(A) = 0.5, P(B) = 0.4, P(A ∩ B) = 0.2 the naive sum gives 0.9 and the correct union is 0.7. Omitting inclusion-exclusion on three events requires subtracting all three pairwise intersections *and* adding back the triple intersection.

### 3. Confusing P(A|B) with P(B|A)
With 1% prevalence, 99% sensitivity, 95% specificity: P(disease | positive) = 0.0099/0.0594 ≈ 16.7%, not 99%. The 99% figure is P(+ | D); the conditioning event moves the denominator, not the numerator.

### 4. Ignoring the base rate when conditioning
The same confusion in reverse: reporting "the test is 99% accurate" alongside a 1% base rate hides that ~5 in 6 positives are false. Always split P(+) = P(+|D)P(D) + P(+|¬D)P(¬D) before dividing.

### 5. Treating dependent draws as independent
Drawing two aces without replacement: P = (4/52)(4/51) ≈ 0.0060, whereas the independent product (4/52)² ≈ 0.0059. Small gap for a deck, large gap for rare events (sampling 100 rare items without replacement vs with).

### 6. Confusing disjoint with independent
Mutually exclusive events with P(A) > 0 and P(B) > 0 are *never* independent: P(A ∩ B) = 0 ≠ P(A)P(B). Knowing the die showed a 3 tells you it did not show a 5 — maximally dependent, zero intersection.

### 7. Reading P(X = x) = 0 as "impossible"
For X ~ Uniform(0,1), P(X = 0.5) = 0 yet the event {X = 0.5} is possible and P(X ∈ [0.49, 0.51]) = 0.02. Probability zero excludes nothing; it only means the event is negligible under the measure (see Bertrand's paradox for what happens when the sampling scheme is left vague).

## How to catch yourself

- Write down Ω and the measure before computing any P; if you cannot, "equally likely" is doing hidden work.
- Check sums first: any set of probabilities that totals more than 1 means overlap was double-counted.
- Write the conditioning direction as a full sentence — "P(test | disease), not P(disease | test)" — before dividing.
- For a pair of events, test factorization numerically: is P(A ∩ B) − P(A)P(B) within sampling error of zero?
- For continuous claims, quote interval probability; P(X = x) = 0 never means the event is impossible.
- After conditioning, verify the new distribution still sums to 1 over the conditioning event's support.
