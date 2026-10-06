# Quiz — Number Theory Advanced

15 questions. Each key gives the reason.

---

## Q1
Prove gcd(a,b)=gcd(b, a mod b) in two inclusion arguments.

<details><summary>Answer</summary>

Any d dividing a and b divides a-qb = a mod b. Any d dividing b and a mod b divides qb+(a mod b)=a. Same divisor set ⇒ same gcd.

</details>

## Q2
Why does Euclid terminate in Θ(log min(a,b))?

<details><summary>Answer</summary>

Within two steps the larger argument drops below half: a mod b < b, and by the worst case of consecutive Fibonacci numbers the ratio is ≥ φ² each two steps.

</details>

## Q3
What does extended Euclid give that Euclid does not?

<details><summary>Answer</summary>

Bézout coefficients s,t with sa+tb=gcd(a,b); those yield the modular inverse when gcd=1.

</details>

## Q4
Why reduce every intermediate in modPow?

<details><summary>Answer</summary>

Keeps values < m, so a multiply is a single word square; otherwise the exact power has Θ(e) bits.

</details>

## Q5
State Fermat's little theorem and its use in exponent reduction.

<details><summary>Answer</summary>

a^(p-1) ≡ 1 (mod p) for prime p and p∤a; hence a^e ≡ a^(e mod (p-1)).

</details>

## Q6
When does exponent reduction mod φ(m) NOT apply?

<details><summary>Answer</summary>

When gcd(a,m) > 1; e.g. reducing 4^x mod 6 by φ(6)=2 fails.

</details>

## Q7
In the sieve, why start crossing off at p²?

<details><summary>Answer</summary>

Every composite with a factor p and a smaller cofactor was already crossed off by the smaller cofactor; the smallest unclaimed multiple is p·p.

</details>

## Q8
Why is Miller–Rabin probabilistic?

<details><summary>Answer</summary>

A base can be a liar for composite n; each round rejects composites with probability ≥ 3/4, so error ≤ 4⁻ᵏ.

</details>

## Q9
Why must Miller–Rabin first check small prime factors?

<details><summary>Answer</summary>

The 2^s·d decomposition assumes an odd n; composites with small factors would otherwise produce misleading passes, so sieve them out first.

</details>

## Q10
Give the CRT construction formula.

<details><summary>Answer</summary>

x = Σ bᵢ Mᵢ yᵢ mod M, with M = Πmᵢ, Mᵢ = M/mᵢ, yᵢ = Mᵢ⁻¹ mod mᵢ.

</details>

## Q11
What coprimality is needed for CRT?

<details><summary>Answer</summary>

Pairwise-coprime moduli; if two moduli share a factor g then consistency requires bᵢ ≡ bⱼ (mod g).

</details>

## Q12
Compute -7 mod 12.

<details><summary>Answer</summary>

((-7 % 12) + 12) % 12 = 5; Java gives -7 directly, which is the trap.

</details>

## Q13
Why is long insufficient for a*b % m when a,b ≈ 10⁹?

<details><summary>Answer</summary>

a·b ≈ 10¹⁸ fits, but doubling to ≈10⁹.⁵ overflows long; use BigInteger or split the multiplication.

</details>

## Q14
What does Euler's totient φ(n) count?

<details><summary>Answer</summary>

The integers in [1,n] coprime to n; the order of (Z/nZ)*.

</details>

## Q15
Why does a^φ(m) ≡ 1 mod m when gcd(a,m)=1?

<details><summary>Answer</summary>

Because a is a unit in (Z/mZ)*, a group of order φ(m), and by Lagrange a^|G| = 1.

</details>
