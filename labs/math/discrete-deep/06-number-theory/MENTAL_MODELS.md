# Mental Models: Number Theory

## 1. Modulo Is a Clock, Then It's a Partition

Start with the clock: 13 o'clock on a 12-hour face is 1. The deeper picture: "mod m" cuts the integers into m **equivalence classes** {…, r−m, r, r+m, r+2m, …} — one class per remainder. Arithmetic mod m is arithmetic on these classes, where every integer has exactly one representative in [0, m). When a computation "mod 7" returns −1 or 13, you've handed back the wrong representative of the right class — the class is correct, the canonical form is not.

## 2. The Modular Inverse Is Division by Rewriting the Question

x = a⁻¹ mod m means you're not dividing — you're asking "which remainder, when multiplied by a, lands on 1?" Since multiplication by a permutes the residue classes exactly when gcd(a, m) = 1, such an x exists iff a is *invertible* in that ring; if gcd(a, m) = d > 1, a's multiples only hit the multiples of d, and 1 is not among them. The mental check: "does a share a factor with m?" precedes any attempt to invert.

## 3. Primes Are the Atoms — and Unique Factorization Is a Fingerprint

Every n > 1 factors uniquely as p₁^{e₁}···pₖ^{eₖ}: a multiset of primes that *is* the number's identity. This is why primality tests work (a "prime" with no factors ≤ √n has none at all), why φ(pq) = (p−1)(q−1) (the CRT structure of the residue classes), and why RSA's whole security story reduces to "factoring n gives the atoms; without them you can't rebuild φ(n)."

## 4. φ Counts What's Invertible

φ(n) = |{1 ≤ a ≤ n : gcd(a, n) = 1}| — the size of the *unit group* of Z/nZ. Every theorem about a^φ(n) ≡ 1 is really "the units form a finite group, so every element's order divides the group's size" (Lagrange). This one sentence subsumes Fermat (group of size p−1), Euler (group of size φ(n)), and the existence of primitive roots (a group that is cyclic).

## 5. Exponentiation Is Repeated Multiplication in a Small World

a^e mod m: because residues live in only m states, the sequence a, a², a³, … must eventually repeat — the **order** of a is the cycle length, and the order divides φ(m) for units. Fermat is "a's order divides p−1, so a^(p−1) returns to 1"; the "clock" of repeated multiplication wraps around with a period you can compute. This is also why square-and-multiply works: you're composing within a group, and every intermediate stays in [0, m).

## 6. CRT: Change of Coordinates

x mod 105 and (x mod 3, x mod 5, x mod 7) carry identical information (pairwise coprime moduli) — CRT is just a *change of basis* from one big ring to a product of small ones. Practical translation: a problem mod pq (hard: p, q unknown) becomes two problems mod p and mod q (easy: each is a small clock) — the structural trick behind RSA decryption proofs, Pollard's rho, and many a hand-computed exercise.

## 7. Remainder as "What's Left After Grouping"

Division: n = qd + r. The remainder answers "if I make groups of size d, what doesn't fit?" — which makes gcd (the biggest group size that leaves no leftovers for both numbers) and the Euclidean algorithm (the leftover shrinks fast: r < d) intuitive rather than procedural. Euclid's speed is the observation that leftovers decrease geometrically (worst case = Fibonacci, which still shrinks like φⁿ ≈ 1.618ⁿ per two steps).

## 8. Size Is the Security Parameter

The only reason RSA works is that "compute φ(n)" and "factor n" are the same hard problem, and both are easy for humans *who know p and q*. Always ask: which side of the sqrt/wall are we on? Trial factoring is O(√n) — trivial for 10¹², hopeless for 10³⁰⁰. The mental line between "computationally fine" and "computationally impossible" is a specific exponent, and number theory is where you learn to compute it.
