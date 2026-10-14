# MINI_PROJECT — Exact Exponential Algorithms
> Build a tiny exact solver kit: Held-Karp TSP, brute-force cross-check, and subset enumeration, with the measured crossover points.

## Inputs
- 4-city distance matrix from MOCK_INTERVIEW Q1 (expected optimum 80).
- Random symmetric matrices for n = 8..16 generated with a fixed seed.
- 5-vertex edge list from MOCK Q3 (expected 12 independent sets, alpha 3).

## Build steps
1. Implement Held-Karp over dp[mask][u] with O(n 2^n) memory; print the optimum for the 4-city matrix.
2. Implement permutation brute force for n <= 10 and assert equality with Held-Karp on identical inputs.
3. Implement subset-mask enumeration counting independent sets and tracking alpha.
4. Time all three on n = 8, 10, 12 (brute force only to n = 10) and record wall ms in a table.
5. Document the largest n each method handles on your machine and which resource (time vs memory) stops it first.

## Acceptance criteria
1. 4-city matrix prints heldkarp_cost=80 and bruteforce_cost=80.
2. 5-vertex graph prints independent_sets=12 and alpha=3.
3. Timing table has rows for n = 8, 10, 12 with all three applicable cells filled from real runs.
4. Held-Karp uses an int bitmask (document the n <= 25 practical ceiling from the O(n 2^n) table).
5. The write-up names the stopper resource per method (CPU for brute force, RAM for Held-Karp).
6. No method shells out to a library solver; all search code is in the submission.

## Analysis prompts
1. At what n does Held-Karp overtake brute force by 10x on your machine?
2. How much memory does the dp table need at n = 20 in bytes, computed not guessed?
3. Which lower bound would you add first to turn brute force into branch-and-bound?

## Non-goals
- Heuristic TSP (2-opt, Lin-Kernighan), approximation guarantees, and parallel solvers.

## Worked reference (verified outputs)
- 4-city matrix prints heldkarp_cost=80 and bruteforce_cost=80; the two methods must agree on every shared input.
- 5-vertex edge list prints independent_sets=12 alpha=3; alpha=3 is witnessed by vertices {1,2,4}.

## Stretch
- Add an MST (1-tree style) lower bound to the brute-force search and count pruned nodes at n=12.
- Implement meet-in-the-middle subset sum and record the n where it beats Held-Karp-style DP on memory.
