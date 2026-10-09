# Performance: Combinatorics Algorithms

## Binomial Coefficient: Closed Form vs DP (Precise Costs)

| Method | Time | Memory | Best when |
|---|---|---|---|
| Multiplicative C(n,k), k ≤ n/2 | O(k) multiplications | O(1) | single query |
| Pascal table build to n | Θ(n²) additions | Θ(n²) storage | many queries over n ≤ a few thousand |
| Pascal row-by-row (1D) | O(n) per row, Θ(n²) total | Θ(n) | streaming rows |
| Stirling/binomial via `BigInteger` | O(k · M(d)) on d-bit numbers | O(d) | exact values beyond 64 bits |

A single C(10⁶, 5) is O(5) work multiplicatively; building Pascal's table that large would be Θ(10¹²) additions and 10¹² entries of memory — infeasible. Rule: *one query → O(k) formula; many queries → O(n²) precompute then O(1) per query*. Neither is ever O(1) from scratch.

## Catalan Numbers: Binomial vs DP

Closed form Cₙ = C(2n, n)/(n+1) via one binomial: O(n) multiplications, O(1) memory (exact arithmetic O(n·M(d)) with big integers, since Cₙ has Θ(n) bits). The DP Cₙ = Σᵢ₌₀ⁿ⁻¹ CᵢCₙ₋₁₋ᵢ costs Θ(n²) additions — 10,000× more arithmetic at n = 10⁵ than the binomial's ~10⁵ operations. Use the DP only when Cₙ exceeds what you can store or when you need all intermediate Catalan values anyway. For n ≤ 20 the DP is fine either way; the asymptotic point is that the closed form is asymptotically superior: Θ(n) vs Θ(n²).

## Enumerating Is Exponentially Harder Than Counting

- Counting subsets: O(n) (just the number 2ⁿ). Listing them: Ω(2ⁿ) — output-bound.
- Counting permutations: O(1) (n!). Listing: Ω(n!) — Heap's algorithm does Θ(n!) swaps, and no algorithm can beat the output size.
- Practical ceilings: 2²⁰ ≈ 10⁶ subsets listable in ms; 10! = 3.6×10⁶ permutations listable; 20! ≈ 2.4×10¹⁸ permutations — impossible to list, trivial to count. `long` overflows at 20! > 9.2×10¹⁸, so factorial results beyond 20 need `BigInteger`.

This is the lab's core performance lesson: **counting is polynomial, enumeration is super-polynomial**, and conflating the two is both an algorithmic and a mathematical error.

## Inclusion–Exclusion Cost

n properties → 2ⁿ − 1 masks, each computing an intersection size. If intersection sizes are precomputed from a frequency count over masks (SOS-style), the table build is Θ(n·2ⁿ) bitwise operations (sum over subsets DP); naively scanning data per mask is Θ(|data|·2ⁿ). Practical n ≤ 20–25. Faster to use the complement product only when the properties are independent — then it is Θ(n) instead of Θ(2ⁿ).

## Memoized Recurrences

Linear recurrences with constant coefficients (Fibonacci, aₙ = aₙ₋₁ + 2aₙ₋₂): iterative loop Θ(n) time, O(1) memory; naive recursion is Θ(φⁿ) — exponential in n for the same answer. If you need terms at huge indices, fast doubling (matrix exponentiation) gives the n-th term in O(M(log n)) time — versus Θ(n) for the loop — worth it only beyond ~10⁷.

## DP Beats Closed Form? The Real Trade-Off

- DP wins when the closed form is a *sum over exponentially many cases* (e.g., counting paths with obstacles: no product formula, but Θ(n·m) DP).
- Closed form wins when it compresses the sum (Catalan, derangements !n = round(n!/e), binomials).
- DP loses when it materializes a table you never query: cache only states the recurrence actually reaches.
