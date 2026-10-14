# MINI_PROJECT — DP Deep Track
> Advanced DP forms: tree DP with rerooting, digit DP, bitmask DP, plus one optimized transition (divide-and-conquer or Knuth) with the monotonicity condition stated.

## Inputs
- Random trees (n = 100/1k/10k) for tree DP; digit queries counting numbers <= 10^12 with a digit property; bitmask TSP instances n <= 14 shared with 32-exact-exponential.
- Reference: tree independent-set size on a fixed 7-node tree verified against brute force; digit count verified against brute force below 10^5.

## Build steps
1. Implement tree DP (max independent set) with one rerooting pass for all-root answers; verify against brute force on the 7-node tree.
2. Implement digit DP (tight/loose, positional memo) for a stated property (e.g. digit-sum divisible by 7); verify against brute force below 10^5.
3. Implement bitmask DP (Held-Karp reuse allowed with citation) for n <= 14 and cross-check vs the 32-lab outputs.
4. Implement one optimized transition: divide-and-conquer DP optimization with the quadrangle/monotonicity condition written out, or Knuth with its quadrangle + monotonicity preconditions.
5. Record time and state counts per method; state the precondition each optimization depends on.

## Acceptance criteria
1. Tree DP matches brute force on the 7-node tree for every root after rerooting.
2. Digit DP matches brute force below 10^5 and answers the 10^12 query within the time budget from a single run.
3. Bitmask DP agrees with the 32-lab reference optimum (80) on the shared 4-city matrix.
4. Optimization section states the monotonicity/quadrangle precondition verbatim and includes a test that would fail if it were violated.
5. State-count table (not just time) recorded per method from real runs.
6. All memo keys documented with their exact meaning (pos/tight/started or mask/last).

## Analysis prompts
1. Where does rerooting save the naive O(n^2) re-solve, in messages passed?
2. Which digit-DP dimension (tight, sum mod, started) dominates state count?
3. What breaks in D&C optimization if opt-index monotonicity fails?

## Non-goals
- Profile/plug DP and alien-trick Lagrangian methods (named with triggers), and full FPTAS constructions.

## Exact-match anchors
- 7-node tree DP must match brute force for every root after the reroot pass, not just root zero.
- Digit DP below 10^5 must match brute force exactly before the 10^12 answer counts.

## Stretch
- Add profile DP for domino tilings on small widths with the state encoding documented.
- Add monotone-queue optimization for a bounded-knapsack instance and state its window condition.
