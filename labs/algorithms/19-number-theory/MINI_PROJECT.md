# Mini Project: Sieve and Euclid
> Prime listing plus Bezout coefficients with self-checks.

## Background
- Extended Euclid unwinds the remainder chain into the Bezout identity.
- The sieve crosses multiples from p*p; the double-log bound follows.
- Every routine asserts its own defining equation before printing.
## Goal
Implement egcd, sieve, and modpow with check equations.
Pass a 12-case batch covering primes, factors, and powers.
## Tasks
1. Implement egcd returning (g, x, y) with the a*x + b*y assertion.
2. Implement the sieve with p*p starts and list output.
3. Implement modpow with per-step reduction.
4. Add trial-division factoring with product verification.
5. Build the 12-case batch: egcd(30,20), primes(30), factor(1001), modpow cases, edges.
6. Run the batch and require 12 of 12 passing.
## Acceptance criteria
- egcd(30, 20) prints g = 10 with a passing check equation.
- primes(30) prints exactly the 10 expected primes.
- factor(1001) prints 7 11 13 with verified product.
- modpow(2, 16, 17) prints 1.
- Batch reports 12 of 12 passing.
## Pitfalls
- Recursion without the b = 0 base case ordering (division by zero).
- Sieve from 2*p instead of p*p with no asymptotic awareness.
- modpow without per-step reduction overflowing on moderate inputs.
- Calling Fermat passes primality proof in comments or output.
## Stretch
- Carmichael demo: base-2 passes under 1000 listed with notes.
- Segmented sieve sketch for inputs above the memory cap.
## Timebox
One evening session, roughly 2 hours with the batch run.
