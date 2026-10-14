# VISION — Matrix Algorithms
> Direction: from triple loops to thinking in exponents, tiles, and memory traffic.

## Where this sits
- Dense multiplication spans naive O(n^3), Strassen O(n^2.81), and near-optimal research exponents; production runs blocked O(n^3) because constants and cache behavior dominate.
- Matrix powers connect to recurrences (Fibonacci), graph path counts, and Markov steps via exponentiation by squaring.
- The same tiling ideas recur in convolution, attention, and scientific codes.

## 4-week direction
- Week 1: hand-multiply the lab 3x3 pair; reproduce all three rows without code.
- Week 2: finish MINI_PROJECT; measure the transpose effect at n = 512 yourself.
- Week 3: work the Strassen recombination formulas until each of the 7 products is justified.
- Week 4: REAL_WORLD_PROJECT review; whiteboard the cutover reasoning in 10 minutes.

## Done criteria
- Derive F(n) from M^n on demand and compute fib20 = 6765 by powering.
- Explain the Strassen exponent log2 7 from the 7-multiplication recurrence.
- Predict whether transpose-then-multiply helps for a given size, then verify.

## Non-coverage
- This lab does not cover sparse formats, iterative eigensolvers, or distributed (Cannon/SUMMA) multiplication.
- No claim that a better exponent is always faster in practice; crossover analysis is mandatory.
- Numerical stability of fast algorithms is named but not derived here.

## Pitfalls
- Benchmarking without warmup and reporting noise as signal.
- Assuming Strassen wins at textbook sizes; measure the crossover on your hardware.
- Ignoring remainder tiles when n is not a multiple of the tile size.

## Adjacent labs
- Pair with 29-fft for the transform side of fast algorithms and 25-optimization-algorithms for the trainer that consumes Gram matrices.
- Revisit when a multiply job gets slow; the tile/transpose checklist transfers to any dense kernel.

## Weekly drills
- Recompute one row of the lab 3x3 product by hand in under 3 minutes.
- Recombine the 7 Strassen products into C11..C22 from the formulas without peeking.
- State the exponent log2 7 ~= 2.81 and the two overheads that delay the crossover.

## Anti-roadmap
- Do not adopt a fast algorithm on exponent alone; crossover first, deploy second.
- Do not benchmark without warmup, median-of-runs, and machine/JDK labels.
