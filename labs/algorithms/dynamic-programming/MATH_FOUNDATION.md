# MATH_FOUNDATION — Dynamic Programming Track
> Recurrences / Master theorem / amortized. Track `dynamic-programming`.

## 1. Recurrence toolkit
- T(n) = a·T(n/b) + f(n); Master cases 1/2/3.
- Naive fib: T(n) = T(n-1)+T(n-2)+O(1) → Θ(φ^n).
- Memoized fib: n states × O(1) → Θ(n).

## 2. Master theorem cases
- Case 1: leaves dominate. Case 2: balanced → log factor. Case 3: root dominates + regularity.
- Drill: mergesort 2T(n/2)+O(n) → Θ(n log n).

## 3. State-count method (primary DP tool)
- Bound = #states × transition cost.
- Grid mn × O(1) = O(mn); coin amount×n; knapsack nW.
- Prove by counting table cells + per-cell work.

## 4. Akra-Bazzi sketch
- Uneven splits Σ a_i T(b_i n) + f(n); solve Σ a_i b_i^p = 1.
- Rarely needed at intro level; know it exists for uneven recurrences.

## 5. Amortized: dynamic array
- 3-credit accounting → O(1) push; shrink at 1/4.
- Analogy: memo pays once per state, reads many times.

## 6. Amortized: counter
- n increments = O(n) flips → O(1) each; Φ = #ones.
- Same telescoping as DP reuse arguments.

## 7. Amortized: union-find (preview)
- Size + compression → O(α(n)); used in dp-deep tree/graph hybrids.

## 8. Lower-bound thinking
- Output size lower-bounds time (e.g., print all paths is exponential).
- Counting vs enumerating: counts can be poly while listings are not.

## 9. Practice proofs (do on paper)
- Prove naive fib exponential via φ tree.
- Prove memo fib linear by state counting.
- Prove grid bound by cell counting.
- Prove dynamic-array accounting.

## Checklist
- [ ] State Master case in 30s. [ ] Sketch one amortized proof. [ ] Derive memo bound.
