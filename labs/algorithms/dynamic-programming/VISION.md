# VISION — Dynamic Programming Track
> Direction: from recursion with memo to table-shape thinking — state, transition, order, reconstruction.

## Where this sits
- Core patterns: sequences (LIS O(n log n), LCS/edit O(nm)), knapsack O(nW) pseudo-polynomial, intervals (matrix chain O(n^3)), DAGs (shortest path O(V+E)), Bellman-Ford O(VE) with negative edges.
- The discipline is DAG thinking: every DP is shortest/longest path on a state graph; cycles mean the formulation is wrong.
- Reconstruction (backpointers) is half the skill; values without witnesses do not ship.

## 4-week direction
- Week 1: hand-fill LIS and edit-distance tables for the reference inputs until 4 and 3 are reproducible cold.
- Week 2: finish MINI_PROJECT; write the pseudo-polynomial paragraph from your own timing data.
- Week 3: add reconstruction to every table that lacks it; print alignments, pack lists, and parenthesizations.
- Week 4: REAL_WORLD_PROJECT review; whiteboard any lab recurrence with its fill order in 5 minutes.

## Done criteria
- Write each lab recurrence plus fill order and reconstruction rule from memory.
- Distinguish polynomial from pseudo-polynomial with the bit-length argument on demand.
- Pick memo vs tabulation for a given (state size, sparsity, stack) triple.

## Non-coverage
- This track does not cover tree/digit/bitmask DP (dp-deep), DP optimizations (Knuth, divide-and-conquer, monotone queue), or FPTAS design beyond naming.
- No claim that DP is the right tool when greedy suffices; the exchange argument comes first.
- Probabilistic DP (MDPs) belongs to another track.

## Pitfalls
- Filling tables in the wrong order and reading garbage with confidence.
- Shipping values without reconstructions; unwitnessed optima are undebuggable.
- Calling O(nW) polynomial; W is a value, not a size.

## Adjacent tracks
- Pair with dp-deep for structured state (trees, digits, masks) and 38-mst-variants for exchange-argument proofs.
- Revisit before adding another dimension to a table; state count is the budget.

## Weekly drills
- Refill the LIS and edit-distance reference tables cold; reproduce 4 and 3.
- Recite one recurrence per lab file with fill order and reconstruction rule.
- Argue polynomial vs pseudo-polynomial for knapsack with the bit-length example.

## Anti-roadmap
- Do not add dimensions to dodge modeling; each dimension multiplies the table.
- Do not ship values without witnesses; reconstructions are deliverables.
