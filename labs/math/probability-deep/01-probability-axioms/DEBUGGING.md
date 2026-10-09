# Debugging: Probability Axioms Implementation

### Symptom: probabilities sum to 1.0000000002 after normalization
Cells were rounded individually before dividing. Normalize *after* summation: sum once, divide every cell by that one sum, and assert `|Σp − 1| < 1e-12`.

### Symptom: NaN from a conditional probability
P(A|B) computed as 0/0 when B was never assigned mass — conditioning on an event the model treats as impossible. Guard: if P(B) < epsilon, either return an unconditional value or report "conditioning event has zero probability" instead of silently returning NaN.

### Symptom: enumerated space has 21 outcomes for two dice
Ordered pairs number 36 (6 × 6); treating {(i,j)} as unordered gives 21 outcomes with *unequal* probabilities, so P(sum = 7) comes out 1/6 instead of the correct 6/36. If you enumerate unordered outcomes, weight each by its multiplicity.

### Symptom: simulation disagrees with the analytic answer
For Monty Hall the switch strategy converges to 2/3, not 1/2. Usual causes: reusing the same seed across strategies, shuffling in place so the car position is no longer uniform, or stopping early (check the SE bound 1/(2√N)).

### Symptom: 0.1 + 0.2 != 0.3 in a probability assertion
Binary floating point cannot represent 0.1. Assert with a tolerance (1e-12) or compute the cell exactly with `BigInteger` numerator/denominator and compare rationals.

### Symptom: independent events still show correlation in samples
Independence is a statement about the joint *model*, not about small samples: n = 100 draws estimate a correlation with standard error ≈ 1/√n = 0.1. Increase n before suspecting the model — or check that the RNG is not an LCG sampled in a correlated pattern.

### Symptom: union probability exceeds 1
Overlapping events were added. Walk the partition: {A ∩ B, A ∩ ¬B, ¬A ∩ B, ¬A ∩ ¬B} must be disjoint and sum to 1; a sum > 1 somewhere localizes the overlap.

## Triage order when a probability looks wrong

1. Recompute Σp over the whole space — must be 1 to 1e-12. If it is off, the bug is upstream of the query.
2. Check the support: two dice give 36 ordered cells, not 21; support errors corrupt every downstream ratio.
3. Recompute one conditional by hand from the joint table. Table right + conditional wrong ⇒ wrong denominator.
4. Re-evaluate the same quantity with exact BigInteger rationals; divergence beyond 1e-12 means rounding (sum) or cancellation (ratio).
5. Only then suspect the sampler: RNG seed, independence of draws, and N ≥ 1/SE² trials for the precision you claimed.
