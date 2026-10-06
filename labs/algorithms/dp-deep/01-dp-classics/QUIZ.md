# Quiz — DP Classics

15 questions. Each key gives the reason.

---

## Q1
State the five questions that turn a problem into a DP solution, in order.

<details><summary>Answer</summary>

1. **What is the state?** → the thing you will index (`dp[...]`)
2. **What does it mean?** → a complete, precise English definition (this is where bugs live)
3. **What is the transition?** → `dp[i] = f(dp[<i], …)`, referencing only strictly smaller states
4. **What are the base cases?** → values known without recursion
5. **In what order do I fill it?** → a topological order of the dependency DAG

Step 2 is the skill. A wrong-but-plausible state definition compiles, runs, and returns a wrong answer.
</details>

## Q2
Why does memoising `fib` collapse `Θ(φⁿ)` to `Θ(n)`? Frame it as deduplication, not optimisation.

<details><summary>Answer</summary>

`T(n) = 2T(n-1) + Θ(1)` ⇒ `Θ(φⁿ)` with `φ = (1+√5)/2`.

In the recursion tree, `fib(n-2)` is reached 2×, then 3×, then 5×, … The number of **distinct** subproblems is exactly `n+1`. Memoisation computes each once:

```
M(n) = 1 + Σ_{i<n} M(i) = Θ(n)
```

The exponential cost was never distinct work — it was **repeated evaluation of the same value**.
</details>

## Q3
Give the two contentful steps of the DP correctness proof by strong induction.

<details><summary>Answer</summary>

1. **Acyclicity:** the transition reads only strictly smaller indices (so they are already correct by hypothesis).
2. **Faithfulness:** the transition *is* the defining recurrence.

The base case is checked separately. **Every DP bug violates (1) or (2)** — a negative index read is (1); reading `dp[i]` instead of `dp[i-1]` is (2). Knowing which one you violated gives you the fix.
</details>

## Q4
When is bottom-up better than top-down? Give three concrete reasons.

<details><summary>Answer</summary>

1. **Stack safety** — top-down is `Θ(n)` frames and throws `StackOverflowError` above `n ≈ 10⁴`. Bottom-up has `O(1)` depth.
2. **Constant factor** — no per-call memo lookup, no frames, flat memory access.
3. **Explicit unreachable states** — bottom-up computes the whole state space, so `∞`/sentinel handling is uniform.

**Top-down wins only when the state space is large but the reachable part is small** (see Q12).
</details>

## Q5
The sentinel for a top-down memo is `0`. What breaks?

<details><summary>Answer</summary>

If `0` is a legitimate answer — `F(0) = 0`, "min coins for amount 0" is `0`, "ways to make 0" is `1` — the cache check `if (memo[n] != 0)` treats an *already-computed* state as *uncomputed* and recomputes it. For Fibonacci that costs exponential time again for the states whose answer is `0`.

**Fix:** fill with a value outside the answer domain (`-1`, `Long.MIN_VALUE`) or keep a separate `boolean[] seen`. The `seen[]` version is unambiguous for every domain and costs 1 byte per state — usually worth it.
</details>

## Q6
Why is `dp[0] = 1` for climbing stairs, not `0`?

<details><summary>Answer</summary>

`dp[i]` = number of **ways** to reach step `i`. There is exactly one way to be at step 0: do nothing. `dp[0] = 0` would say "no ways to stand still", which is false.

With `dp[0] = 1, dp[1] = 1` you get `1,1,2,3,5,8` — Fibonacci shifted. With `dp[0] = 0` you get `1,0,1,1,2,3` — wrong at `n = 1` and `n = 2`, and only visible if you test small `n`.
</details>

## Q7
In unbounded coin change, why must the inner `w` loop run **ascending**, and what do you get if it runs descending?

<details><summary>Answer</summary>

Ascending `w` means `dp[w - weight]` has **already been updated for the current item**, so the item can be reused — that is the *unbounded* semantics.

Descending `w` means `dp[w - weight]` is still the previous item's value, so each item is used at most once — the *0/1* semantics.

**No crash, no warning — a silently different problem.** This is the #1 knapsack-family bug.
</details>

## Q8
Why is `INF = Integer.MAX_VALUE` wrong in a DP, and what is the fix?

<details><summary>Answer</summary>

`INF + 1 = Integer.MIN_VALUE` (overflow). So `Math.min(dp[a], dp[a-c] + 1)` produces a **negative** "cost", which then propagates and can even be mistaken for a valid answer.

**Fix:** `INF = Integer.MAX_VALUE / 2` (so `INF + 1` is representable), **or** an explicit `if (dp[a-c] < INF)` reachability check. For `long`, `Long.MAX_VALUE / 4`.
</details>

