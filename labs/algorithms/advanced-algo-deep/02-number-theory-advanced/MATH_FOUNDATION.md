# Math Foundation — Number Theory Advanced

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Euclid correctness

d | a and d | b ⟺ d | (a - qb) and d | b, so the two pairs share all common divisors.

Apply recursively: gcd(a,b) = gcd(b, a mod b) = … = gcd(g,0) = g. The recursion strictly decreases the second argument, so it terminates.

## Euclid termination bound

If Euclid took 2t steps then a ≥ F_{2t+2}; since F_n ≥ φ^(n-2), t ≤ log_φ(a) + O(1).

The bound is tight exactly on consecutive Fibonacci inputs — Euclid is slowest there.

## Square-and-multiply correctness

Maintain acc·a^e₀ ≡ a^e (mod m) where e₀ is the remaining exponent. Halving e₀ by squaring a preserves the invariant; the bit decides whether one more a-factor is included.

After log₂ e iterations e₀ = 0 and acc ≡ a^e. Every multiply stays < m², so no intermediate exceeds the word size.

## Euler via Lagrange

(Z/mZ)* is a group of order φ(m). For any a in it, a^φ(m) = a^|G| = e = 1 by Lagrange's theorem.

Counter-example when gcd(a,m) > 1: 2^φ(6) = 2² = 4 ≢ 1 (mod 6) — the hypothesis is essential.

## Miller–Rabin soundness (sketch)

If n is an odd composite and a is not a strong liar, the sequence a^d, a^(2d), …, a^(n-1) cannot reach 1 without some earlier term being a nontrivial square root of 1, which Z/nZ admits only for composite n.

A prime n has only ±1 as square roots of 1, so every prime always passes — the test never rejects a prime.

## CRT construction

Let x = Σ bᵢ Mᵢ yᵢ with Mᵢ = M/mᵢ and yᵢ ≡ Mᵢ⁻¹ (mod mᵢ). Modulo mⱼ every term except the j-th is 0, and the j-th is bⱼ·Mⱼ·yⱼ ≡ bⱼ·1 (mod mⱼ).

Pairwise coprimality makes each Mᵢ invertible mod mᵢ; without it either no solution or non-uniqueness.
