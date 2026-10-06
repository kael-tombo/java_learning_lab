# Number Theory — Quiz (15 Questions with Worked Answers)

Congruences, the Chinese Remainder Theorem, Fermat's little theorem, residues,
and the difference between a theorem and an empirical pattern.

---

## Q1 — Euclid's algorithm and Bézout
**Q.** Find $\gcd(240,46)$ and integers $s,t$ with $240s+46t=\gcd$.

**A.** $240=5\cdot46+10$; $46=4\cdot10+6$; $10=1\cdot6+4$; $6=1\cdot4+2$;
$4=2\cdot2$. So $\gcd=2$. Back-substitute: $2=6-4=6-(10-6)=2\cdot6-10
=2(46-4\cdot10)-10=2\cdot46-9\cdot10=2\cdot46-9(240-5\cdot46)
=47\cdot46-9\cdot240$. Check: $47\cdot46=2162$, $9\cdot240=2160$, difference 2 ✓.
With $s=-9,t=47$. This is the extended Euclidean algorithm — the basis of modular
inverses and the proof that $\gcd(a,b)=1\Rightarrow ax\equiv1\pmod b$.

---

## Q2 — Modular inverse existence
**Q.** For which $b$ does $3$ have an inverse mod $b$? Compute it for $b=7$.

**A.** Exists iff $\gcd(3,b)=1$, i.e. $b$ not divisible by 3.
Mod 7: $3\cdot5=15\equiv1$, so $3^{-1}\equiv5$.
The general mechanism: extended Euclid returns integers with $3s+7t=1$; here
$3\cdot5+7\cdot(-2)=1$, so $s=5$ is the inverse.

---

## Q3 — Chinese Remainder Theorem
**Q.** Solve $x\equiv2\pmod3$, $x\equiv3\pmod4$, $x\equiv2\pmod5$.

**A.** First two: $x=2+3k$, and $2+3k\equiv3\pmod4$ ⇒ $3k\equiv1$ ⇒ $k\equiv3$
(since $3^{-1}\equiv3$), so $x\equiv2+9=11\pmod{12}$.
With $x\equiv2\pmod5$: $11+12m\equiv2$ ⇒ $2m\equiv-9\equiv1\pmod5$ ⇒ $m\equiv3$ ⇒
$x\equiv11+36=47\pmod{60}$.
CRT applies because the moduli are pairwise coprime; for non-coprime moduli it
applies iff the residues agree modulo the gcd ($\gcd(3,4)=1$ always consistent).
The search space collapses from $60$ candidates to one class.

---

## Q4 — CRT when the moduli are not coprime
**Q.** Solve $x\equiv1\pmod4$, $x\equiv2\pmod6$.

**A.** Inconsistent: reduce modulo $\gcd(4,6)=2$: the first says $x$ is odd,
the second says $x$ is even. No solution. Consistent versions exist, e.g.
$x\equiv1\pmod4$, $x\equiv3\pmod6$ → solution $x\equiv9\pmod{12}$.
The generalised CRT condition (residues equal mod the gcd) is worth stating
explicitly, since "solve the congruences" as a programming task must handle it.

---

## Q5 — Fermat's little theorem, and its hypothesis
**Q.** Compute $2^{100}\bmod7$. Why can't you apply FLT to $2^{100}\bmod 8$?

**A.** $\phi(7)=6$, so $2^6\equiv1$, and $100=6\cdot16+4$, so
$2^{100}\equiv2^4=16\equiv2\pmod7$.
For modulus 8: $2$ is **not coprime** to 8, so FLT does not apply; indeed
$2^{100}\equiv0\pmod8$. Using FLT here would give a wrong answer. FLT requires
$\gcd(a,p)=1$; the coprimality hypothesis is the whole point, and dropping it is
the most common misapplication.

---

## Q6 — Euler's theorem and totient
**Q.** Compute $3^{100}\bmod 10$ and justify it.

**A.** $\gcd(3,10)=1$, $\phi(10)=10(1-\frac12)(1-\frac15)=4$, so
$3^{100}=(3^4)^{25}\equiv1$. Alternatively $3^4=81\equiv1\pmod{10}$.
Actually the multiplicative order of 3 mod 10 is 4, so $3^{100}\equiv3^0\equiv1$ ✓.
Euler generalises Fermat to composite moduli. $\phi(10^k)=4\cdot10^{k-1}$ —
the standard formula for last digits, used in every "what are the last $n$
digits of $2^{2^n}$" problem.

---

## Q7 — Order, and multiplicative order modulo primes
**Q.** Order of 2 mod 7? Order of 5 mod 7?

**A.** $2^1=2$, $2^2=4$, $2^3=8\equiv1$: order 3. And $5^1=5$, $5^2=25\equiv4$,
$5^3\equiv20\equiv6\equiv-1$, so $5^6\equiv1$ and order 6 (not 3, not 2).
Order divides $\phi(7)=6$; divisors $1,2,3,6$. For prime $p$, the group is
cyclic of order $p-1$, so an element of order $p-1$ is a primitive root.
That structure is what makes discrete-log problems (and hence Diffie–Hellman)
possible — and what makes them hard.

---

## Q8 — Quadratic residues
**Q.** Which of $3,5,6,7$ are quadratic residues mod 7? What is the count?

**A.** Squares mod 7: $1,4,2,2,4,1$ for $1..6$ ⇒ $\{1,2,4\}$. So among
$3,5,6,7$ (with 7≡0) only $2$-class members qualify: none of $3,5,6$ is a
residue.
Exactly half the nonzero residues are squares: for odd prime $p$, $(p-1)/2=3$
quadratic residues. Proof: $x^2=y^2\iff x=\pm y$, so each square has exactly two
roots. The Legendre symbol $\left(\frac{a}{p}\right)=\pm1$ encodes this, and
Euler's criterion $a^{(p-1)/2}\equiv\pm1\pmod p$ makes it computable in
$O(\log p)$ — the basis of quadratic reciprocity, which underpins primality
testing and Jacobi sums.

