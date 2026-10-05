# MATH_FOUNDATION — Searching Track
> Recurrences / Master theorem / amortized. Track `searching`.

## 1. Recurrence toolkit
- T(n) = T(n/2) + O(1): Master a=1,b=2, f=O(1) → case 2 → Θ(log n).
- Recursion-tree view: log n levels × O(1) = O(log n).
- Substitution: guess c·log n, verify inductive step.

## 2. Master theorem cases
- Case 1/2/3; binary search is the canonical case-2 example (a=1).
- Contrast: mergesort 2T(n/2)+O(n) case 2 with log factor.

## 3. Information-theoretic lower bound
- n+1 outcomes (n positions + absent) need ⌈log₂(n+1)⌉ comparisons.
- Binary search achieves it: optimal in comparison model.

## 4. Interpolation analysis sketch
- Uniform keys: expected O(log log n) via shrinking gap argument.
- Skewed/adversarial: degrades to O(n); guard with fallback.

## 5. Exponential search
- Bound doubling: pos + binary in [pos/2, pos] → O(log pos).
- Optimal when target near start of unbounded array.

## 6. Amortized: sort once, query many
- q queries: binary each O(q log n) vs sort+scan trade-off.
- Batch inserts: buffer + periodic merge (log-structured idea).

## 7. Amortized: dynamic array (background)
- 3-credit accounting → O(1) push; same telescoping style as reuse proofs.

## 8. Answer-search monotonicity
- Predicate P false...false true...true; first-true well-defined.
- Correctness = monotonicity proof + binary invariant.

## 9. Practice proofs (do on paper)
- Prove binary bound via Master case 2.
- Prove lower bound ⌈log₂(n+1)⌉ via decision tree.
- Prove peak existence + logarithmic find.
- Prove amortized push O(1).

## Checklist
- [ ] State Master case in 30s. [ ] Sketch one amortized proof. [ ] Derive log bound.
