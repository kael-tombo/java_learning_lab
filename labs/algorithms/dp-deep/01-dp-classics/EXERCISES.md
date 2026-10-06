# Exercises — DP Classics

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.dpclassics`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Trace Fibonacci

**Bottom-up, tabulated** for `n = 6`:

| `i` | `dp[i-1]` | `dp[i-2]` | `dp[i]` |
|-----|-----------|-----------|---------|
| base | — | — | `dp[0]=0`, `dp[1]=1` |
| 2 | 1 | 0 | 1 |
| 3 | 1 | 1 | 2 |
| 4 | 2 | 1 | 3 |
| 5 | 3 | 2 | 5 |
| 6 | 5 | 3 | 8 |

**Rolled (`O(1)` space)** for `n = 6`:

| `i` | `prev1` | `prev2` | `cur` | after |
|-----|---------|---------|-------|-------|
| init | 1 | 0 | — | — |
| 2 | 1 | 0 | 1 | `prev1=1, prev2=1` |
| 3 | 1 | 1 | 2 | `prev1=2, prev2=1` |
| 4 | 2 | 1 | 3 | `prev1=3, prev2=2` |
| 5 | 3 | 2 | 5 | `prev1=5, prev2=3` |
| 6 | 5 | 3 | 8 | `prev1=8, prev2=5` |

Return `prev1 = 8` ✓

**Now trace the buggy assignment order** `prev1 += prev2; prev2 = prev1;`:

| `i` | `prev1` | `prev2` | after | correct? |
|-----|---------|---------|-------|----------|
| init | 1 | 0 | | |
| 2 | 1 | 1 | 1 | ✓ |
| 3 | 2 | 2 | 2 | ✓ |
| 4 | 4 | 4 | 4 | ✗ (should be 3) |
| 5 | 8 | 8 | 8 | ✗ |

**Answer in writing:** the values are increasing and plausible, so what kind of test catches this? (Answer: it satisfies `f(n) = 2·f(n-1)` — a *different* recurrence. Compare against `F(n) = F(n-1)+F(n-2)` computed independently, or assert `f(4) == 3`.)

---

## Exercise 2 — Count recursion-tree nodes

Instrument the naive recursion with a counter. Report the number of calls for `n = 0..30` and verify:

1. It equals `2·F(n+1) − 1` for `n ≥ 1`.
2. The number of **distinct** arguments is exactly `n+1`.
3. The ratio `calls(n)/calls(n-1)` tends to `φ = 1.618`.

Then instrument the memoised version and confirm it makes exactly `n+1` calls. **Explain the whole collapse in terms of "distinct subproblems", not "memoisation is faster".**

**Bonus:** draw the recursion tree for `fib(5)` and mark each node with the number of times it is visited. `fib(3)` is visited 5 times. Verify.

---

## Exercise 3 — Derive a greedy counterexample for rod cutting

**Do not look this up.** Write a brute-force rod-cutting solver, then search:

```java
for (int n = 2; n <= 12 && !found; n++)
    for (int p1 = 1; p1 <= n && !found; p1++)
        for (int p2 = p1; p2 <= n && !found; p2++)
            for (int p3 = p2; p3 <= n && !found; p3++) {
                if (p1 + p2 + p3 != n) continue;
                int[] price = new int[n + 1];
                price[p1] = 1; price[p2] = 2; price[p3] = 4;   // set ONLY these lengths
                int greedy = 0;                                 // naive length-greedy
                int rem = n;
                while (rem > 0) {
                    int take = Math.min(rem, p3);
                    greedy += price[take] * (take / p3) + price[take % p3];
                    rem -= take;
                }
                if (greedy < dp[n]) { report; found = true; }
            }
