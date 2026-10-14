# MINI_PROJECT — Advanced Number Theory
> Build a classical primality-and-factoring bench: binary modPow, fixed-base Miller-Rabin, and Pollard Rho, with every verdict checkable.

## Inputs
- Integer list file; must include 17, 561, 2047, 7919, and 8051.
- Bases fixed to {2, 7, 61} for all Miller-Rabin runs (documented as the run's stated scope: correct over the 32-bit range).

## Build steps
1. Implement binary modular exponentiation on long; verify powmod(3,200,1000)=1 and 2^16=1 mod 17.
2. Demonstrate the Fermat gap: 2^340=1 mod 341 with 341=11x31, one line of commentary on why Fermat alone misleads.
3. Implement Miller-Rabin with the fixed bases; verify 17=PRIME, 561=COMPOSITE, 2047=COMPOSITE, 7919=PRIME.
4. Implement Pollard Rho (f(x)=x^2+1, Floyd) with trial division by small primes first; verify 8051=97x83.
5. Emit one verdict line per input (`n=... verdict=... witness_or_factor=...`) and a scope note stating the base set and range.

## Acceptance criteria
1. modPow outputs match 1, true/true exactly as in the lab snippet.
2. Miller-Rabin verdicts match all four reference classifications.
3. Pollard Rho prints factor=97 cofactor=83 for 8051; trial division comes first in code order.
4. 341 is shown factored (11x31) next to its pseudoprime equation, never presented as prime.
5. Scope note states the {2,7,61} bases and the 32-bit range limit explicitly.
6. Multiplication overflow guard (long intermediates, non-negative mod) is covered by a comment plus one edge test at the int boundary.

## Analysis prompts
1. Why does 561 fool base 2 Fermat but fall to Miller-Rabin? Trace the witness chain.
2. What input shape makes Pollard Rho return d=n, and what is the exact restart rule?
3. Where does trial division stop and Rho take over in your pipeline, and why there?

## Non-goals
- Proof of the deterministic base set, ECM/quadratic sieve, and any production-crypto certification claim.

## Worked reference (verified outputs)
- modPow prints powmod(3,200,1000)=1 with fermat_ok=true pseudo341=true; 341 shown factored as 11x31 beside it.
- Miller-Rabin prints 17=PRIME, 561=COMPOSITE, 2047=COMPOSITE, 7919=PRIME; Rho prints factor=97 cofactor=83.

## Stretch
- Add perfect-power precheck before Rho and demonstrate it on 3^8 = 6561.
- Add a round-count policy for inputs above 32 bits with the count logged per verdict.
