# MATH_FOUNDATION — Backtracking
> Recurrences, Master theorem, amortized analysis for search trees + pruning.

## 1. Recurrences (tailored)
- N-Queens naive: `T(n)=n·T(n-1)+O(n)` → `Θ(n!)` leaf-ish.
- Subset/Sudoku: `T(n)=2T(n-1)+O(1)` → `Θ(2ⁿ)`; constrained branches cut constant.
- Permutations: `n!` leaves; combinations `2ⁿ`;Bound prunes subtrees (branch-and-bound link).
- DPLL/SAT: `T(n)=2T(n−k)+poly` with unit propagation shrinking `k`.
- Recurrence tree = search tree itself; height = depth, leaves = candidates.

## 2. Master Theorem (scope)
- Search trees shrink by constant (`n−1`), not fraction — Master inapplicable (b=1).
- Applies to D&C helpers inside backtracking (e.g., sort candidates `2T(n/2)+n`).
- Contrast: `2T(n/2)+n → n log n` vs `2T(n-1)+1 → 2ⁿ` — recognize at a glance.
- Akra–Bazzi for uneven `T(n)=T(n−1)+T(n−3)+O(1)`-style (brief).
- Interview trap: don't force Master onto `T(n-1)` forms.

## 3. Tree Counting + Pruning Math
- Full `b^d` bound (branching × depth); constraints reduce effective `b`.
- Forward checking / propagation: prune factor multiplies across levels.
- Symmetry breaking divides by orbit size (e.g., N-Queens `/8`ish).
- Lower-bound prune (B&B): subtree skipped if `bound ≥ best` (optimization form).

## 4. Amortized Analysis
- Incremental state (place/remove queen in O(1) with col/diag bitsets) — charge per node, not recompute.
- Potential `Φ` = remaining candidates; propagation drops `Φ` fast on tight constraints.
- Copy-vs-undo: undo `O(1)` amortized per edge vs copy `O(n)` — aggregate over tree favors undo.
- Memo (DP over subsets): each mask once → `O(n·2ⁿ)` from `O(n!)` (TSP Held-Karp).

## 5. Probabilistic Notes
- Random variable ordering: expected prune varies; restarts (Luby) derandomize heavy tails.
- Monte-Carlo tree estimates (knuth sampling) for size prediction.

## 6. Worked Numbers
- N-Queens n=8: 92 solutions; nodes ~2M naive → ~50k with bitsets+symmetry.
- Subsets n=30: 10⁹ leaves — infeasible; need prune or meet-in-middle.
- Sudoku: propagation cuts branching 9→2–3 average.

## 7. Exercises
- [ ] Solve `2T(n-1)+1` by unrolling.
- [ ] Bound N-Queens tree vs pruned count.
- [ ] Amortized place/remove vs copy analysis.
- [ ] Held-Karp `n·2ⁿ` state count.
