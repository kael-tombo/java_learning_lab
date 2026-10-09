# Debugging: Generating Functions Code

## Symptom: Coefficient Arrays Are Off by One Power

If `a[0]` should hold [x⁰] but your loop fills `a[1]` first, every multiply/shift mismatches. Fixed discipline: store coefficients in an array where `coeff[i]` = [xⁱ] — never shift the array to "look like" polynomial evaluation order. After each operation, assert `coeff.length` and `coeff[0]` against a hand expansion: for 1/(1−x) the first three must be 1, 1, 1; for 1/(1−x)² they must be 1, 2, 3 (the triangular numbers).

## Symptom: Convolution Result Is Garbage

Series multiplication must compute `c[k] = Σ_{i=0..k} a[i] * b[k−i]` — index *sum* constant per term. Two classic bugs: using `b[i]` (element-wise product) and looping `j` from 0..n instead of 0..k (reads past b's meaningful range, folds in zeros *or* stale data if the array is reused). Test with tiny series: (1 + 2x)(1 + 3x) = 1 + 5x + 6x² — if you get (1, 6, 0) you multiplied element-wise (or read b[i] instead of b[k−i]); if the constant term is wrong, the k−i indexing never touched i = 0.

## Symptom: Coefficients Overflow `int`/`long`

Partition numbers grow fast: p(100) = 79,207,083,952 ≈ 7.9×10¹¹ (exceeds `int`), p(1000) ≈ 2.4×10³¹ (exceeds `long`; p(300) ≈ 9.4×10¹⁵ still fits). Catalan: C₃₅ ≈ 3.1×10¹⁸ fits in `long` (max 9.2×10¹⁸) but C₃₆ ≈ 1.2×10¹⁹ overflows, and C₅₀ ≈ 2.0×10²⁷ needs `BigInteger`. Symptom: negative or shrinking counts where the true sequence is strictly increasing.

Fix: `BigInteger` for all coefficient arithmetic in a series library, or checked arithmetic (`Math.addExact`) so overflow throws at the operation that caused it instead of returning a wrong coefficient three products later.

## Symptom: Recurrence-Based Extraction Disagrees With the Series

If aₙ = aₙ₋₁ + 2aₙ₋₂ gives 1, 1, 3, 5, 11… but your closed form 2ⁿ⁺¹ + (−1)ⁿ)/3 gives 1, 1, 3, 5, 11… — check by computing *both* for n = 0..5 and diffing. A mismatch at n = 0 usually means the closed form was derived for n ≥ 1 with a₀ filled in by hand; a mismatch later usually means a partial-fractions sign. Build a 6-term table and compare; never debug the algebra in the abstract.

## Symptom: Partial Fractions Give Nonsense Coefficients

Check the division-first rule: deg(numerator) must be < deg(denominator) before splitting. For (x³ + 1)/(1−x)², do polynomial division first: x³ + 1 = q(x)(1−x)² + r(x) with deg r < 2, then split r. Also verify by re-combining: put your partial fractions back over a common denominator and compare to the original — the recombination test catches sign errors in seconds.

## Symptom: Truncating to n Terms Changes Low-Order Coefficients

If multiplying series truncated at N changes coefficients below xᴺ, something reads beyond the array (loop bound `j <= n` instead of `j <= k`) or an untruncated term (like 1/(1−2x) with radius issues) leaked in. Invariant: in any ring of truncated series mod xᴺ⁺¹, low coefficients are stable under +, −, × — test by computing with N = 20 and N = 30 and comparing the first 20 entries (they must be identical).

## Symptom: Exponential GF Gives Factorial-Scaled Answers

Compare against known sequences: EGF for permutations is 1/(1−x) with coefficients n! → 1, 1, 2, 6, 24; ordinary GF 1/(1−x) gives 1, 1, 1, 1. If your "permutation count" returns 1, 1, 1, 1 you forgot you are extracting EGF coefficients (multiply by n! when reading out). Encode this as the library's single read-out function with a comment — one conversion point beats a scattered n! factor.
