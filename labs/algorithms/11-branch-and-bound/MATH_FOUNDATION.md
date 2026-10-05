# MATH_FOUNDATION — Branch and Bound
> Recurrences, Master theorem, amortized analysis for pruned search.

## 1. Recurrences (tailored)
- Worst: `T(n)=2T(n-1)+O(bound)` → `Θ(2ⁿ)` (bound only cuts constants in worst case).
- TSP Held-Karp DP memo alternative: `O(n²·2ⁿ)` states × transitions.
- Knapsack B&B: fractional-relaxation bound per node `O(n log n)` sort once + `O(n)` per node.
- Best-first order doesn't change worst recurrence, only typical nodes explored.
- D&C contrast `2T(n/2)+n → n log n` (fractional shrink vs constant shrink).

## 2. Master Theorem (scope)
- B&B shrinks by constants → Master inapplicable; unroll/sum instead.
- Applies to sorting/bounding subroutines (fractional knapsack sort, LP relax pieces).
- State the recognition rule: fraction (`n/b`) → Master candidate; minus (`n−c`) → not.
- Akra–Bazzi for uneven branch reductions (brief).

## 3. Bound Math
- Relaxation (fractional/LP) gives admissible upper (max) / lower (min) bound.
- Bound quality = gap closed per node; strong bound prunes exponentially more.
- Fathoming rules: infeasible / bound-dominated / integral — all preserve optimum.
- Approximation + B&B: initial heuristic `best` tightens prune from the start.

## 4. Amortized Analysis
- Incremental bounds: child bound from parent in `O(1)` delta vs recompute `O(n)`.
- Aggregate over explored nodes: `nodes × delta-cost` vs naive `nodes × full-cost`.
- PQ best-first overhead `O(log Q)` per node; depth-first `O(1)` + less memory.
- Potential `Φ` = open nodes' gap sum; fathoming drops `Φ`.

## 5. Probabilistic / Heuristic Notes
- Strong branching vs pseudocost: fewer nodes vs cheaper nodes tradeoff.
- Restarts + randomization tame heavy-tail runtimes (Luby sequence).

## 6. Worked Numbers
- TSP n=20: `2²⁰≈10⁶` DP states feasible; naive `20!` impossible; B&B between.
- Knapsack `n=100`: bound prunes 99%+ on correlated instances; adversary still exponential.
- Initial greedy `best` within 5% → prune doubles (typical).

## 7. Exercises
- [ ] Unroll `2T(n-1)+n` to `Θ(2ⁿ)`.
- [ ] Fractional-bound computation on 3-item instance.
- [ ] Fathom-rule soundness proof (1 paragraph).
- [ ] Incremental vs recompute aggregate comparison.
