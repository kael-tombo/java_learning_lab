# Vision: Number Theory for Algorithms
> GCD, sieves, and modular arithmetic: the integers as an algorithmic playground.

## Where this leads
- Primality utilities, factoring helpers, and modular exponentiation.
- RSA-literacy: understanding what the key operations are without deploying toy RSA.
- Divisibility reasoning used in hashing, RNGs, and calendar-style problems.
## What mastering it unlocks
- Run extended Euclid and produce Bezout coefficients with the check value.
- Sieve to n in O(n log log n) and justify starting crossings at p^2.
- Compute modular powers with square-and-multiply in O(log e) multiplies.
- Reduce a modular inverse to extended Euclid correctly.
- Distinguish prime, pseudoprime, and Carmichael behavior under Fermat tests.
## What it does not cover
- Analytic number theory: distributions, zeta connections, deep prime gaps.
- Primality proving (ACR-style certificates) beyond probable-prime tests.
- Algebraic structures (groups, rings, fields) as theory rather than tools.
## Core questions you will answer
- Why does a mod b shrink fast enough for logarithmic Euclid?
- Why is the sieve bound a double log, and where does each log come from?
- Why must every multiply reduce mod m in square-and-multiply?
- What does a Fermat pass on a composite actually prove?
## How to judge progress
- Derive Bezout coefficients by unwinding Euclid on new pairs.
- Analyze the sieve sum over primes without skipping steps.
- Predict Fermat-test outcomes for given bases on small composites.
## Common misuse
- Using Fermat passes as proof of primality.
- Writing modpow without per-step reduction and overflowing silently.
## After this lab
- 15-cryptographic-algorithms for what this arithmetic protects.
- 20-bit-manipulation for the bit-level view of the same integers.
One-line self-test: Explain the p^2 sieve start and the double-log bound in two sentences.
