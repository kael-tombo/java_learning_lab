# Common Mistakes: Generating Functions

## 1. Using an Ordinary GF Where an Exponential GF Belongs

Count labeled structures (graphs on labeled vertices, permutations, mappings) with EGFs A(x) = Σ aₙ xⁿ/n!; count unlabelled/sequence-shaped objects (partitions, binary strings, compositions) with ordinary GFs. Mixing them off by the n! factor: the EGF of "set partitions into blocks" is exp(eˣ − 1), whose coefficients times n! give the Bell numbers — if you read the series as an ordinary GF you get aₙ = Bₙ/n! instead of Bₙ. Symptom: answers that are right up to factorial factors.

## 2. Wrong Exponents: Convolutions Need Index Arithmetic

If A(x) = Σ aₙxⁿ and B(x) = Σ bₙxⁿ then (AB)ₙ = Σ_{i+j=n} aᵢbⱼ — coefficient of xⁿ multiplies indices that *sum to n*. Students routinely write Σ aᵢbᵢ (diagonal products), which is the Hadamard product, not convolution. The rule "multiply series → indices add; divide by (1−x) → cumulative sum" is the whole mechanical skill.

## 3. Applying 1/(1−x) = Σ xⁿ Outside |x| < 1 (or Forgetting Formality)

As *formal* power series, 1/(1−x) = Σ_{n≥0} xⁿ is an identity with no convergence requirement — the answer is a symbol. As *functions*, it holds only for |x| < 1, and evaluating at x = 1 or x = 2 silently gives ∞ or nonsense. Decide which layer you are in: coefficient extraction is always formal; plugging in numbers for closed forms needs an actual radius of convergence.

## 4. Off-by-One in Index Shifts

xᵏA(x) shifts *up*: [xⁿ] xᵏA = aₙ₋ₖ. And (A(x) − a₀ − … − a_{k−1}x^{k−1})/xᵏ shifts down. The error is inverting them: "multiply by x to drop the first term" is backwards. When a recurrence seeds a₀, a₁ and you multiply by x², the coefficient of x² is a₀ — verify with a small case before trusting the algebra.

## 5. Wrong Decomposition in Partial Fractions

For A(x) = (2x)/(1−x)(1−2x), write A = A/(1−x) + B/(1−2x) with 2x = A(1−2x) + B(1−x): x = 0 → 0 = A + B... solving properly: A + B = 0 (constant 0) and −2A − B = 2 (coefficient of x) → A = −2, B = 2, so aₙ = −2 + 2·2ⁿ = 2^{n+1} − 2. The frequent slip is forgetting the *numerator's degree* must be less than the denominator's degree before splitting — do polynomial long division first if deg(num) ≥ deg(den).

## 6. Conflating "Coefficient of xⁿ" With "Sum of Coefficients"

The count you want is usually [xⁿ]A(x). The *total* of all aₙ for n ≤ N is A evaluated at x = 1 (if that converges). Evaluating at 1 to get a single coefficient is a category error that shows up as absurd magnitudes.

## 7. Ignoring Label Bookkeeping: exp vs 1/(1−B)

For structures built from labeled components: a *set* of components gives EGF exp(B(x)) (order irrelevant, partitions into blocks, forests as sets of trees), while a *sequence* of components gives 1/(1 − B(x)) (order matters — words, compositions). Choosing the wrong one swaps Bell numbers for words-at-a-glance errors. Symptom: your answer matches a known sequence only after dividing by n! (or only after multiplying).

## 8. Series Solutions Without Checking Initial Terms

After deriving aₙ from a GF, always expand the first three terms of the series by hand and compare to the recurrence's first three computed values (e.g., Catalan: 1, 1, 2). A one-power or one-factor error (forgetting the (1−x) denominator factor) shows immediately at n = 0 or 1 and saves an hour of algebra.
