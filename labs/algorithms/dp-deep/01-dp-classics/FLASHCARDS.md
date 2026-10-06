# Flashcards — DP Classics

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | The five DP questions | state · meaning · transition · base cases · fill order |
| 2 | The skill in DP | writing a **complete, precise** state definition |
| 3 | Naive `fib` complexity | `Θ(φⁿ)`, `φ = (1+√5)/2 ≈ 1.618` |
| 4 | Memoised `fib` | `Θ(n)` time, `Θ(n)` space, `O(1)` rolled |
| 5 | Distinct subproblems of `fib(n)` | exactly `n+1` |
| 6 | What memoisation actually is | **deduplication**, not optimisation |
| 7 | Fibonacci characteristic equation | `r² = r + 1` ⇒ `r = φ` |
| 8 | `fib` `int` overflow | `n ≥ 47` |
| 9 | `fib` `long` overflow | `n ≥ 93` |
| 10 | Fibonacci closed form instability | `double` loses the fractional part past `n ≈ 70` |
| 11 | DP correctness proof | strong induction; 2 steps: **acyclicity** + **faithfulness** |
| 12 | Every DP bug violates | acyclicity (reads a future state) or faithfulness (wrong recurrence) |
| 13 | Top-down obligations | check memo → check base → recurse (order matters) |
| 14 | Bottom-up obligation | fill order must be a **topological order** of the dependency DAG |
| 15 | Top-down stack depth | `Θ(n)` — `StackOverflowError` above `n ≈ 10⁴` |
| 16 | When top-down wins | the state space is **sparse** (few reachable states) |
| 17 | When bottom-up wins | dense state space, large `n`, tight time budget |
| 18 | Rolling array break-even | `n ≳ 10⁷` ints (must exceed L3) |
| 19 | Rolling arrays reduce | **peak footprint only** — memory traffic is identical |
| 20 | Rolling arrays cost | you can no longer reconstruct the solution |
| 21 | Safe `INF` for an `int` DP | `Integer.MAX_VALUE / 2` |
| 22 | `INF = MAX_VALUE` failure | `INF + 1 = MIN_VALUE` — a "negative cost" propagates |
| 23 | `seen[]` vs sentinel memo | `seen[]` is unambiguous for every value domain; costs 1 byte/state |
| 24 | Top-down memo sentinel bug | `0` collides with `F(0) = 0` and with "min coins for 0" |
| 25 | Climbing stairs base case | **`dp[0] = 1`** (one empty way), not 0 |
| 26 | Climbing stairs identity | `ways(n) == fib(n+1)` — assert it |
| 27 | Rod cutting state | `dp[i]` = max revenue from a rod of length `i` |
| 28 | Rod cutting transition | `dp[i] = max(price[j] + dp[i-j])`, `j = 1..i` |
| 29 | Rod cutting initialiser | `dp[i] = price[i]` — the "no cut" option |
| 30 | Rod cutting complexity | `Θ(n²)` time, `Θ(n)` space |
| 31 | Unbounded coin change state | `dp[a]` = min coins to make amount `a` |
| 32 | Coin change base | `dp[0] = 0` (min) / `dp[0] = 1` (count) |
| 33 | Coin change complexity | `Θ(n·k)` — `n` = max amount, `k` = #coins |
| 34 | Coin change unreachable | must return `-1`/`∞`; not every amount is reachable |
| 35 | Compositions vs combinations | **loop order**: amounts outer vs coins outer |
| 36 | Compositions example | `{1,2}`, amount 3 → **3**; combinations → **2** |
| 37 | Unbounded knapsack fill order | capacities **ascending** ⇒ items reusable |
| 38 | 0/1 knapsack fill order | capacities **descending** ⇒ items used once |
| 39 | The wrong fill order is | a **silently different problem**, not a crash |
| 40 | Triangular fill saving | `2×` on `Θ(n²)` DPs (only fill `j ≤ i`) |
| 41 | DP feasibility limit | `|states| ≲ 10⁷` for an `int` 2-D table |
| 42 | Held–Karp state count | `2ⁿ` — feasible to `n ≈ 20–24` |
| 43 | 2-D rolling `diagonal` save | required or `dp[i-1][j-1]` is destroyed |
| 44 | The `diagonal` bug's signature | first row correct, everything after wrong |
| 45 | The rolled-Fibonacci bug | swapping `prev1 += prev2; prev2 = prev1;` doubles instead of adding |
| 46 | Optimal substructure | every optimal solution is composed of optimal subsolutions |
| 47 | The `Θ(n·k)` DP shape | `n` states × `k` transitions — almost every classical DP |
| 48 | Lab `08` optimisations | all reduce the inner `k` loop (D&C, SMAWK, monotone queue, bitset, WQS) |
| 49 | When can a problem not be bottom-up? | when the dependency graph is cyclic under the index order |
| 50 | Cross-validation gold standard | `topDown == bottomUp == bruteForce` for all small `n` |
| 51 | The strongest DP invariant to assert | `combinations ≤ compositions` |
| 52 | Rod cutting greedy counterexample | derive it yourself; `{1,5,6,9}`, `n = 10` works |
| 53 | Canonical coin systems | `{1,5,10,25}` greedy is correct; `{1,3,4}` it is not; decidable in `Θ(k)` |
| 54 | Coin change greedy failure | `{1,3,4}`, amount 6: greedy `4+1+1`=3, optimal `3+3`=2 |
| 55 | Coin change huge amounts | not DP — use gcd reachability + closed forms for 2 denominations |
| 56 | Reconstruction requires | the `choice[]`/full table — `Θ(n)` space, `O(k)` cannot |
| 57 | Master theorem on a memoised linear recurrence | `a=2, b=2, f=O(1)` → Case 1 → `Θ(n)` |
| 58 | Java default thread stack | ~512 KB–1 MB ⇒ ~10⁴ frames |
| 59 | "Exactly `k` steps" variant | `Θ(nk)`, or `Θ(n)` with a sliding window |
| 60 | "No three consecutive" variant | add state dimensions: `dp[i][0..2]` |

## Self-test (one line each)

1. Two contentful steps of the DP correctness proof? → **Acyclicity (reads only smaller states) and faithfulness (the transition is the defining recurrence)**
2. Why does top-down need a `seen[]` or a sentinel outside the answer domain? → **Because `0` can be a legitimate answer, and `memo[n] != 0` then recomputes**
3. Compositions vs combinations? → **Loop order: amounts outer vs coins outer — `Θ(nk)` either way**
4. Rolling arrays: what do they actually reduce? → **Peak footprint only — memory traffic is unchanged; pay-off above ~10⁷ ints**
5. When does top-down beat bottom-up? → **When the state space is sparse and the reachable set is small**