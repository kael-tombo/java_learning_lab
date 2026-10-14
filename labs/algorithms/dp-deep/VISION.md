# VISION — DP Deep Track
> Direction: from flat tables to structured state — trees, digits, masks — plus one optimization earned by proving its precondition.

## Where this sits
- Tree DP exploits acyclicity twice (DP up, reroot down); digit DP exploits positional structure with tight/loose flags; bitmask DP pays 2^n deliberately at small n.
- D&C and Knuth optimizations trade the monotonicity/quadrangle proof for a complexity drop; without the proof they are just bugs.
- Profile DP and alien tricks extend the menu for grid and cardinality-constrained variants.

## 4-week direction
- Week 1: hand-run tree independent-set DP both directions on the 7-node tree.
- Week 2: finish MINI_PROJECT; verify digit DP against brute force below 10^5 yourself.
- Week 3: implement the chosen optimization with its violation test; watch the test catch a broken precondition on a crafted input.
- Week 4: REAL_WORLD_PROJECT review; whiteboard reroot messaging in 10 minutes.

## Done criteria
- Write tree-DP recurrences plus reroot combination from memory.
- State digit-DP state (pos, tight, started, property) and why each dimension exists.
- Quote the exact precondition for your optimization and the test that guards it.

## Non-coverage
- This track does not build profile/plug DP or alien-trick solvers; triggers and shapes are named, implementations deferred.
- No FPTAS construction; approximation lives in 25-optimization-algorithms.
- Bitmask DP filings defer to 32-exact-exponential for the full budgeting treatment.

## Pitfalls
- Applying D&C/Knuth optimization without the monotonicity proof; fast wrong answers.
- Forgetting the started flag in digit DP and miscounting leading zeros.
- Rerooting with the wrong combination direction; verify every root against brute force.

## Adjacent tracks
- Pair with dynamic-programming for core tables and 32-exact-exponential for bitmask budgeting.
- Revisit before optimizing any transition; the precondition proof comes first.

## Weekly drills
- Recombine one reroot step by hand on the 7-node tree with messages labeled.
- Restate your optimization's precondition verbatim and describe the violation test.
- Write digit-DP state dimensions and justify each (tight, started, property).

## Anti-roadmap
- Do not optimize transitions on unproven monotonicity; the violation test is mandatory.
- Do not forget the started flag; leading-zero bugs are the classic digit-DP failure.
