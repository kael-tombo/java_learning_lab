# Debugging: Combinatorics Code

## Off-by-One in Recurrence Seeds

Symptom: `catalan(4)` returns 14 in a reference and 42 (or 0) in yours. Check the seeds: C[0] = 1, and the loop must run `for (int i = 0; i <= n; i++) split into (i, n−1−i)` including both ends — skipping i = 0 or i = n−1 drops exactly half the decompositions. For Fibonacci-style recurrences verify `a[0]` and `a[1]` are both set before the loop reaches n = 2.

Debug tactic: hand-compute the first 5 terms (Catalan: 1, 1, 2, 5, 14) and assert them as a unit test. A wrong seed corrupts every later term, so test the small end, not n = 30.

## Silent Integer Overflow

`C(67, 33)` exceeds 2⁶³ − 1 (C(66,33) ≈ 7.2×10¹⁸ < 9.2×10¹⁸ < C(67,33) ≈ 1.4×10¹⁹), so `long` silently wraps above n ≈ 66. Symptoms: negative binomials, non-monotone rows of Pascal's triangle, Catalan values that stop growing.

Fixes:

1. Detect rather than crash: use `Math.multiplyExact` / `Math.addExact` to convert silent wrap into an `ArithmeticException`.
2. Or compute exactly with `BigInteger`.
3. Or restructure to avoid intermediate growth: multiplicative `C(n,k) = Π (n−k+i)/i` divides at every step and keeps intermediates near the final value.

Assertion worth having: Pascal's identity `C(n,k) == C(n−1,k−1) + C(n−1,k)` for all n ≤ 66 — overflow breaks it immediately.

## Duplicate Enumerations

Generating permutations by naive recursion without a `used[]` flag yields nⁿ results (repeats included) instead of n!. Generating combinations by choosing index i twice yields duplicates. Fixes: mark used positions, or generate combinations as strictly increasing index tuples `(i₁ < i₂ < … < iₖ)` advancing via next-combination — then count must equal C(n, k) exactly. Assert `list.size() == nChooseK(n,k)` on every test; a size mismatch *is* the bug report.

## Inclusion–Exclusion Loop Bounds

For n properties the subset loop runs `mask` from 1 to (1 << n) − 1 (skip the empty set: it contributes nothing and its size n = 0 makes parity-based signs wrong). Sign is `popcount(mask)` odd → +, even → −. Common bug: using `mask % 2` instead of popcount — correct only when the loop processes bits in a specific order, wrong in general.

Self-check: with n = 3 all-nonempty and no overlaps, Σ = |A|+|B|+|C| must equal the count of elements having ≥ 1 property when properties are disjoint.

## Wrong Denominator in Probability Counts

Symptom: probabilities > 1.0. Usual cause: numerator counts *ordered* tuples while denominator counts *unordered* (or vice versa). Rule: pick one convention and use it on both sides. If outcomes are equally likely sequences, count sequences everywhere; if you divide by n! on top you must divide on the bottom too.

## Float Accumulation in Expectation Sums

Summing 1/C(n,k) terms as doubles loses precision past ~10¹⁵ in the numerator scale. For exact answers keep rationals (`BigInteger` numerator/denominator) until the final step; convert once.

## Brute-Force Oracle for Small n

For n ≤ 10, generate everything explicitly (recursively enumerate all k-subsets / all permutations), count with a `HashSet`, and compare to the closed form. This oracle founds your confidence: any formula you trust at n = 10 failing at n = 40 usually means overflow, not mathematics.
