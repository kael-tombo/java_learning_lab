# VISION — Advanced Number Theory
> Direction: from "probably prime" as a feeling to verdicts with stated bases, logged rounds, and checkable factors.

## Where this sits
- Fermat's little theorem gives a cheap but foolable test (pseudoprimes like 341, Carmichael numbers like 561).
- Miller-Rabin strengthens it with the square-root-of-unity check along n-1 = d*2^s; fixed base sets make it deterministic over bounded ranges (32-bit with the lab's stated set).
- Pollard Rho factors via Floyd-cycle gcd collisions in roughly n^(1/4) heuristic time, after trial division clears small factors.

## 4-week direction
- Week 1: hand-verify 2^16 mod 17 and the 341 pseudoprime equation; factor both 341 and 2047 by trial division.
- Week 2: finish MINI_PROJECT; trace the Miller-Rabin witness chain for 561 on paper.
- Week 3: run Rho on three semiprimes of your choice and log time-to-first-factor vs digit count.
- Week 4: REAL_WORLD_PROJECT review; whiteboard why Carmichael numbers fail Miller-Rabin despite fooling Fermat.

## Done criteria
- Define pseudoprime, witness, and Carmichael number precisely without notes.
- State the lab's base set and its range limit verbatim, and what happens outside it.
- Factor any sub-6-digit composite with the pipeline (trial division then Rho) on demand.

## Non-coverage
- This lab does not certify anything for production cryptography; use an approved library and its primality guarantees.
- No proofs of deterministic base sets and no sieve/ECM internals beyond naming and trigger conditions.
- Side-channel and constant-time concerns are out of scope.

## Pitfalls
- Quoting Miller-Rabin results without the bases and range; a verdict without scope is folklore.
- Skipping trial division before Rho and paying full random-walk cost on smooth numbers.
- Using screening verdicts to generate real key material.

## Adjacent labs
- Pair with 32-exact-exponential for search-and-bound discipline and 26-bit-manipulation for the mod-arithmetic mechanics.
- Revisit before trusting any primality verdict whose bases you cannot name.

## Weekly drills
- Factor 341 and 2047 by trial division from memory of method, not of answer.
- Write n-1 = d*2^s for 561 and 2047 and trace one Miller-Rabin base each.
- Recite the lab base set with its range limit verbatim.

## Anti-roadmap
- Do not generalize the fixed bases past 32 bits; outside needs its own analysis.
- Do not feed screening verdicts into real key generation, ever.
