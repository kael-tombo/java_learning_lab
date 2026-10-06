# 01 — DP Classics

<div align="center">

**The DP Framework · Fibonacci · Coin Change · Climbing Stairs · Rod Cutting · Top-Down vs Bottom-Up**

</div>

---

## Learning Objectives

- State the DP framework precisely: **state, transition, base cases, evaluation order, answer location**
- Convert a naive exponential recursion into a memoised `O(n)` solution by naming the *state*
- Choose top-down (memoisation) vs bottom-up (tabulation) with a stated reason, not a preference
- Detect the two DP signature shapes: *linear recurrence* and *choice/knapsack*
- Prove correctness by strong induction on the state
- Recognise when a problem is **not** DP (greedy, graph search, divide-and-conquer)
- Compute the space cost of a DP and apply rolling-array optimisation safely

## Prerequisites

- Recursion and memoisation
- Big-O notation and the Master theorem
- `11-dp-basics` and `12-dp-knapsack` for the introductory treatment

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## The Five Questions

Every DP problem is solved by answering these five, in order:

| # | Question | What it produces |
|---|----------|------------------|
| 1 | **What is the state?** | the array/dict you will index: `dp[...]` |
| 2 | **What does it mean?** | a *complete, precise* English definition — this is where bugs live |
| 3 | **What is the transition?** | `dp[i] = f(dp[< i], ...)` — must reference only *smaller* states |
| 4 | **What are the base cases?** | the values you know without any recursion |
| 5 | **In what order do I fill it?** | increasing index, or reverse if the transition points forward |

**The step-2 discipline is the whole skill.** "What does `dp[i]` mean?" is a *semantic* question, and a solution with a wrong definition compiles, runs, and returns a wrong answer.

## Algorithms Covered

### Fibonacci
- **State:** `dp[i]` = the `i`-th Fibonacci number.
- **Transition:** `dp[i] = dp[i-1] + dp[i-2]`.
- **Naive recursion:** `T(n) = 2T(n-1) + O(1) = Θ(φⁿ)` where `φ = (1+√5)/2`. **Memoising collapses it to `Θ(n)`** because the recursion tree has only `n+1` distinct nodes.
- **Overflow:** `dp[70]` overflows `int`. `dp[92]` overflows `long` (`F₉₃ > 2⁶³`).
- **The lesson:** the naive recursion computes `F(n)` from `2ⁿ` calls of which `n` are distinct — memoisation is deduplication, not optimisation.

### Coin Change (unbounded)
- **State:** `dp[i]` = the minimum number of coins to make amount `i` using an unlimited supply of the given denominations.
- **Transition:** `dp[i] = 1 + min over coins c ≤ i of dp[i - c]`.
- **Base:** `dp[0] = 0`; `dp[i] = ∞` for unreachable amounts.
- **`O(n · k)`** for `n` = max amount, `k` = number of denominations.
- **Infeasibility:** some amounts are unreachable (e.g. coins `{3,5}` cannot make 4) — must be handled, not assumed away.
- **Variant:** *count the ways* — same `O(nk)` shape but summing instead of minimising, and the answer is `dp[n]`.

### Climbing Stairs
- **State:** `dp[i]` = ways to reach step `i`.
- **Transition:** `dp[i] = dp[i-1] + dp[i-2]`.
- **This is Fibonacci with different names.** Recognising that is the skill — see the "recognition table" below.
- **Variants:** *exactly* `k` steps (sum over a window), no three consecutive same steps (needs a 3-state recurrence), forbidden steps (mask then DP).

### Rod Cutting
- **State:** `dp[i]` = maximum revenue from cutting a rod of length `i`.
- **Transition:** `dp[i] = max over cut positions j ≤ i of ( price[j] + dp[i-j] )`.
- **`O(n²)`**, and the constant-factor lesson: use `price[i]` as a candidate too (no cut), and initialise `dp[i] = price[i]`.

## Complexity Snapshot

| Problem | Naive | Memoised / tabulated | Space | Notes |
|---------|-------|----------------------|-------|-------|
| Fibonacci | `Θ(φⁿ)` | **`Θ(n)`** | `Θ(n)` / `O(1)` rolled | `O(1)` space requires keeping 2 values |
| Climbing stairs | `Θ(φⁿ)` | **`Θ(n)`** | `Θ(n)` / `O(1)` | identical recurrence |
| Rod cutting | `Θ(2ⁿ)` | **`Θ(n²)`** | `Θ(n)` | greedy fails — see below |
| Unbounded coin change | `Θ(n · 2ᵏ)` backtracking | **`Θ(n·k)`** | `Θ(n)` | must handle unreachable |
| Coin-change ways count | — | **`Θ(n·k)`** | `Θ(n)` | sum instead of min |
| 0/1 knapsack | `Θ(2ⁿ)` | **`Θ(n·W)`** | `Θ(W)` | see lab `04-knapsack-variants` |
| Edit distance | `Θ(3ⁿ)` | **`Θ(n·m)`** | `Θ(min(n,m))` rolled | see lab `02-lcs-edit-distance` |
| Longest increasing subseq | `Θ(n²)` | `Θ(n²)` or **`Θ(n log n)`** | `Θ(n)` | see lab `03-lis-kadane` |

## Recognition Table — "which bucket?"

| Symptom | Family | Example |
|---------|--------|---------|
| `f(n) = f(n-1) + f(n-2)`, linear state | **1-D linear recurrence** | Fibonacci, climbing stairs, tribonacci |
| `f(i,j) = f(i-1,j) + f(i,j-1)` or with a diagonal | **2-D grid recurrence** | LCS, edit distance, unique paths |
| "maximum over choices that split the problem" | **Partition / choice DP** | rod cutting, matrix chain, knapsack |
| "each item may be used once, decide take or skip" | **0/1 knapsack** | knapsack, subset sum, target sum |
| "each item may be reused" | **Unbounded knapsack** | coin change, rod cutting |
| "state depends on a *prefix property*, not an index" | **LIS / subarray** | LIS, max subarray, longest run |
| "state is a *tree node*" | **Tree DP** | see lab `06-tree-dp` |
| "state is a *digit* of a number" | **Digit DP** | see lab `07-digit-dp` |

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/dpclassics/` | Top-down + bottom-up for every problem |
| `src/test/java/com/alglab/dpclassics/` | Cross-validation top-down vs bottom-up vs brute force |
| `SOLUTION/` | Worked exercise solutions |
| `TESTS/` | Boundary-value suites (`n = 0`, unreachable amounts, overflow) |
| `BENCHMARK/` | Naive vs memoised vs tabulated, with call counts |
| `MINI_PROJECT/` | DP table visualiser (edit a cell, watch the table update) |
| `REAL_WORLD_PROJECT/` | Change-making / pricing optimiser |
| `CHALLENGE/` | Space-optimised variants, matrix-formula shortcuts |
| `DIAGRAMS/` | Recursion trees, DP table fills |