```

**Report:** the smallest `n`, the price vector, greedy's answer, and the DP's answer, plus the ratio. Then explain *why* greedy fails here: the price-per-unit ratios are not monotone in length, so the greedy ratio order is not a valid exchange argument.

---

## Exercise 4 — Coin change: all four variants

Implement and validate:

| variant | returns | loop order |
|---------|---------|-----------|
| `minCoins` | fewest coins, `-1` if impossible | amounts outer |
| `countCompositions` | number of **ordered** ways | amounts outer |
| `countCombinations` | number of **unordered** ways | **coins outer** |
| `minCoinsGreedy` | fewest coins, greedy by largest | n/a — and possibly wrong |

Trace all four for `coins = {1, 3, 4}`, `amount = 6`:

| | result |
|---|---|
| `minCoins` | `2` (`3+3`) |
| `countCompositions` | enumerate: `1+1+1+1+1+1`, `3+1+1+1`, `1+3+1+1`, `1+1+3+1`, `1+1+1+3`, `4+1+1`, `1+4+1`, `1+1+4`, `3+3` ⇒ **9** |
| `countCombinations` | `{1,1,1,1,1,1}`, `{3,1,1,1}`, `{4,1,1}`, `{3,3}` ⇒ **4** |
| `minCoinsGreedy` | `4+1+1` = 3 coins ⇒ **wrong**, should be 2 |

**Then:** implement `minCoinsGreedy` and **prove** it is correct for `coins = {1, 5, 10, 25}` (US coins) and wrong for `coins = {1, 3, 4}` (the classic). Explain why "canonical coin systems" is a real property and whether it is known which systems are canonical. (Answer: yes — `Kozen and Zaks` / Pearson's characterisation; `{1,5,10,25}` and `{1,2,5,10,20,50,100}` are canonical, `{1,3,4}` is not, and it is decidable in `Θ(k)` for `k` denominations.)

---

## Exercise 5 — `INF` overflow hunt

Implement `minCoins` three ways and find the smallest input that breaks each:

| variant | sentinel |
|---------|----------|
| A | `INF = Integer.MAX_VALUE / 2` |
| B | `INF = Integer.MAX_VALUE` |
| C | `INF = Integer.MAX_VALUE`, no reachability check |
| D | `INF = Integer.MAX_VALUE - 1` |

Find the smallest `(coins, amount)` where B/C/D return a **negative** or absurdly small number.

**Then:** prove that `MAX_VALUE/2` is always safe for `minCoins`, i.e. that `dp[a]` never exceeds `MAX_VALUE/2 - 1` for any reachable `a ≤ amount`. (Argument: `dp[a] ≤ a` because coin 1 is always available when `a` is reachable; and the `amount` in any realistic problem is `≪ 2³⁰`. State the assumption and note where it breaks.)

**And:** what happens for `amount = 2³⁰`? (`new int[amount+1]` is 4 GB — `OutOfMemoryError`.) What is the alternative for huge amounts? (Answer: number theory — Bézout/gcd first to test reachability, then a closed-form for two denominations: `amount/g - floor((amount - (g-1)c₂)/g)` type results. See labs `02-number-theory-advanced` and `39-number-theory-advanced`.)

---

## Exercise 6 — Reconstruction: prove the `Θ(n)` space claim

Implement `cutPlan` for rod cutting and `coinChangePlan` for minCoins. For both:

1. Verify the reconstructed solution's value equals the DP answer.
2. Show the reconstruction table is `Θ(n)` space — then argue **why you cannot roll the array and still reconstruct.** (The argument: reconstruction needs to know, at each step, which transition was optimal at the *current* index; a rolled array has discarded that. Counter-example: `price = {1, 5, 6, 9, 10}`, `n = 10` — several indices tie, and the optimal choice at `i` differs from the one a single pass would make. Construct one.)
3. Implement a **backward** reconstruction that only keeps the `choice[]` array (`Θ(n)` but no `dp[]`), and show it is cheaper in memory than keeping both.

---

## Exercise 7 — Top-down vs bottom-up, measured

For `fib`, `ways`, `maxRevenue`, and `minCoins`, measure on `n` from `10²` to `10⁷`:

| algorithm | states computed (top-down) | states computed (bottom-up) | top-down time | bottom-up time | ratio |
|-----------|---------------------------|-----------------------------|----------------|----------------|-------|
| fib | | (n/a) | | | |
| ways | | (n) | | | |
| maxRevenue | | (n) | | | |
| minCoins | | (amount) | | | |

**Answer in writing:**

1. For `minCoins` with `coins = {1, 2, 5}` and `amount = 10⁶`, does top-down compute **all** `amount+1` states? (Yes — every `a` is reachable and `dp[a]` depends on `dp[a-1]`.) Now try `coins = {7, 11}` and `amount = 10⁶`: **how many states does top-down reach?** (Only the amounts expressible as `7a + 11b`, which is `Θ(amount)` anyway by the Frobenius structure — but compute the exact count.) This is the case where top-down wins, and you should find the arithmetic.

2. Why is top-down *always* slower or equal on these problems? (Hash/array lookup per call plus recursion frames plus poor locality.)

3. At what `n` does top-down overflow the stack, and what is the exact Java default? (Default thread stack ~512 KB–1 MB; ~10⁴ frames for a simple DP. Measure it.)

---

## Exercise 8 — Rolling-array equivalence

For each recurrence, implement (a) the full table and (b) a rolled `O(k)` version, and assert equality for all `n` up to `10⁵`:

| recurrence | `k` |
|-----------|-----|
| `dp[i] = dp[i-1] + dp[i-2]` | 2 |
| `dp[i] = max(dp[i-1], x[i])` | 1 |
| `dp[i] = Σ_{j=1..3} dp[i-j]` | 3 |
| `dp[i][j] = max(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + a[i][j]` | needs `diagonal` |
| `dp[i] = dp[i-1] + (i % 2)` | 1 |

Then: implement the 2-D rolled version **without** the `diagonal` save and find the smallest failing instance. Explain in one sentence why the first row is correct and everything after is wrong.

**Bonus:** measure whether rolling is faster for `n = 10⁴`, `10⁶`, `10⁷`, `10⁸`. Predict the crossover (see `MATH_FOUNDATION.md` §3) and verify. **Report whether your hardware shows the predicted `10⁷` crossover.**

---

## Exercise 9 — Climbing-stairs variant zoo

Implement and validate each against a brute-force enumeration of all move sequences:

| variant | constraint |
|---------|-----------|
| 1,2 steps | baseline |
| 1..k steps | `Θ(nk)`, and `Θ(n)` with a sliding window |
| exactly `k` steps | sliding window over `dp[i-1..i-k]` |
| no three consecutive 1-steps | needs `dp[i][0..2]` — a 3-state DP |
| forbidden steps `{3, 7}` | mask then DP |
| steps of distinct sizes only | different state |
| landing exactly on `n`, no overshoot | the base case changes |

**Trace the "no three consecutive" variant by hand for `n = 6`:** state `dp[i][k]` = ways to reach `i` ending with exactly `k` consecutive 1-steps, `k ∈ {0,1,2}`. Show the full 2-D table and confirm it matches brute force.

**Then answer:** how many *state dimensions* did each variant add, and what is the general rule for when you need a `k`-dimensional DP? (Rule: when the constraint involves "the last `r` decisions", add `r` dimensions.)

---

## Exercise 10 — Debugging drills

Find and fix each. For each, state the **specific test** that catches it.

1. `int[] memo = new int[n+1];` (initialised to 0) with `if (memo[n] != 0) return memo[n];` — fails at which `n`?
2. Bottom-up loop starting at `i = 1` with `dp[i] = dp[i-1] + dp[i-2]` — reads `dp[-1]`. What happens?
3. `countCombinations` with the loops swapped — which variant do you get, and how do you tell from the output?
4. `minCoins` with `INF = Integer.MAX_VALUE` and no reachability check on `coins = {3, 5}`, `amount = 7`.
5. Rod cutting with `dp[i] = 0` as the initialiser and `for (j = 1; j < i; j++)` — what is lost?
6. `maxRevenue` with `price = new int[n]` instead of `n+1` and `j` running to `i` — index error?
7. 2-D grid DP rolled without `diagonal` — smallest failing case?
8. `waysExactly(n, k)` with the sliding-window subtraction removed — what does it compute?
9. Top-down DP with the cache check **after** the base check reversed — behaviour change?
10. A `long` DP with `INF = Long.MAX_VALUE` — at what point does `dp[a-c] + 1` overflow, and what does it look like?

---

## Exercise 11 — Deliverable

`MINI_PROJECT/DpTable.java`: an interactive-ish visualiser. Given a small problem instance (rod cutting prices, coin set), print:
- the full `dp` table with indices;
- the states in **fill order**, annotated with which prior cells each transition read;
- the reconstruction path highlighted;
- for the top-down version, the recursion tree with hit/miss colouring on each node.

Then `BENCHMARK/DpRace.java`: a markdown table of naive / top-down / bottom-up / rolled for every problem in the lab, at `n ∈ {10³, 10⁵, 10⁶, 10⁷}`, including the **states-computed** column.

**Answer in writing:** for which problem in this lab is top-down *better* than bottom-up, and what property of the state space causes it? (Hint: look at Exercise 7's coin-set experiment.)