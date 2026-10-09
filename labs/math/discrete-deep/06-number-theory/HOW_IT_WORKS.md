# How It Works: Number Theory Mechanics

## 1. Why the Euclidean Algorithm Works

If a = q·b + r, then any divisor of (a, b) divides r = a − q·b, and vice versa — so gcd(a, b) = gcd(b, r). Replacing (a, b) with (b, a mod b) preserves the gcd while strictly shrinking the second entry; when the remainder hits 0, the last nonzero remainder divides both originals and is therefore the gcd. Steps are logarithmic because remainders shrink at least as fast as consecutive Fibonacci numbers (the worst case, where each quotient is exactly 1).

## 2. Why the Inverse Exists (Extended Euclid)

Euclid's steps run backwards to express gcd(a, m) as s·a + t·m (Bézout). If gcd = 1: s·a ≡ 1 (mod m), so s (reduced into [0, m)) is a⁻¹. If gcd = d > 1: s·a + t·m = d, so every combination of a and m is a multiple of d — 1 is unreachable, no inverse exists. The algorithm *proves* existence by constructing it; nothing separate is needed.

## 3. Fermat's Little Theorem From Permutations

For prime p, multiplication by a (∤p) maps {1,…,p−1} into itself: if a·x ≡ a·y then p | a(x−y), and since p ∤ a, p | (x−y) — so the map is injective on a finite set, hence a permutation. The product of all elements is unchanged by permuting: (p−1)! ≡ a^(p−1)·(p−1)!. Cancel (p−1)! (it is not divisible by p, hence invertible): **a^(p−1) ≡ 1 (mod p)**. The map's *cycle structure* is what powers modPow; the order of a divides p−1 by Lagrange's theorem on the multiplicative group.

## 4. Euler's Theorem as the Same Statement on the Unit Group

Z/nZ's units (residues coprime to n) form a group of order φ(n). Lagrange: every element's order divides the group order, so a^φ(n) ≡ 1. The multiplicative arithmetic for φ: for prime powers φ(p^k) = p^k − p^{k−1} = p^k(1 − 1/p), and for coprime m, n: φ(mn) = φ(m)φ(n) (CRT: the coprimality makes the residue pairs independent) — giving φ(12) = φ(4)φ(3) = 2·2 = 4.

## 5. Square-and-Multiply: Exponentiation in O(log e)

Write e in binary: e = Σ bits. Maintain `result = 1`, `base = a`; for each bit of e (LSB→MSB): square `base` mod m; if the bit is set, multiply it into `result`. For e = 123 = 1111011₂: squarings at every step (7 for a 7-bit exponent), multiplications at the 4 set bits. Total: O(log e) modular multiplications instead of e multiplications — 10⁹ exponent → ~1500 operations instead of 10⁹. This is exactly method B in STEP_BY_STEP, mechanically applied.

## 6. Miller–Rabin: What Fermat Misses

Write n−1 = 2^s·d. For base a compute the sequence x₀ = a^d, x_{i+1} = xᵢ² (mod n). If a prime, the sequence can only reach 1 by first passing through −1 (since x² ≡ 1 mod prime implies x ≡ ±1, and the only square roots of 1 in a prime field are ±1). So: if some xᵢ ≡ −1, n is *probably* prime; if the sequence reaches 1 without ever hitting −1, n is *definitely* composite (a nontrivial square root of 1 — which exists only for composites). 561 fails at 2³⁵ = 263 → 166 → 67 → 1 with no −1: composite. Each random base is a 4-sided coin landing on a witness with probability ≥ 3/4, so k rounds err with probability ≤ 4^(−k).

## 7. CRT: Constructive Isomorphism

Given pairwise-coprime m₁…mₖ and residues aᵢ: set M = Πmᵢ, Nᵢ = M/mᵢ. Since Nᵢ ≡ 1 (mod mᵢ) and Nᵢ ≡ 0 (mod mⱼ) for j ≠ i, multiplying Nᵢ by the inverse of Nᵢ mod mᵢ isolates aᵢ's contribution. x = Σ aᵢ·Nᵢ·(Nᵢ⁻¹ mod mᵢ) satisfies x ≡ aᵢ (mod mᵢ) for each i (only its own term survives modulo mᵢ), and x is unique mod M. The "why" is the isomorphism Z/MZ ≅ Π Z/mᵢZ — one coordinate per modulus, which is why decryption mod p and mod q can be done separately in CRT-RSA.

## 8. The Shape of Every Proof in This Lab

Notice the recurring pattern: exhibit a *bijection* or an *invariant* (Euclid's gcd preservation; multiplication-permutation for Fermat; term-wise cancellation for inclusion-style sums; the residual-network certificate for flow-like arguments), then let finiteness finish the job. The machinery is small; the discipline is checking each hypothesis (prime? coprime? pairwise coprime?) before applying it.
