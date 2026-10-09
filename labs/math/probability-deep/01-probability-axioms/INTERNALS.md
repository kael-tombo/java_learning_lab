# Internals: Probability Axioms Implementation

## Finite sample spaces as bitsets
For |Ω| ≤ 64, an event is a `long`: union = `a | b`, intersection = `a & b`, complement = `~a & universeMask`. Probability of an event is the sum of the cell weights at the set bits — popcount-style accumulation, no allocation. Ω itself is stored as a mask so complement never leaks bits outside the sample space.

## Weights live outside the events
The measure is a `double[] weights` indexed by outcome id; events reference ids, never probabilities. This separation means conditioning rewrites *weights*, not structure: P(·|B) = weights[i] / P(B) for i ∈ B, 0 otherwise — one precomputed divisor, one pass.

## Exact arithmetic path
Rational probabilities are held as `BigInteger numerator/denominator` with gcd reduction after every operation. Adding 1/36 + 1/36 multiplies denominators only when coprime, so dice/card computations stay small; cross-multiplication is done before comparison to avoid floating drift entirely. The exact path is the reference oracle for the double path.

## One-pass conditioning
Never compute P(A ∩ B) by building the intersection and then the marginal separately (two passes). Accumulate `num = Σ_{i∈A∩B} w[i]` and `den = Σ_{i∈B} w[i]` in a single sweep and divide once — division is the only rounding-heavy step, and it happens exactly once.

## Product rule without constructing joints
P(A ∩ B) = P(A)·P(B|A) needs only the marginal and the conditional, so a model can be evaluated without materializing the 2 × 2 joint table. The joint is reconstructed for display: four cells from three independent numbers plus the Ω = 1 constraint.

## Monte Carlo path
A uniform `double u` maps to an outcome by inverse CDF over the cumulative weights (binary search over the prefix sums). The estimator only needs a counter — successes and trials — so sampling is O(1) memory regardless of run length.

## Layering
`bitsets → measure → conditioning → bayes → montecarlo`. Each layer adds one concept and depends only downward; exact rationals run parallel to doubles behind the same measure interface so tests can compare both.

## Complexity per operation

- Event union/intersection on ≤ 64 outcomes: one machine instruction (OR/AND), probability lookup O(popcount).
- Conditioning: one pass for the denominator, one pass to divide — O(|Ω|), zero allocation.
- Exact addition of k/n and p/q: one gcd plus one BigInteger multiplication; unit-fraction cell weights (1/36, 1/52) keep denominators small.
- Sampling: prefix-sum table built once O(|Ω|), then O(log|Ω|) per draw.

## Failure modes this layer owns

- A missing universe mask turns `~event` into silent garbage — asserted at construction by masking against Ω.
- Renormalization after dropping cells must happen *before* conditioning, or the posterior inherits a sub-probability measure and every ratio is inflated.
- Cached conditionals must be keyed by event id, never by a double-valued conditioning weight (two weights within 1e-15 are the same event for all practical purposes — and different keys).
