# MATH_FOUNDATION — DP Deep Track
> Recurrences / Master theorem / amortized. Track `dp-deep`.

## 1. Recurrence toolkit
- T(n) = a·T(n/b) + f(n); Master 1/2/3.
- D&C optimization: T(n) = 2T(n/2) + O(n log n) → O(n log² n) level sum.
- Karatsuba-style splits appear in convolution DP speedups.

## 2. Master theorem cases
- Case 1/2/3 with ε and regularity; memorize decision tree.
- Drill: mergesort (case 2), Strassen (case 1), naive matrix (case 2/3 edge).

## 3. DP counting, not recurrences
- Table size × transition cost = bound: LCS mn×O(1); knapsack nW×O(1).
- Matrix chain: O(n²) states × O(n) splits = O(n³).
- Tree knapsack: O(n·k²) naive merges; small-to-large improves.

## 4. Knuth proof sketch
- Quadrangle inequality + monotonicity ⇒ opt range narrows.
- Total splits Σ(opt gaps) telescopes to O(n²).
- Verify conditions before applying; test on fixtures.

## 5. D&C optimization proof
- Monotone opt[i][j] ⇒ compute mid, recurse halves with bounded ranges.
- Level cost O(n log n)-ish; depth log n → stated bound via summation.

## 6. Amortized: DSU on tree (small-to-large)
- Each element moves O(log n) times → O(n log n) total merges.
- Potential: Σ size·log(size); merge charges smaller set.

## 7. Amortized: dynamic array / counter
- Push 3-credit accounting → O(1); counter bit-flips → O(1).
- Same telescoping idea as DP memo reuse: pay once, read many.

## 8. LIS bound argument
- tails[k] = min tail of length-k subsequence; binary search valid by monotonicity.
- Each x extends/replaces exactly once → O(n log n).

## 9. Practice proofs (do on paper)
- Prove LCS recurrence optimal via case split on last chars.
- Prove 0/1 backward-loop correctness (no reuse).
- Prove Knuth/D&C under monotonicity (one each).
- Prove small-to-large O(n log n).

## Checklist
- [ ] State Master case in 30s. [ ] Sketch one amortized proof. [ ] Derive LCS bound.
