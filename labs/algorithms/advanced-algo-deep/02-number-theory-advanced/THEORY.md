# Theory — Number Theory Advanced

Number theory supplies the modular arithmetic that cryptography, hashing, and combinatorics stand on. The core results are old; the engineering is in computing with them without overflow and in understanding what "probable prime" certifies.

## Euclid and the gcd

The key identity is `gcd(a, b) = gcd(b, a mod b)`. Proof: any common divisor of a and b divides `a - qb` where q = floor(a/b), and any common divisor of b and `a - qb` divides `qb + (a - qb) = a`. The two pairs have *identical* common-divisor sets, hence the same gcd. Each step replaces the larger argument by one strictly smaller than b, and after two steps the larger argument drops by at least half — so the loop runs in Θ(log min(a,b)) steps.

## Extended Euclid: Bézout coefficients

Tracking the quotients backwards (or carrying (x,y) through the recursion) yields integers s, t with `s·a + t·b = gcd(a,b)`. Those coefficients are exactly the modular inverse you need when `gcd(a, m) = 1`: `s·a ≡ 1 (mod m)`, so `a⁻¹ = s mod m`. Without extended Euclid, an inverse is one exponentiation too far; with it, it is one gcd.

## Fast modular exponentiation

To compute `aᵉ mod m` with a large e, write e in binary: `e = Σ eᵢ2ⁱ`. Then `aᵉ = Π a^(2ⁱ)^eᵢ`, and we get the squares by repeated squaring: `a^(2^(i+1)) = (a^(2ⁱ))²`. That is `Θ(log e)` squarings and at most `Θ(log e)` extra multiplies. Every multiplication is immediately reduced mod m, keeping values below m² — which is why a long is mandatory when m is near 10⁹.

## Euler's theorem and exponent reduction

Euler: if `gcd(a, m) = 1`, then `a^φ(m) ≡ 1 (mod m)`. Consequence: `aᵉ ≡ a^(e mod φ(m)) (mod m)`. For m prime, φ(m) = m-1 and this is Fermat's little theorem. This is how a 10¹⁰-bit exponent is folded to a workable one — *but only* when the base is coprime to the modulus. A common bug is reducing the exponent mod φ(m) unconditionally.

## Sieve of Eratosthenes

To enumerate primes up to n, mark multiples of each surviving unmarked p starting at p² (all smaller multiples were already marked by a smaller factor). Total work is `Σ_{p ≤ √n} n/p = n·log log n`, memory `Θ(n)`. The p² start and the log log bound are the two facts to keep.

## Chinese Remainder Theorem

Given congruences `x ≡ bᵢ (mod mᵢ)` with pairwise-coprime moduli, there is a unique solution mod `M = Π mᵢ`. Construct it as `x = Σ bᵢ·Mᵢ·(Mᵢ⁻¹ mod mᵢ)`, where `Mᵢ = M/mᵢ`. The inverse exists because `gcd(Mᵢ, mᵢ) = 1` by coprimality. CRT is how RSA combines prime-modulus results, and how hash collisions across moduli are avoided in practice.

## Primality: Miller–Rabin

For odd n write `n-1 = 2^s·d` with d odd. A witness base a passes if either `a^d ≡ 1` or `a^(2^r·d) ≡ -1` for some 0 ≤ r < s. Primes always pass (this follows from the structure of (Z/nZ)*); composites pass for at most 1/4 of bases. `k` random bases give error ≤ 4⁻ᵏ — each round is an independent filter. The cost is `Θ(k·log³ n)` with naive multiplication.

## Complexity at a glance

| Procedure | Time | Note |
|-----------|------|------|
| gcd | Θ(log min(a,b)) | Euclid |
| xgcd + Bézout | Θ(log min(a,b)) | one pass |
| modPow | Θ(log e) mults | reduce every step |
| inverse via Euler | Θ(log φ(m)) | needs gcd(a,m)=1 |
| sieve to n | Θ(n log log n) | Θ(n) bits |
| Miller–Rabin, k rounds | Θ(k·log³ n) | Monte Carlo |
| CRT combine, r moduli | Θ(r²) | pairwise xgcd |

## Pitfalls

- `%` on a negative numerator in Java returns a negative remainder — reduce with `(x % m + m) % m` when the mathematical result is needed.
- Exponent reduction mod φ(m) requires coprimality; applying it blindly to a shared factor gives a wrong answer.
- `long` overflow in `a*b % m` when both operands approach 10⁹; widen or use BigInteger.
- Miller–Rabin is Monte Carlo: a composite can pass all sampled bases with probability ≤ 4⁻ᵏ.