## Q9
Count coin-change ways with coins outer vs amounts outer. Which counts what?

<details><summary>Answer</summary>

```java
for (int a = 1; a <= amount; a++)          // AMOUNTS outer  -> ORDERED (compositions)
    for (int c : coins) dp[a] += dp[a - c];

for (int c : coins)                        // COINS outer    -> UNORDERED (combinations)
    for (int a = c; a <= amount; a++) dp[a] += dp[a - c];
```

With coins `{1,2}`, amount 3: compositions = `1+1+1, 1+2, 2+1` = **3**; combinations = `{1,1,1}, {1,2}` = **2**.

Same `Θ(nk)` cost. **A one-line change of loop order is the entire difference and it is the most common exam/interview variant.**
</details>

## Q10
Why does rolling a DP array usually *not* speed things up?

<details><summary>Answer</summary>

**Memory traffic is identical**: `n` writes + `n` reads either way. Rolling reduces **peak footprint**, not traffic.

It only pays when the full array exceeds L2/L3, so that the sequential scan misses:
| `n` ints | size | worth rolling? |
|---|---|---|
| 10⁶ | 4 MB | no (fits L3) |
| 10⁷ | 40 MB | **yes** |
| 10⁸ | 400 MB | **yes, 30–50%** |

**And it costs correctness:** rolling destroys the ability to reconstruct the solution.
</details>

## Q11
You rolled `dp[i][j] = max(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + a[i][j]` to `O(m)` and got the first row right but everything else wrong. Why?

<details><summary>Answer</summary>

You overwrote `dp[j]` in place, destroying `dp[i-1][j-1]`, which the recurrence still needs.

**The fix is a `diagonal` save:**

```java
int diagonal = 0;
for (int j = 1; j <= m; j++) {
    int up = dp[j];                        // old dp[i-1][j]
    dp[j] = Math.max(dp[j], dp[j-1]) + a[i-1][j-1];
    diagonal = up;                          // becomes next iteration's dp[i-1][j-1]
}
```

The first row is correct because `dp[0][j]` is untouched there. **A test suite that only checks small cases, or only the first row, will not catch this.**
</details>

## Q12
Give a case where top-down memoisation beats bottom-up.

<details><summary>Answer</summary>

When the **state space is much larger than the reachable set**. Example: `coins = {7, 11}`, `amount = 10⁶`. Top-down only ever visits amounts of the form `7a + 11b`, while bottom-up computes all `10⁶+1` cells, most of which are `∞`.

(For coins `{1, 5}` the reachable set is *all* amounts, so top-down gains nothing — the standard case where top-down is strictly worse.)

The general rule: **top-down when the state space is sparse; bottom-up when it is dense.**
</details>

## Q13
When can a problem *not* be solved bottom-up?

<details><summary>Answer</summary>

When the dependency graph has a **cycle under the index order** — i.e. some transition references a state that is not strictly "smaller".

Examples: `dp[i]` depending on `dp[i+1]`; a graph DP where "reachable" is cyclic (must use BFS/topological order instead); a bitmask DP where transitions add bits (order by popcount).

**Test:** can you find a total order on states such that every transition goes forward? If yes, bottom-up. If not, top-down (or an explicit topological sort).
</details>

## Q14
Why does greedy fail for rod cutting and coin change, and what is the exchange argument that fails?

<details><summary>Answer</summary>

Greedy proofs need a **greedy-choice property**: there exists an optimal solution containing the greedy choice, and the remainder is a smaller instance of the same problem.

Rod cutting with prices `{1, 5, 6, 9}`, `n = 10`: price-per-unit is not monotone in length, so "take the best ratio first" has no exchange argument — a long low-ratio piece may be replaced by two short high-ratio pieces.

Coin change with `{1, 3, 4}`, amount 6: greedy takes `4+1+1` = 3 coins; optimal is `3+3` = 2.

Greedy *does* work for canonical coin systems (`{1,5,10,25}`) — which is a real, decidable property — and the DP is needed for the non-canonical ones.
</details>

## Q15
Prove rolling cannot also reconstruct the solution, and construct a witness.

<details><summary>Answer</summary>

Reconstruction at index `i` requires knowing **which transition was optimal at `i`**. A rolled array has discarded that information, and it cannot be recovered — no state was ever stored for the indices already passed.

**Witness:** prices `{1, 5, 6, 9, 10}`, `n = 10`. Multiple `(i, j)` pairs tie at the optimum, and the choice a backward walk would make depends on values recorded at indices the rolled version overwrote. Two DP tables that produce identical *answers* can require different *paths*.

So: `O(k)` memory ⇒ answer only; `Θ(n)` memory ⇒ answer plus plan. **Design the interface around which one you need before you pick the loop.**
</details>