# References: Number Theory

## Primary Sources

- **Euclid, *Elements*, Books VII–IX (c. 300 BC)** — the Euclidean algorithm (VII.1–2), primes and unique factorization (VII.30–32), and the infinitude of primes (IX.20). Still the clearest statement of the classical arguments; many free translations exist (e.g., the Perseus/Tufts archive).
- **Sun Zi (孫子), *Sunzi Suanjing* (c. 3rd century AD)** — the *huàn shù* remainder puzzle (answer 23), the earliest known Chinese Remainder Theorem problem.
- **Pierre de Fermat, letters to Frenicle de Bessy (1640)** — Fermat's little theorem as stated to other mathematicians in correspondence; and the marginal note in his copy of Diophantus (c. 1637) recording the Last Theorem.
- **Leonhard Euler, "Theoremata arithmetica nova methodo demonstrata" (1763)** and related papers of the 1740s–60s — the totient function and a^φ(n) ≡ 1 (mod n); Euler's proofs for FLT at n = 4 and his work on quadratic reciprocity.
- **Carl Friedrich Gauss, *Disquisitiones Arithmeticae* (1801)** — congruence notation, quadratic residues, reciprocity (with six proofs), primitive roots, and the foundations of the field. English translation by A. A. Clarke (Yale, 1966; Chelsea reprint).
- **Peter Gustav Lejeune Dirichlet, "Beweis des Satzes, dass jede unbegrenzte arithmetische Progression, deren erstes Glied und Differenz ganzen Zahlen ohne gemeinschaftlichen Factor sind, unendlich viele Primzahlen enthält" (Monatsberichte der Berliner Akademie, 1837)** — primes in arithmetic progressions.
- **Bernhard Riemann, "Über die Anzahl der Primzahlen unter einer gegebenen Grösse" (1859)** — the zeta-function memoir.
- **Manindra Agrawal, Neeraj Kayal, Nitin Saxena, "PRIMES is in P" (Annals of Mathematics 160, 2004; announced 2002)** — the AKS deterministic polynomial primality test.

## Textbooks

- **Tom Apostol, *Introduction to Analytic Number Theory* (Springer, UTM, 1976)** — the standard undergraduate analytic text: congruences, residues, primes in progressions, PNT.
- **David Burton, *Elementary Number Theory*, 8th ed. (McGraw-Hill, 2020)** — the accessible computational-leaning treatment; good problem sets for this lab's STEP_BY_STEP work.
- **Kenneth Ireland & Michael Rosen, *A Classical Introduction to Modern Mathematics*, 3rd ed. (Springer, 2000)** — bridges elementary number theory and algebraic structures (groups, fields, Galois theory).
- **Niven, Zuckerman, Montgomery, *An Introduction to the Theory of Numbers*, 5th ed. (Wiley, 1991)** — the comprehensive reference: divisibility, Diophantine equations, congruences, analytic topics.
- **Hardy & Wright, *An Introduction to the Theory of Numbers*, 6th ed. (Oxford, 2008)** — the classic with the deepest perspective; Chapter X on congruences, Chapter XX on primes in progressions.
- **Alfred Menezes, Paul van Oorschot, Scott Vanstone, *Handbook of Applied Cryptography* (CRC, 1996)** — free from the authors' site; Ch. 4 (number-theoretic preliminaries) is the engineering reference.

## Computational / Cryptographic

- **Ron Rivest, Adi Shamir, Leonard Adleman, "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems" (CACM 21, 1978)** — the RSA paper.
- **Alfred Menezes, Paul van Oorschot, Scott Vanstone, *Handbook of Applied Cryptography* (CRC, 1996)** — free from the authors' site; Ch. 4 (number-theoretic preliminaries) is the engineering reference for modular arithmetic, primality, and factoring.
- **Gary Miller, "Riemann's Hypothesis and Tests for Primality" (J. Comput. Syst. Sci. 1976)**; **Michael Rabin, "Probabilistic Algorithms" (1980)** — the Miller–Rabin test.
- **Richard Crandall & Carl Pomerance, *Prime Numbers: A Computational Perspective*, 2nd ed. (Springer, 2005)** — trial division, Pollard's rho, QS/NFS, and implementation details for every algorithm in INTERNALS and PERFORMANCE.
- **Menezes–van Oorschot–Vanstone (above)**, §4.6 of Knuth TAOCP Vol. 2, and **Donald Knuth, *The Art of Computer Programming*, Vol. 2, 3rd ed. (Seminumerical Algorithms, 1997)** — §4.5.2 (gcd), §4.6.2 (factoring), §4.6.3 (modular arithmetic), the standard source for the arithmetic algorithms' analysis.

## For This Lab's Hand Computations

- **Titu Andreescu & Dorin Andrica, *Number Theory: Structures, Examples, and Problems* (Birkhäuser, 2009)** — worked solutions for gcd, congruence, and CRT exercises of exactly the STEP_BY_STEP variety.
- **David Burton, *Elementary Number Theory*, Ch. 2 and Ch. 4 exercises** — short computational problems with answers in the back, ideal for checking the sieve traces and inverse computations in this lab.
