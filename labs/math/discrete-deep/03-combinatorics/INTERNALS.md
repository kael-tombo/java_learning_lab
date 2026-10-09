# Internals: Combinatorics Data Structures

## Binomial Coefficient: Three Strategies and Their Footprints

1. **Pascal's triangle table** — `long[][] C = new long[n+1][n+1]`, fill by `C[i][j] = C[i−1][j−1] + C[i−1][j]`. Memory Θ(n²) (for n = 1000 that is ~10⁶ entries, ~8 MB as `long`), preprocessing Θ(n²) adds, then every query is O(1). Only valid where intermediate values fit the word size.
2. **Single-value multiplicative** — `result = result * (n − k + i) / i` for i = 1..k. Time O(k), memory O(1); exact as long as the division at step i is exact (it always is for the running product of binomials), intermediates stay ≤ the final C(n,k)·small factor.
3. **`BigInteger` product of factorials** — O(M(F)) where F ≈ n·log n bits; correct for any n but dominated by big-integer multiplication cost.

## Storing Large Counts

C(200, 100) ≈ 9.05×10⁵⁸ needs 197 bits — no primitive fits. The bit length of C(2n, n) is ≈ 2n·log₁₀2·log₂10 ≈ Θ(n) bits (Stirling: log₂ C(2n,n) ≈ 2n − ½log₂(πn)), so memory for the exact count grows linearly in n while arithmetic cost grows super-linearly (schoolbook O(d²) on d-digit numbers).

## Enumerating k-Subsets: The Next-Combination Jump

Represent a combination as a strictly increasing tuple i₁ < … < iₖ in [0, n). "Next" finds the rightmost index that can be incremented (i_j < n − k + j), increments it, and resets everything right of it to consecutive values. Each jump is O(k) worst case (amortized O(1) for the common case), total enumeration Θ(C(n,k) · k), no recursion stack, no visited set — the standard "combinations in lexicographic order" loop in competitive-programming libraries.

## Permutation Generation

- **Heap's algorithm**: n! permutations, O(1) swaps between consecutive outputs (no comparison, no visited array) — the internal-work benchmark for permutation output.
- **Lexicographic next_permutation** (as in `java.util.Arrays` / C++ `std::next_permutation`): each call O(n), terminates after the sorted-descending sequence; produces n! outputs and visits every permutation exactly once.
- Backtracking with `used[]`: memory O(n) for the path plus O(n) for flags — simpler, but it is O(n!) *stack* work and duplicates nothing only if flags are set correctly.

## Enumerating Subsets by Mask

`for (int m = 0; m < (1 << n); m++)` yields all 2ⁿ subsets, each expanded in O(n) (or O(popcount)). Memory O(1) besides output. This is the workhorse for inclusion–exclusion over ≤ 20–25 properties: 2²⁰ = 1,048,576 masks, each contributing an intersection-size computation — the exponential is in the mask count, which is why n ≤ ~20 is the practical ceiling.

## Stars and Bars Encoding

A composition of n into k nonnegative parts is a binary string of n stars and k−1 bars: C(n+k−1, k−1) such strings. Internally, encode one outcome as a `k`-element array of counts (Θ(k) memory) or as a bitmask of positions (Θ(n+k) bits). Iterating them with a next-combination jump over bar positions gives each distribution in O(k).

## Memoization Layout

Recurrences like aₙ = aₙ₋₁ + 2aₙ₋₂ or the derangement !n = (n−1)(!(n−1) + !(n−2)) need only the two most recent values for a single term: O(1) memory, O(n) time iteratively (a growing memo only pays off when all terms are requested or the recurrence's state space is genuinely multidimensional, e.g., DP over (i, j) pairs). Storing full history when only the last two values are read wastes Θ(n) memory for no query benefit.
