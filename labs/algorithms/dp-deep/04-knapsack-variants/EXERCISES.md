# Exercises — Knapsack Variants

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.knapsack`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Trace the 0/1 DP

Items `[(w,v)] = [(2,3), (3,4), (4,5), (5,8)]`, `W = 7`. Fill the table:

| `w` | after item 1 `(2,3)` | after item 2 `(3,4)` | after item 3 `(4,5)` | after item 4 `(5,8)` |
|-----|--------------------|--------------------|--------------------|--------------------|
| 0 | | | | |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |

**Answer: `dp[7] = 11`** (items 2 and 4: weight 8? no — items 1+4 = weight 7, value 11. Verify.)

**Now run the same trace with an ASCENDING loop** and confirm you get a different (larger) number: `unbounded` gives `dp[7] = 14` (item 1 three times = weight 6, value 9, plus... verify). **The trace is the proof that loop order is the specification.**

---

## Exercise 2 — "At most" vs "exactly"

Implement `solve01` and `solveExact`. For items `[(2,3), (3,4), (4,5)]`, `W = 5`:

| | `solve01` | `solveExact` |
|---|---|---|
| `dp[5]` | | |
| Is weight 5 reachable? | yes (0) | **no** — `2+3 = 5` yes! | |
| `dp[4]` | | |

Redo with items `[(2,3), (4,5)]`, `W = 5`:
| | `solve01` | `solveExact` |
|---|---|---|

**Then:** find the smallest item set where `solveExact` returns `-1` while `solve01` returns a value. Answer: `[(2,3)], W = 3` — `solve01` = 3, `solveExact` = `-1`.

**Explain in writing why `dp[w] = 0` initialisation is correct for "at most" and wrong for "exactly".** ("At most `w`" with the empty set always gives value 0 for every `w`. "Exactly `w`" is unreachable unless a subset sums to `w`.)

---

## Exercise 3 — Bounded: three methods must agree

Implement `solveBoundedSplit` and `solveBoundedDeque`. Test on `count = 0..15` for every `c`, with items `[(w,v)] = [(3,7), (5,11)]`, `W = 30`:

| `c₁`,`c₂` | naive `O(W·c)` | binary split | monotone queue | MITM-with-bounds |
|-----------|---------------|--------------|----------------|-----------------|
| (0,0) | | | | |
| (1,0) | | | | |
| (2,3) | | | | |
| (5,2) | | | | |
| (7,6) | | | | |
| (10,6) | | | | |
| (15,15) | | | | |

**Then answer in writing:** prove the binary decomposition `{1,2,4,…,2^{m−1}, c−(2^m−1)}` covers **every** count in `[0, c]`. Give the proof (do not just assert it).

**And:** find the smallest `c` and `W` where the monotone queue's `s < t - c` window is off by one. (Answer: any `c ≥ 1` — you must include `s = t-c`.) Show the wrong answer with `<=`.

---

## Exercise 4 — Monotone-queue trace

For item `(p=3, q=7, c=2)` applied to `dp = [0, 1, 5, 2, 8, 3, 9, 4, 11, 6]`, `W = 9`:

**Residue `r = 0`:** states `w = 0, 3, 6, 9` ⇒ `t = 0, 1, 2, 3`. Compute `X(t) = dp[3t] − 7t`:

| `t` | `dp[3t]` | `X(t)` | deque after push+expire | `next[3t]` |
|-----|----------|--------|----------------------|-----------|
| 0 | 0 | 0 | `[s=0, X=0]` | `0 + 0 = 0` |
| 1 | 2 | `2−7 = −5` | | |
| 2 | 9 | `9−14 = −5` | | |
| 3 | 6 | `6−21 = −15` | | |

Fill it in and verify `next[9] = max(dp[9], dp[6]+7, dp[3]+14) = max(6, 9+7, 2+14) = 16`.

Do the same for residues `r = 1` and `r = 2`. Then verify the whole `next` array against the naive triple loop.

**Trace the dominance pops explicitly** — for each `t`, which `s` values are dropped and why.

---

## Exercise 5 — Fractional: greedy proof and the `11/9` bound

1. Verify the greedy solution is optimal by brute force over all fractional allocations with a fine grid: for `n = 3` items and `W = 10`, enumerate all allocations in steps of `1/1000` and confirm greedy's value is the max.
2. **Derive the exchange argument** in writing: if `S` is optimal and items `a, b` have `vₐ/wₐ > v_b/w_b` with `a` under-filled and `b` in `S`, show that moving `δ` weight from `b` to `a` strictly increases the value. Compute `Δvalue = δ·wₐ·(vₐ/wₐ − v_b/w_b)`.
3. **Find an instance where greedy-by-ratio on 0/1 is far from optimal.** Use items `[(w,v)] = [(10,10), (10,10), (20,19)]`, `W = 20`: greedy takes the first two → `20`; optimal is `(20,19) + (10,10) = 29`. Ratio: `29/20 = 1.45`.
4. Search exhaustively for the **worst-case ratio** over all instances with `n ≤ 5` and small weights/values. Report the maximum `greedy/OPT` you find and the instance. (The theory says the supremum is `11/9 ≈ 1.2222` — see if you can get close with a small search, and explain why small `n` cannot reach the supremum.)

**Then:** implement greedy + local search (try adding one unselected item, dropping one selected item, swapping one for one) and measure how much of the gap it closes on 1000 random instances.

---

## Exercise 6 — Bitset subset sum

Implement `subsetSum`. Validate against the boolean DP for 20 000 random cases with `W ≤ 200`, alphabet weights `{1..20}`.

**Explicitly test:**
- `a = [5,5], W = 10` → must be **`false`** (0/1!)
- `a = [5,5,5], W = 10` → `true`
- `a = [1], W = 0` → `true`
- `a = [W], W` → `true`
- `a = [W+1], W` → `false`
- `a` with a weight of exactly `64`, `W = 64` → exercises `wordShift = 1, bitShift = 0` (the `>>> 64` pitfall!)
- `a` with weight `1`, `W = 200` → exercises cross-word carry

**Benchmark** `W = 10⁶`, `n = 1000`: bitset vs boolean DP. Verify the `64×` ratio (it will be less in practice — report the actual).

**Then:** implement the **unbounded** bitset variant (ascending loop) and confirm the `a = [5,5], W = 10` case flips to `true`.

---

## Exercise 7 — Trading the axes

For instances with `n = 100` and `W ∈ {10³, 10⁵, 10⁷, 10⁹}`:

1. Run `solve01` and record whether it completes. Mark the infeasible cells.
2. Run `solveByProfit` (vary the values so `P ∈ {10³, 10⁵, 10⁷}`).
3. Run `solveMITM` where `n ≤ 44`.
4. Run the fractional greedy.

**Fill in the matrix of which method is feasible, and answer in writing:**
- At what `nW` does the DP stop being viable in Java? (Answer: ~`10⁹` operations, ≈ 5 s, and ~`4·10⁹` bytes if you keep a 2-D table for reconstruction.)
- When does by-profit win? (`P ≪ W`.)
- When does MITM win? (`n < 2 log₂ W`.)
- What is the honest engineering recommendation for `n = 10⁵`, `W = 10¹²`? (Fractional greedy with the `11/9` bound, plus local search, plus an explicit statement to stakeholders that the answer is approximate.)

---

## Exercise 8 — Multi-dimensional and group knapsack

1. Implement `d`-dimensional knapsack for `d = 1, 2, 3`. Show the state-count blow-up numerically.
2. Implement **group** knapsack (at most one item per group) and demonstrate that putting the group loop **inside** the weight loop lets you take two items from one group. Find the smallest witness.
3. Implement the **Pareto frontier** version for the 2-objective problem. Measure the frontier size on random instances and compare with the `Θ(nW)` DP.

**Answer:** for a real multi-constraint allocation problem (ad budget × audience size × frequency cap), why is the DP the wrong tool and LP relaxation + branch and bound the right one?

---

## Exercise 9 — Branch and bound (CHALLENGE)

Implement branch and bound: sort by ratio descending, DFS with the fractional-knapsack bound on the remaining items, prune when `bound ≤ incumbent`.

- Verify it returns the exact optimum on 1000 small instances against the DP.
- Measure the number of nodes explored for `n = 50, 100, 200` with correlated and uncorrelated weights.
- **Find the hard instance class**: weights equal, values equal (every subset ties) is degenerate. Try weights that are `w[i] = i` and values `v[i] = i + random` — that is the hard class for B&B.
- Report the crossover with `Θ(nW)`.

**Compare with the Pisinger (1997) linear-time bounded algorithm** — describe it in one paragraph: it keeps the best and second-best breakpoints and does a `Θ(n·min(c, W/w_i))` sweep that avoids the modulo decomposition entirely. Implement it if time allows.

---

## Exercise 10 — Debugging drills

1. 0/1 with an ascending loop — find the smallest witness that differs from the descending version.
2. `solveExact` with `dp` initialised to `0` instead of `NEG` — what happens for `items = [(2,3)], W = 3`?
3. `solveExact` with `NEG = Integer.MIN_VALUE` and no reachability check — what does `dp[3]` become?
4. Binary splitting with `take = Math.min(size, remaining)` where `size` overflows — construct the failure for `c = 2³⁰`.
5. Monotone queue with `s < t - c` replaced by `s <= t - c` — find the smallest failing instance.
6. Monotone queue with expire-before-push — what breaks when `c = 0`?
7. Fractional comparator using `(double) vi / wi` — find two items whose order flips relative to cross-multiplication.
8. Bitset with an ascending word loop — what does it compute?
9. Bitset without the `bitShift != 0` guard, with a weight of exactly 64 — verify the wrong bit gets OR'd in.
10. `solveByProfit` with an ascending `p` loop — what does it compute?

---

## Exercise 11 — Deliverable

`MINI_PROJECT/KnapsackViz.java`: print the `dp` row after each item, highlighting which cells changed, and overlay the selected items. Include a mode for the bounded variants that shows the monotone-queue windows.

Then `BENCHMARK/KnapsackRace.java` producing a markdown table: 0/1, unbounded, bounded-split, bounded-deque, fractional, by-profit, MITM, Pareto — across `(n, W)` regimes including the infeasible ones (marked `-`).

**Answer in writing:** state the decision rule you would put in a code review: *"use 0/1 DP if ...; use greedy if ...; use MITM if ...; declare the problem NP-hard and stop if ..."*