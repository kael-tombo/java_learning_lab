# Vision: Randomized Algorithms
> Randomness as a tool: expectation, fixed seeds, and honest error bounds.

## Where this leads
- Random pivots, sampling, sketching introductions, and Monte Carlo estimation.
- Las Vegas vs Monte Carlo thinking applied to every randomized proposal.
- Seed discipline: reproducible tests for irreproducible-looking methods.
## What mastering it unlocks
- Separate Las Vegas (random time, exact answer) from Monte Carlo (fixed time, error chance).
- Analyze randomized quicksort expectation via comparison indicators.
- Estimate by sampling with the 1/sqrt(n) error shape stated and used.
- Amplify a Monte Carlo success rate by repetition with the math shown.
- Catch pseudoprime blind spots and explain why repetition alone cannot fix Carmichael cases.
## What it does not cover
- Derandomization theory and pseudorandom generator constructions.
- Measure-theoretic probability and martingale machinery.
- Cryptographic randomness requirements and entropy sourcing.
## Core questions you will answer
- Why does a fixed seed keep testing deterministic while analysis stays randomized?
- How does linearity of expectation simplify the quicksort analysis?
- How many repetitions drive error below a stated bound, and by which inequality?
- Why do Carmichael numbers survive Fermat repetition at coprime bases?
## How to judge progress
- Classify any randomized algorithm as Las Vegas or Monte Carlo with reasons.
- Compute an expectation via indicators on a new example.
- Size a repetition count from an error target without guessing.
## Common misuse
- Reporting one lucky Monte Carlo run as the method's accuracy.
- Believing more Fermat bases always suffice against Carmichael numbers.
## After this lab
- 19-number-theory for the modular arithmetic underneath primality tests.
- 14-approximation-algorithms for the other way to cope with hard problems.
One-line self-test: Explain the Las Vegas vs Monte Carlo split using quicksort and pi estimation.
