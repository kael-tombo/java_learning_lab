# MATH_FOUNDATION — Dynamic Programming (Overview)
> Recurrences, Master theorem, amortized analysis for DP.

## 1. Recurrences (tailored)
- Fib/ways: `T(n)=T(n-1)+T(n-2)+O(1)` naive → `Θ(φⁿ)`; DP collapses to `O(n)` states.
- Generic DP cost = `(#states) × (transition cost)` — the master formula (not Master theorem).
- Knapsack: `nW` states × `O(1)` → `Θ(nW)` pseudo-polynomial.
- LCS/LIS: `O(nm)` / `O(n log n)` optimized; matrix chain `O(n³)`.
- DAG longest path: `O(V+E)` (topo + relax) — linear DP on DAG.

## 2. Master Theorem (scope + limits)
- Applies to divide-and-conquer recurrences `aT(n/b)+f`, not typical DP (which sums smaller prefixes).
- Still useful inside DP: merge-style subroutines, segment-tree DP optimization (`2T(n/2)+n`).
- D&C optimization (Aliens/Divide-Conquer DP): `T(k,n)=2T(k,n/2)+O(k·n)`-ish analysis.
- State when Master does NOT apply — common interview trap.
- Use induction/tree for `T(n)=T(n-1)+O(1)`-style DP fills.

## 3. Optimal Substructure + Overlap Counting
- Substructure: optimum contains optima of subproblems (cut-and-paste proof).
- Overlap: count distinct states (e.g., `n+1` for Fib vs `2ⁿ` tree nodes).
- DAG view: states as nodes, transitions as edges; DP = topo-order relaxation.
- Cyclic dependencies → not DP (needs another method / Bellman-Ford style iteration).

## 4. Amortized Analysis
- Memo: each state pays transition once → aggregate `O(states × t)`.
- Path compression/DSU inside DP-adjacent algos: `α(V)` amortized (Kruskal context).
- Table doubling for `dp` growth (e.g., extensible memo): `O(1)` amortized append.
- Potential view: `Φ` = uncomputed states; each fill drops `Φ` by 1.

## 5. Complexity Classes
- Pseudo-poly (`nW`): poly in magnitude, exp in bits (`log W`).
- NP-hard (knapsack) vs polynomial (LCS, intervals) — reduction awareness.
- FPTAS tradeoff: `(1−ε)` approx in `poly(n,1/ε)`.

## 6. Worked Numbers
- Fib: tree `~φ⁵⁰≈20B` vs DP 51 states.
- Knapsack `n=100,W=10⁵` → 10⁷ ops fine; `W=10⁹` → infeasible.
- LIS `n=10⁵`: `O(n²)` fails, `O(n log n)` passes.

## 7. Exercises
- [ ] State-count analysis for 3 DP problems.
- [ ] Prove overlap ratio on Fib.
- [ ] Show why Master misapplies to `T(n-1)+1`.
- [ ] Amortized memo proof via Φ.
