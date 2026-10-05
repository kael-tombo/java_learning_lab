# THEORY — 0/1 Knapsack DP
> Mechanics + invariants + complexity proof sketch for knapsack.

## 1. Problem Statement
- Input: `n` items `(wᵢ,vᵢ)`, capacity `W≥0`. Each taken ≤ once.
- Output: max value with `Σw≤W` (+ chosen set optionally).
- 0/1 vs fractional (greedy ok) vs unbounded (repeat allowed) — different recurrences.
- Success: `O(nW)` pseudo-polynomial, reconstruction correct, 1-D direction right.

## 2. Mechanics
- 2-D: `dp[i][w]=max(dp[i-1][w], dp[i-1][w-wᵢ]+vᵢ)` if `wᵢ≤w` else `dp[i-1][w]`.
- Bases `dp[0][*]=0`. Answer `dp[n][W]`. Reconstruct: walk back, take ⟺ value came from diag.
- 1-D: `dp[w]` descending `w=W..wᵢ`: `dp[w]=max(dp[w],dp[w-wᵢ]+vᵢ)`.
- Ascending 1-D = unbounded (wrong for 0/1) — classic bug, test it.
- Zero-weight positive-value items: handle explicitly (take all, avoid `0`-loop weirdness).

## 3. Invariants
- 2-D I: `dp[i][w]` = optimum using first `i` items at capacity `w`.
- Init `i=0` zeros correct. Step: case split (skip `i` vs take `i` once) exhaustive.
- 1-D I: descending loop keeps `dp[w-wᵢ]` = previous-row value (not-yet-overwritten this round).
- Termination: `i=n` (or all items processed) → optimum over all subsets.
- Reconstruction I: backtrack maintains residual capacity + remaining items.

## 4. Worked Trace
- Items `(2,3),(3,4),(4,5)` W=5: table → best 7 (`{2,3}` weights 2+3).
- Show `dp` rows: i=0 all 0; i=1 `[0,0,3,3,3,3]`; i=2 ...; answer 7.
- 1-D descending trace matches 2-D last row; ascending would over-take (demo bug).

## 5. Complexity Proof Sketch
- States `n·(W+1)`, `O(1)` transition → `Θ(nW)` time.
- Space 2-D `Θ(nW)` (reconstructable), 1-D `Θ(W)` (value only; keep parent or table for set).
- Pseudo-polynomial: polynomial in `W` (magnitude), exponential in `log W` (input bits) → NP-hard overall.
- Fractional contrast: greedy by ratio `O(n log n)` optimal (exchange argument) — 0/1 lacks it.
- Counter-example: `(W=50: A(10,10×5?) )` classic where ratio-greedy fails for 0/1.

## 6. Correctness Argument
- Induction on `i` with optimal-substructure: optimum either skips or takes item `i` (then optimal on rest at `W-wᵢ`).
- Exhaustiveness of two cases + IH gives recurrence soundness.

## 7. When NOT to Use
- `W` huge (1e9) → `nW` infeasible; use meet-in-middle (`n≤34`), branch-bound, or FPTAS.
- Fractional allowed → greedy. Unbounded → different DP (ascending loop).
- Small `n` → brute force `2ⁿ` simpler.

## 8. Java Notes
- `int[][] dp` or two rows; `dp[w-wi]+vi` overflow-guard if values near `Integer.MAX`.
- Reconstruction needs `boolean[][] take` or full table — don't promise set from 1-D alone.
- Input validation: `wᵢ<0` meaningless; `W<0` → exception.

## 9. Common Misconceptions
- "`O(nW)` = polynomial" — pseudo; `W` is value not size.
- "1-D ascending works" — only for unbounded; direction is semantics.
- "Greedy by value/weight works for 0/1" — false; needs proof-less counterexample.

## 10. Checklist
- [ ] 2-D + 1-D both coded, directions commented.
- [ ] Reconstruction tested on ties.
- [ ] Ascending-bug demo captured.
- [ ] `W=0`/empty/zero-weight cases pass.
