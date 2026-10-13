# Real-World Project: Integer Toolkit
> GCD with Bezout coefficients, prime sieve, factoring, and modular powers.

## Problem
One CLI for the integer routines every algorithms course needs: gcd, primes, factors, modpow.
Each routine ships with fixtures whose answers are independently checkable.
## Inputs
- Subcommand plus operands: egcd a b, primes n, factor n, modpow x e m.
- Bounds: n up to 1M for sieve, operands within 64-bit signed range.
- Fixture table with 12 cases and expected outputs.
## Steps
1. egcd returns (g, x, y) and asserts a*x + b*y equals g before printing.
2. primes sieves to n starting crossings at p*p and prints the list.
3. factor uses trial division to sqrt(n) and verifies the product of factors.
4. modpow uses square-and-multiply with per-step reduction.
5. Every command self-checks (product, identity, or known value) and exits nonzero on failure.
6. Batch mode runs all 12 fixtures and reports pass/fail per case.
## Acceptance criteria
- egcd(30, 20) prints g = 10 with coefficients satisfying the check equation.
- primes(30) prints exactly 2 3 5 7 11 13 17 19 23 29.
- factor(1001) prints 7 11 13 with product verified.
- modpow(2, 16, 17) prints 1 and modpow(2, 560, 561) prints 1 with the Carmichael note.
- All 12 batch fixtures pass with zero failures.
## Failure modes
- Zero and negative inputs are rejected per-command with usage hints.
- modpow with modulus 1 returns 0 with a note instead of dividing by zero.
- Sieve above the cap refuses with the memory reason, suggesting segmented sieving.
## Extensions
- Miller-Rabin probable-prime mode (conceptual note: bases and limits documented).
- Carmichael demo command listing base-2 passes under 1000.
## How to demo
- Show the batch run with all 12 fixtures passing.
- Show the Carmichael note output and explain what it does not prove.
