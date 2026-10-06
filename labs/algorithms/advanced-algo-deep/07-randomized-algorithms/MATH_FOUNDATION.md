# Math Foundation — Randomized Algorithms

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Randomised quicksort expectation

For any pair (xᵢ, xⱼ) in sorted order, they are compared iff one is the first pivot chosen from {xᵢ,…,xⱼ}, probability 2/(j-i+1). By linearity of expectation, E[comparisons] = Σ_{i<j} 2/(j-i+1) ≤ 2n·H_n = Θ(n log n).

No independence is needed — linearity of expectation suffices.

## Randomised recurrence for quicksort

E[T(n)] = Θ(n) + (1/n)Σ_{k} (E[T(k)] + E[T(n-1-k)]) = Θ(n) + (2/n)Σ_{k} E[T(k)]. Guessing E[T(n)] ≤ c·n log n and substituting gives a valid bound.

The recurrence and the pairing argument agree on Θ(n log n).

## Quickselect expectation

For a random pivot, the larger retained side has at most 3n/4 elements with probability ≥ 1/2. Hence E[T(n)] ≤ Θ(n) + E[T(3n/4)] = Θ(n).

The sum Θ(n) + Θ(3n/4) + Θ(9n/16) + … is geometric: Θ(n).

## Monte Carlo error amplification

If one round errs with probability ≤ δ, k independent rounds err with probability ≤ δᵏ. For Miller–Rabin δ ≤ 1/4, so k rounds give ≤ 4⁻ᵏ.

Repetition multiplies success only when the rounds are independent — reuse of the same witness does not boost.

## Reservoir sampling correctness

By induction on i: after step i the reservoir is a uniform k-subset of the first i items. Step i+1 inserts the (i+1)-th item with probability k/(i+1) and, if inserted, evicts uniformly — preserving uniformity.

The telescoping product Π_{i=k+1}^{n} k/i · (i-k)/(i-1) … simplifies to k/n per element.
