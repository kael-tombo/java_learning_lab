# VISION — Exact Exponential Algorithms
> Direction: from fearing exponentials to budgeting them precisely — right algorithm, right n, measured cutoff.

## Where this sits
- Exact exponential methods (Held-Karp O(n^2 2^n), inclusion-exclusion, branch-and-bound, meet-in-the-middle O(2^(n/2))) solve NP-hard problems optimally at small n.
- They sit between polynomial algorithms (which cannot do these problems) and heuristics (which cannot certify optimality).
- The core skill is resource budgeting: time bound, space bound, and the n where each method stops.

## 4-week direction
- Week 1: hand-run Held-Karp on the 4-city matrix; reproduce 80 without code.
- Week 2: finish MINI_PROJECT; fill the timing table from real runs and find both crossovers.
- Week 3: add one branch-and-bound lower bound (MST bound for TSP) and measure pruned nodes.
- Week 4: REAL_WORLD_PROJECT review; whiteboard Held-Karp state definition in 5 minutes.

## Done criteria
- Write the Held-Karp recurrence and both bounds (time/space) from memory.
- Explain why brute force dies near n = 12 while Held-Karp reaches ~20, with the arithmetic.
- Size the dp table in bytes for any n on demand.

## Non-coverage
- This lab does not teach approximation algorithms (Christofides, PTAS) or heuristic search (simulated annealing, genetic).
- No claim about average-case hardness; bounds here are worst-case.
- Quantum speedups for these problems are out of scope (see 35-quantum-simulation for simulation cost only).

## Pitfalls
- Quoting O(n^2 2^n) without the O(n 2^n) memory twin; memory is usually the binding constraint.
- Testing only on random matrices; structured instances (clustered cities) behave differently under branch-and-bound.
- Confusing theHeld-Karp lower bound (1-tree) with the exact DP of the same name.

## Adjacent labs
- Pair with 25-optimization-algorithms for the heuristic side and 39-number-theory-advanced for another exact-search flavor.
- Revisit before any "just brute force it" production decision; the timing table is the permit office.

## Weekly drills
- Write dp[mask][u] and both Held-Karp bounds from memory in under 5 minutes.
- Size the dp table in bytes for n = 16, 20, 24 without a calculator step skipped.
- Name the stopper resource (time vs RAM) for brute force, Held-Karp, and meet-in-the-middle.

## Anti-roadmap
- Do not run exact search without a timeout and a fallback consumer for the timeout path.
- Do not quote time bounds while ignoring the memory twin; RAM binds first here.