---

## Q9 — Wilson's theorem
**Q.** What is $(p-1)!\bmod p$ for prime $p$? Verify at $p=5$.

**A.** $(p-1)!\equiv-1\pmod p$. At $p=5$: $4!=24\equiv4\equiv-1$ ✓.
Proof: pair each residue with its inverse; the only self-inverses are $\pm1$, so
the product of all pairs is 1 and the total is $-1$. Wilson's theorem is
equivalent to $p$ being prime — the practical use is that $p$ is prime iff
$(p-1)!\equiv-1\pmod p$, which is a (slow) primality criterion.

---

## Q10 — Sieve of Eratosthenes complexity
**Q.** What is the time complexity of the sieve up to $N$, and where does the
$O(N\log\log N)$ come from?

**A.** Outer loop over multiples of each prime $p$ starts at $p^2$: the total
marking work is $\sum_{p\le\sqrt N}N/p$ which is $N\sum_{p\le\sqrt N}\frac1p
=N(\log\log\sqrt N+M)=O(N\log\log N)$, using Mertens' theorem on the harmonic
sum of primes. Space is $O(N)$ bits. Contrast trial division:
$O(N\sqrt N)$ or $O(N^{1.5})$ for finding all primes — the sieve is
asymptotically much better, which is why primes are enumerated by sieving in
practice.

---

## Q11 — Composite numbers with many factors (pseudoprimes)
**Q.** Does $2^{p-1}\equiv1\pmod p$ imply $p$ prime?

**A.** No: $341=11\cdot31$ satisfies $2^{340}\equiv1\pmod{341}$ — a base-2
Fermat pseudoprime. This is why Fermat tests give false positives, and why you
need strong pseudoprime tests ($a^{(p-1)/2}\not\equiv\pm1$ for all prime
factors of $p-1$; 341 fails those) or Miller–Rabin with random bases.
Deterministic primality testing (AKS, $O(\log^6 n)$, 2002) exists but is slow in
practice; Miller–Rabin with a handful of bases is the engineering choice.

---

## Q12 — $a^0 \bmod m$ when $\gcd(a,m)\ne1$
**Q.** What is $0^0\pmod5$? And $6^{0}\bmod 8$?

**A.** $0^0$ is set to 1 by convention in modular arithmetic, and $0^0=1$ as a
monoid convention for empty products. But $6^{1000000}\bmod8=0$, since
$6^2\equiv4$ and $6^3\equiv0\bmod8$ — the multiplicative order doesn't exist.
Any algorithm that computes powers mod $m$ by repeated squaring is fine, but any
algorithm that reduces the exponent mod $\phi(m)$ requires $\gcd(a,m)=1$.
The bug this causes: computing $x^{p}\bmod m$ by reducing $p$ mod $\phi(m)$ when
$x$ shares a factor with $m$ gives wrong answers — a real source of bugs in
"modular exponentiation with huge exponents" problems.

---

## Q13 — Sum of divisors and perfect numbers
**Q.** Verify 6 and 28 are perfect.

**A.** $\sigma(6)=1+2+3+6=12=2\cdot6$ ✓; $\sigma(28)=1+2+4+7+14+28=56=2\cdot28$ ✓.
Euclid–Euler: even perfect numbers are exactly $2^{p-1}(2^p-1)$ with $2^p-1$
prime. $p=2$: $2\cdot3=6$; $p=3$: $4\cdot7=28$; $p=5$: $16\cdot31=496$.
The necessary direction (perfect ⇒ this form) is Euclid's, the converse is
Euler's. No odd perfect number is known; if one exists it exceeds $10^{1500}$.

---

## Q14 — Modular inverse exists for all units; not otherwise
**Q.** In $\mathbb{Z}_8$, which elements are invertible, and what does that
subgroup look like?

**A.** Units $\{1,3,5,7\}$, each self-inverse ($3^2=9\equiv1$, etc.), forming
$(\mathbb{Z}_8)^\times\cong C_2\times C_2$. Non-units $0,2,4,6$ have no inverse.
In general the unit group of $\mathbb{Z}_n$ is not cyclic unless
$n\in\{1,2,4,p^k,2p^k\}$ — and algorithms that assume cyclicity (and hence that
"there is a generator") break on other moduli. This is exactly why discrete-log
implementations verify the order before using Pohlig–Hellman.

---

## Q15 — Which conjecture is unproven?
**Q.** State three famous open statements and say why they matter.

**A.** (i) Goldbach (every even number $>2$ is a sum of two primes) — verified to
$4\times10^{18}$ but unproven; (ii) twin prime conjecture (infinitely many
primes at distance 2; the bounded-gap theorem gives $\liminf\le246$) — relevant to
factoring difficulty estimates; (iii) the Riemann hypothesis (the zeta function
has no zeros on $\Re s=1$) — governs the error term in the prime number theorem
($|x-\pi(x)|\lesssim\sqrt x\log^2 x$) and the security analysis of some
primality-based schemes.
The lesson: "we've checked a huge range" is not a proof, and hard-coding
verification up to a bound gives you a test, not a theorem. Where a theorem is
needed, use the proved bound (Bertrand's postulate: a prime exists in $(n,2n)$).

---

*Self-check: Q5, Q11 and Q12 are all "the standard theorem doesn't apply here"
cases. Identifying the hypothesis — coprimality — is the skill being tested.*