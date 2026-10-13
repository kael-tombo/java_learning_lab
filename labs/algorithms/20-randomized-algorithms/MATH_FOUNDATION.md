# Math Foundation: Expectation, Indicators, Amplification
> Linearity of expectation, quicksort indicators, Monte Carlo error shape and repetition.

## Definitions
- Indicator I_A: 1 if event A occurs else 0; E[I_A] = Pr(A).
- Linearity: E[X + Y] = E[X] + E[Y] with no independence needed.
- Las Vegas: random runtime, always correct. Monte Carlo: fixed time, error chance.
- Fixed seed: reproducible pseudorandom stream; analysis unchanged, testing deterministic.

## Counting argument
- Quicksort comparisons: pairs (i, j) compared iff one is first pivot between them.
- Probability 2/(j-i+1) for ranks i < j; sum over pairs gives Theta(n log n).
- Harmonic sum H_n ~ ln n appears: total ~ 2n ln n expected comparisons.
- Monte Carlo darts: n trials, hits binomial; standard error shape 1/sqrt(n).

## Recurrence
- Expected quicksort: E[T(n)] = (n-1) + average of E[T(k)] + E[T(n-1-k)] over pivots k.
- Solves to Theta(n log n) (standard substitution with harmonic numbers).
- Reservoir size-k: element i kept with probability k/i by induction on the stream.
- Amplification: majority over r runs; error decays exponentially (Chernoff-class).

## Derivation of the bound
- Indicator sum: E[total] = sum_{i<j} 2/(j-i+1) = 2 sum_{d} (n-d)/(d+1) ~ 2n ln n.
- Group by distance d: harmonic series per distance class gives the log factor.
- Monte Carlo: variance sigma^2/n gives 1/sqrt(n) deviations (Chebyshev-class).
- Repetition: error 1/3 per run becomes exponentially small in r via majority vote.

## Worked mini-proofs
- Proof 1: comparison probability 2/(j-i+1) from first-pivot-in-range argument. (4 lines)
- Proof 2: harmonic sum evaluation to 2n ln n order. (4 lines)
- Proof 3: seed fixing preserves the distribution argument while fixing the test. (2 lines)

## Exercises with answers
- 1. Expected comparisons order for n = 10^5. Answer: Theta(n log n), about 2n ln n.
- 2. Halving Monte Carlo error needs what sample multiple? Answer: 4x (1/sqrt shape).
- 3. Las Vegas or Monte Carlo: Fermat test? Answer: Monte Carlo (wrong answers possible).

## Pitfalls
- Needing independence for linearity (it holds regardless).
- Reporting one lucky run as the error rate.
- More Fermat bases as a fix for Carmichael numbers (coprime bases all pass).

## Checklist
- Derive quicksort expectation via indicators cold.
- Explain amplification math from a per-run error rate.
