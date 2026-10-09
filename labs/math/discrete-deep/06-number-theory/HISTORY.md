# History: Number Theory

## The Ancient Foundations

**Euclid (c. 300 BC)** gave the theory its shape in the *Elements* (Books VII–IX): the Euclidean algorithm for greatest common divisors (Prop. VII.2 — still the fastest general method, 2,300 years later), unique factorization into primes (Prop. IX.20 — with the beautiful proof: if a₁…aₙ + 1 is divisible by any of the primes in a list, it has a prime *outside* the list), and the infinitude of primes: "if there were finitely many, their product plus one would have a prime factor not in the list."

**The Sieve of Eratosthenes (c. 250 BC)** listed primes by crossing off multiples — the first algorithm whose description survives complete.

**Sun Zi (孫子, c. 3rd century AD)** posed the *huàn shù* problem in the *Sunzi Suanjing*: "there are things of unknown number; if counted by threes there is a remainder of two, by fives a remainder of three, by sevens a remainder of two — what is it?" (answer: 23) — the Chinese Remainder Theorem, fifteen centuries before Gauss.

**Diophantus (c. 250 AD)**, in *Arithmetica*, studied equations in integers — the "Diophantine" tradition that resumed in Europe 1,400 years later.

## Fermat and Euler: The Golden Age Begins

**Pierre de Fermat (1601–1665)** wrote in the margin of his copy of Diophantus (c. 1637): "It is impossible to separate a cube into two cubes, or a fourth power into two fourth powers, or in general, any power higher than the second into two like powers" — **Fermat's Last Theorem**, unproved until **Andrew Wiles (1995)**. In 1640 Fermat stated to Frenicle de Bessy what we call **Fermat's little theorem**: if p is prime then a^p ≡ a (mod p) — his "little" theorem because the margin theorem was the hard one.

**Leonhard Euler (1707–1783)** proved FLT for n = 4 (using infinite descent, 1738), introduced the **totient function φ(n)** (count of integers ≤ n coprime to n) and proved the generalization **a^φ(n) ≡ 1 (mod n)** when gcd(a, n) = 1 (1763), along with the multiplicative structure φ(pq) = (p−1)(q−1) for primes — the identity RSA is built on. Euler also proved quadratic reciprocity (1748) in an early form, and extended continued-fraction and modular methods throughout his career.

**Joseph Louis Lagrange (1736–1813)** proved **Wilson's theorem** (n prime ⇔ (n−1)! ≡ −1 mod n), conjectured by Edward Waring and John Wilson, in 1771.

## Gauss Systematizes Everything (1801)

**Carl Friedrich Gauss (1777–1855)**, at age 24, published *Disquisitiones Arithmeticae*, which:

- fixed the **congruence notation** a ≡ b (mod n) — our lab's core notation is a direct quotation;
- proved **quadratic reciprocity** (conjectured independently by Euler and Legendre), giving a criterion for when x² ≡ p (mod q) is solvable — Gauss called it *theorema aureum* and gave six proofs in his life;
- developed **quadratic residues**, Gauss's lemma, primitive roots, and the decomposition of primes in cyclotomic fields.

**Adrien-Marie Legendre (1752–1833)** had already introduced the **Legendre symbol** (a/p) in his *Essai sur la théorie des nombres* (1798) and stated reciprocity.

## The Analytic Turn and Primes in Arithmetic Progressions

**Peter Gustav Lejeune Dirichlet (1805–1859)** proved in 1837 that every arithmetic progression a, a+d, a+2d, … with gcd(a, d) = 1 contains **infinitely many primes** — the first use of L-functions (his "Dirichlet series") in number theory. His *Vorlesungen über Zahlentheorie* (1863) coined the term "ideal" and shaped algebraic number theory.

**Bernhard Riemann (1826–1866)** connected primes to the zeta function in his 1859 memoir; the **Prime Number Theorem** (π(x) ~ x/ln x), conjectured by Gauss and Legendre, was proved independently by **Jacques Hadamard** and **Charles Jean de la Vallée Poussin (1896)**.

**Robert Daniel Carmichael (1879–1967)** found in 1910 the smallest composite n passing Fermat's test for every base coprime to n (561 = 3·11·17) — "Carmichael numbers" that fool Fermat tests.

## The Computational Century

**Derrick Lehmer (1914–2011)** built mechanical prime sieves and the **Lucas–Lehmer test** lineage for Mersenne primes (1930s, implemented by Lehmer). **Miller (1976)** showed a randomized primality test under ERH; **Rabin (1980)** made it unconditional — the Miller–Rabin test in everyday use. **Lenstra and Pomerance**, with **Agrawal, Kayal, Saxena (2002)** produced **AKS**, the first deterministic polynomial-time primality test (O(log^12 n) originally, improved to O(log^6 n)); primality is officially in P.

Factoring remained hard: the **general number field sieve** (Lenstra, Lenstra, Manasse, Pollard, 1993) sub-exponential attack stands behind RSA's security assumption, with best-known complexity exp((64/9)^(1/3) (ln n)^(1/3) (ln ln n)^(2/3)).
