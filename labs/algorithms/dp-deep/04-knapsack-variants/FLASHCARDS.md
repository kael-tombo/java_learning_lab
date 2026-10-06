# Flashcards — Knapsack Variants

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | 0/1 knapsack state | `dp[w]` = max value with total weight **at most** `w` |
| 2 | 0/1 loop order | **descending** `w` — that *is* the specification |
| 3 | Unbounded loop order | **ascending** `w` |
| 4 | Test that catches the swap | `items = [(1,3)], W = 10` → `3` vs `30` |
| 5 | "At most" initialisation | `0` (empty set always feasible) |
| 6 | "Exactly" initialisation | `-∞`, using `MAX_VALUE/2` + a reachability check |
| 7 | `NEG = Integer.MIN_VALUE` pitfall | `NEG + v` **overflows to positive** |
| 8 | 0/1 complexity | `Θ(nW)` time, `Θ(W)` space |
| 9 | Viability wall | `nW ≲ 10⁹` for Java (~5 s) |
| 10 | Bounded naive time | `Θ(W Σ cᵢ)` — explodes |
| 11 | Binary splitting | `c → {1,2,4,…,2^{m−1}, c−(2^m−1)}`, `⌈log₂(c+1)⌉` bundles |
| 12 | Binary-split completeness | **every** count in `[0,c]` must be a subset sum, not merely partitioned |
| 13 | Bounded binary-split time | `Θ(W Σ log cᵢ)` |
| 14 | Bounded monotone queue | **`Θ(nW)`**, independent of `c` |
| 15 | Monotone-queue reparametrisation | `newDp[r+t·p] = t·q + max{X(s) : s∈[t−c,t]}`, `X(s)=dp[r+s·p]−s·q` |
| 16 | Monotone-queue window | `[t−c, t]` — **both endpoints inclusive** |
| 17 | Monotone-queue pitfall | forgetting `− s·q` gives the *unbounded* answer |
| 18 | Monotone-queue pitfall | `s <= t−c` expiry silently gives `c−1` copies |
| 19 | Fractional algorithm | greedy by `v/w` descending, `Θ(n log n)`, **exact** |
| 20 | Fractional correctness | LP vertex has ≤ 1 fractional variable; exchange argument proves greedy optimal |
| 21 | Greedy on 0/1 | `Θ(n log n)` with a `2`-approximation |
| 22 | Tighter bound | **`11/9 ≈ 1.2222`** (Martello–Toth, tight) |
| 23 | Fractional comparator | cross-multiply with `long`; do **not** divide |
| 24 | Fractional overflow guard | `v, w ≤ 10⁹` ⇒ `vᵢw_j ≤ 10¹⁸ < 2⁶³` |
| 25 | Subset sum boolean DP | `Θ(nW)` time, `Θ(W)` bits |
| 26 | Subset sum **bitset** | **`Θ(nW/64)`** word ops, `Θ(W/8)` bytes |
| 27 | Bitset update | `bits |= bits << x`, **descending** word order |
| 28 | Bitset pitfall | `>>> (64 − bitShift)` with `bitShift == 0` becomes `>>> 0` |
| 29 | Bitset pitfall test | a weight of exactly 64 exercises `wordShift=1, bitShift=0` |
| 30 | DP by profit `P` | `dp[p]` = min weight for value ≥ `p`; `Θ(nP)`; descending `p` |
| 31 | When by-profit wins | `P ≪ W` |
| 32 | DP by `Σwᵢ` | `Θ(n·min(W, Σwᵢ))` |
| 33 | Meet-in-the-middle | `Θ(n 2^{n/2})` time, `Θ(2^{n/2})` space |
| 34 | MITM feasibility | `n ≤ 44`; wins when `2^{n/2} < W` ⟺ `n < 2 log₂ W` |
| 35 | MITM memory tip | parallel `long[]` arrays, not `List<record>` |
| 36 | Branch and bound | `O(2ⁿ)` worst; exact; fast on ratio-friendly instances |
| 37 | Pisinger 1997 | linear-time bounded knapsack via breakpoint DP, `Θ(n·min(c, W/w))` |
| 38 | Multi-dim time | `Θ(n Π Wᵢ)` — `d ≥ 3` impractical |
| 39 | Multi-dim alternative | LP relaxation + branch and bound, or a Pareto frontier |
| 40 | Pareto frontier | `Θ(n·|P|)`; measure `|P|` before choosing |
| 41 | Group knapsack nesting | group loop **outermost** |
| 42 | Group knapsack pitfall | group loop inside `w` ⇒ two items from one group |
| 43 | Dependency knapsack | turns into **max closure / min cut**, `Θ(nm)` |
| 44 | Reconstruction from `Θ(W)` roll | **impossible** — use a bitset per item |
| 45 | Reconstruction memory | `long[]` bitset per item: `n·W/8` bytes |
| 46 | Alternative reconstruction | re-run the DP from `i−1` backwards, `Θ(nW)` extra time, `Θ(W)` space |
| 47 | Coin change | unbounded knapsack by value (`dp[c] = min coins`) |
| 48 | Rod cutting | unbounded knapsack with `price[j]` as the item value |
| 49 | Fractional greedy vs exact DP | use greedy when `nW` is infeasible; the `11/9` bound is the contract |
| 50 | Weak NP-completeness | 0/1 knapsack; pseudo-polynomial `Θ(nW)` is the best known |
| 51 | "Pseudo-polynomial" meaning | polynomial in the *numeric value* `W`, not in `log W` |
| 52 | The encoding trap | `W` may be exponentially large in `log W` ⇒ the `Θ(nW)` DP may be exponential |
| 53 | Chained invariant test | `solve01 ≤ solveBounded ≤ solveUnbounded` |
| 54 | Equality invariant test | `binarySplit == monotoneQueue == MITM == 0/1` |
| 55 | Fractional vs exact invariant | fractional `≥` 0/1 optimum (it is a relaxation) |
| 56 | Include `count = 0` in tests | it is where the monotone-queue push/expire order matters |
| 57 | Include duplicate weights in tests | it is where the 0/1 vs unbounded loop order matters |
| 58 | Empty `W` | return 0 |
| 59 | Item with `weight > W` | never selected; skip it |
| 60 | Greedy mis-ordering risk | use exact cross-multiplication, never doubles |

## Self-test (one line each)

1. Why is the loop direction part of the 0/1 spec? → **Descending makes `dp[w−wᵢ]` read the previous item's row; ascending reads the current row's already-updated value, which is exactly the unbounded recurrence**
2. Bounded monotone queue derivation? → **`newDp[r+t·p] = t·q + max{ dp[r+s·p] − s·q : s ∈ [t−c, t] }` — a sliding-window max, `Θ(nW)` independent of `c`**
3. Fractional greedy guarantee, and its 0/1 counterpart? → **Exact, `Θ(n log n)`; on 0/1 it is a `2`-approximation tightened to `11/9`**
4. Bitset subset sum speedup and its pitfall? → **`Θ(nW/64)` word ops, descending order; `>>> (64−bitShift)` must be guarded when `bitShift == 0`**
5. When is MITM the right choice? → **`n ≤ 44` with `W ≫ n`**, i.e. `2^{n/2} < W`