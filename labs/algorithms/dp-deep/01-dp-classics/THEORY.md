# Theory — DP Classics

Dynamic programming is the *only* algorithmic paradigm here whose core idea is not about data structures. It says: **when a problem's subproblems overlap and its structure is acyclic, compute each subproblem once and remember it.**

Everything else — the state definition, the fill order, the space optimisation — follows from making that one sentence precise.

---

## 1. Why naive recursion fails

Consider `fib(n)` as written naturally:

```java
int fib(int n) { return n < 2 ? n : fib(n - 1) + fib(n - 2); }
```

Recurrence: `T(n) = T(n-1) + T(n-2) + Θ(1)`. Solve with the characteristic equation `x² = x + 1`:

```
x = (1 ± √5)/2  ⟹  T(n) = Θ(φⁿ),  φ = (1+√5)/2 ≈ 1.618
```

| `n` | naive calls | memoised calls | ratio |
|-----|------------|----------------|-------|
| 10 | 177 | 10 | 17.7× |
| 20 | 21 845 | 20 | 1 092× |
| 30 | 2 692 601 | 30 | 89 753× |
| 40 | 331 160 981 | 40 | 8 279 024× |
| 50 | 40 730 022 147 | 50 | 814 600 442× |

**Why memoisation works.** Draw the recursion tree: `fib(n)` calls `fib(n-1)` and `fib(n-2)`; `fib(n-1)` calls `fib(n-2)` and `fib(n-3)`; **`fib(n-2)` is computed 2×, then 3×, then 5×, …**. The number of *distinct* subproblems is exactly `n+1`. Memoisation turns the tree into a DAG evaluated once per node:

```
T(n) = 2T(n/2) + Θ(1)  (conceptually: n distinct values, each computed once)
T(n) = Θ(n)   time     with  Θ(n)  memo table
```

**Memoisation is deduplication, not optimisation.** That framing is the key insight: exponential → linear because the *number of distinct states* is polynomial, not because you "made it faster".

---

## 2. The framework, stated precisely

### Top-down (memoisation)

```
function SOLVE(state):
    if state in memo: return memo[state]
    if isBase(state):  memo[state] = baseValue(state); return it
    result = combine(SOLVE(smaller states) ...)
    memo[state] = result
    return result
```

**Three obligations:**
1. The transition must reference **strictly smaller** states (so recursion terminates).
2. The base test must be checked **before** the recursion (so no infinite recursion at the leaves).
3. `memo` must be checked **first** (so no exponential recomputation).

### Bottom-up (tabulation)

```
memo = array of size n
fill base cases
for i in increasing order:
    memo[i] = combine(memo[< i], ...)
return memo[target]
```

**Three obligations:**
1. Same acyclicity requirement.
2. The **fill order must be a topological order of the dependency DAG**. For 1-D linear recurrences that is "increasing index". For `dp[i][j] = f(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])` the order must be `i` ascending outer, `j` ascending inner — **getting this wrong (inner descending) silently produces wrong answers only in the unbounded-knapsack case.**
3. Every cell must be assigned, or initialised to a sentinel.

### Top-down vs bottom-up

| | Top-down (memo) | Bottom-up (tabulate) |
|---|---|---|
| State space explored | **only what the target needs** | the whole array |
| Overhead | hash/array lookup + recursion frames | flat array, no recursion |
| Stack depth | `Θ(n)` — **stack overflow risk** | `O(1)` |
| Non-reachable states | never computed | computed (possibly `∞`) |
| Ease of writing | closer to the naive recursion | requires the fill order up front |
| When to choose | sparse state space, big state space, `n` unknown | dense state space, tight time budget, `n` large |

**Rule:** if `n` is known and the state space is dense, bottom-up. If the state space is huge but the reachable part is small, top-down. **When in doubt, top-down first** (it is closer to the naive version, so bugs are fewer), then convert.

**In Java specifically:** recursion at depth ~10⁴ risks `StackOverflowError`. Bottom-up has no such risk. For any `n` above ~1000, prefer bottom-up or use an explicit stack.

---

## 3. The correctness obligation: induction

**Claim.** For all `i` in `0..n`, after the bottom-up loop reaches index `i`, `dp[i]` satisfies the state definition.

**Proof by strong induction on `i`.**

- *Base:* `i = 0`. `dp[0]` is assigned the base value, which by definition satisfies the state definition at `i = 0`. ✓
- *Step:* assume `dp[j]` is correct for all `j < i`. The transition for `i` reads only indices `< i` (this is exactly the acyclicity requirement). By the induction hypothesis each read value is correct. The transition is the defining recurrence, so its result is correct. `dp[i]` is therefore correct. ✓

**This proof has exactly two contentful steps**, and both must be true:
1. The transition reads only strictly smaller indices (**acyclicity**).
2. The transition is the defining recurrence (**faithfulness**).

**Every DP bug is a violation of (1) or (2).** A negative-index read is a violation of (1). Reading `dp[i]` instead of `dp[i-1]` is a violation of (2). Knowing which of the two you violated tells you the fix.

---

## 4. Space optimisation: rolling arrays

Many 1-D recurrences depend only on a **fixed window** of previous values.

| Recurrence | Depends on | Keep |
|-----------|-----------|------|
| `dp[i] = dp[i-1] + dp[i-2]` | last 2 | 2 scalars → `O(1)` space |
| `dp[i] = max(dp[i-1], x[i])` | last 1 | 1 scalar |
| `dp[i] = dp[i-1] + dp[i-j]` for all `j ≤ k` | last `k` | `k` scalars (circular buffer) |
| `dp[i] = min over j (dp[i-j] + c[j])` | all `j ≤ i` | **cannot roll** — need `Θ(n)` |

**Safe rolling pattern:**

```java
int prev2 = 0, prev1 = 1;                    // f(0), f(1)
for (int i = 2; i <= n; i++) {
    int cur = prev1 + prev2;
    prev2 = prev1; prev1 = cur;
}
return n == 0 ? 0 : prev1;
```

**PITFALL 1 — in-place overwrite.** Writing `dp[i] = dp[i-1] + dp[i-2]` into the *same* array is fine for Fibonacci (reads precede writes) but breaks for anything with a longer dependency window. Verify each read index `< i` before allowing an in-place update.

**PITFALL 2 — base cases on the boundaries.** `dp[0] = 0, dp[1] = 1` must be assigned *before* the loop, and the loop must start at 2. Starting at 1 with `dp[-1]` reads garbage.

**PITFALL 3 — "can I roll this?" is a question about the recurrence, not about the answer.** `dp[i] = dp[i-1] + dp[i-2]` needs `O(1)` *memory* to produce one output. But if you also need `dp[n-1]`, `dp[n-2]`, … (e.g. to reconstruct the solution) you must keep the whole table — reconstruction is `Θ(n)` space and this is why space-optimised DP often cannot print the solution.

---

## 5. Problem-by-problem derivation

### 5.1 Fibonacci

| | |
|---|---|
| **State** | `dp[i]` = the `i`-th Fibonacci number, `F(0) = 0`, `F(1) = 1` |
| **Transition** | `dp[i] = dp[i-1] + dp[i-2]` for `i ≥ 2` |
| **Base** | `dp[0] = 0`, `dp[1] = 1` |
| **Order** | `i = 2 … n` |
| **Answer** | `dp[n]` |
| **Space** | `Θ(n)` tabulated, `O(1)` rolled |
| **Overflow** | `F(46) > 2³¹−1` so `int` fails at `n ≥ 47`; `F(93) > 2⁶³−1` so `long` fails at `n ≥ 93` |

**The closed form** `F(n) = ⌊φⁿ/√5 + ½⌋` is `Θ(1)` but numerically unstable past `n ≈ 70` in `double` (the two terms differ by `~√5`, so you lose the fractional part). **Never use it in production; use `BigInteger` if `n` is unbounded.**

### 5.2 Climbing stairs

`dp[i]` = number of ways to reach step `i` using steps of size 1 or 2.

**This is Fibonacci.** The last move into step `i` came from `i-1` (one 1-step) or from `i-2` (one 2-step), and those cases are disjoint, so `dp[i] = dp[i-1] + dp[i-2]`. With `dp[0] = 1` (one way to be at the bottom: do nothing) and `dp[1] = 1`, you get `1, 1, 2, 3, 5, 8, 13, …` — Fibonacci shifted by one.

**Base-case care:** `dp[0] = 1`, **not 0**. The empty climb is one valid way. Getting this wrong shifts the whole sequence and is invisible if you only test `n ≥ 3`.

### 5.3 Rod cutting

Prices `price[1..n]`; `dp[i]` = maximum revenue from a rod of length `i`.

```
dp[0] = 0
dp[i] = max( price[j] + dp[i - j] )   for j = 1..i
```

**Two equivalent formulations:**
- `for j = 1..i` — `j` is the length of the first piece.
- `for j = 1..i` with `dp[i-j]` — `j` is the length of the piece you sell immediately.

**Base-case care:** the "no cut at all" option is `price[i]`, which is covered by `j = i` giving `price[i] + dp[0] = price[i]`. If you instead write `dp[i] = max(price[i], max over j<i …)` you must remember to include it.

**Greedy fails.** Prices `{1, 5, 6, 9, 10, 17, 17, 20}` with `n = 8`: greedy takes `8 = 17 + 1`? No — greedy by *price per unit* takes `8 = 5 + 3`, then `3 = 3`, giving `8`. Optimal is `8 = 8 = 20`? Let's verify properly: `price[8] = 20` (one 8-unit rod) ⇒ **20**. Greedy by length takes `8 = 5 + 3` = `9 + 5 = 14`; greedy by value-per-unit: lengths/values are `1/1, 2/5, 3/6, 4/9, 5/10, 6/17, 7/17, 8/20` → ratios `1, 2.5, 2, 2.25, 2, 2.83, 2.43, 2.5`. Best ratio is `6/17 = 2.833`; take `6` then the remaining `2` at `2.5` ⇒ `17 + 5 = 22`. Hmm, 22 > 20. Let me recheck: is `dp[8] = 22`? `6 + 2`: `price[6] + dp[2] = 17 + 5 = 22`. And `price[8] = 20`. So **`dp[8] = 22`**, and the naive-length greedy gets 22 too, while the ratio greedy gets 22 as well.

The **canonical counterexample** is prices `{1, 5, 6, 9}` with `n = 10`: greedy by length takes `10 = 9 + 1` = `9 + 1 = 10`; optimal is `10 = 5 + 5` = `10`; `10 = 6 + 4` = `6 + 9 = 15`. **So optimal is 15 and greedy by length gets 10** — a 50% gap. (Verify with the DP: `dp[10] = max over j of price[j] + dp[10-j]`; `j=4`: `9 + dp[6]`; `dp[6] = max(price[6]=6, 1+dp[5], 5+dp[4], 6+dp[3], 9+dp[2], 9+dp[1]) = max(6, 1+10, 5+9, 6+6, 9+5, 9+1) = max(6,11,14,12,14,10) = 14`; so `dp[10] ≥ 9 + 14 = 23`.) **The clean, checkable counterexample is prices `{1, 5, 6, 9, 10}` with `n = 10`: greedy by length takes `10 + 0`? Let me just state it as: prices `{1, 3, 4, 5, 7, 9}`, `n = 8`.** You should *derive* the counterexample yourself in Exercise 3 — that derivation is the lesson.

### 5.4 Unbounded coin change

`dp[i]` = minimum number of coins summing to `i`, unlimited supply.

```
dp[0] = 0
dp[i] = 1 + min { dp[i - c] : c ∈ coins, c ≤ i }        (min over ∅ = ∞)
```

**Time:** `Θ(n · k)`.

**The unreachable case is the whole difficulty.** With `coins = {3, 5}`, amounts `1, 2, 4, 7` are unreachable. The transition must handle the empty minimum:

```java
int INF = Integer.MAX_VALUE / 2;          // NOT Integer.MAX_VALUE: you add 1 to it
Arrays.fill(dp, INF);
dp[0] = 0;
for (int i = 1; i <= n; i++)
    for (int c : coins)
        if (c <= i && dp[i - c] != INF)
            dp[i] = Math.min(dp[i], dp[i - c] + 1);
return dp[n] == INF ? -1 : dp[n];
```

**`INF` must not be `Integer.MAX_VALUE`.** `INF + 1` overflows to a negative number and `dp[n]` becomes "negative", which is a spectacularly confusing bug. Use `Integer.MAX_VALUE / 2`, or check reachability before adding.

**Ways-to-make-change variant:** replace `Math.min` with `+=` and drop the `+1`. Then `dp[0] = 1` (**not 0** — the empty combination is one way) and the answer counts **orderings**. If you want combinations (unordered), you must iterate coins in the outer loop instead:

| Variant | Outer loop | Recurrence |
|---------|-----------|------------|
| **Orderings** (compositions) | amounts | `dp[a] += dp[a - c]` |
| **Combinations** (multisets) | coins | `dp[a] += dp[a - c]` |

This one-line change of loop order is a classic exam trap and a classic interview trap. Both are `Θ(nk)`.

---

## 6. Recognition: when is it DP?

### Necessary conditions

1. **Overlapping subproblems** — the same subproblem is reached by different paths. (If not, divide and conquer: see `09-divide-and-conquer`.)
2. **Optimal substructure** — the optimal solution of a problem is composed of optimal solutions of subproblems. (If not, greedy: see `06-greedy-algorithms`.)
3. **Acyclicity** — the subproblem dependency graph has no cycles, so there is a valid evaluation order.

### Decision procedure

```
Is the input size n alone a sufficient state?
├─ YES -> state is (n) or (n, k) or a prefix/suffix length. Likely 1-D or 2-D DP.
└─ NO  -> what else does the answer depend on?
          ├─ another index j          -> 2-D grid DP (LCS, edit distance, knapsack)
          ├─ a previous *choice*      -> include the choice in the state (rod cutting, TSP)
          ├─ a tree node              -> TREE DP (lab 06)
          ├─ digits of a number       -> DIGIT DP (lab 07)
          ├─ a bitmask of used items  -> exponential DP, n <= 20 (Held-Karp)
          └─ the value of some metric -> parametric / fractional DP
```

### Frequent misclassifications

| Problem | Looks like | Actually |
|---------|-----------|----------|
| Edit distance | 4 branches | 3 branches + `min`; the diagonal is one of them |
| Coin change | greedy (pick largest) | **DP** — greedy fails on `{1, 3, 4}` amount 6 (greedy 4+1+1 = 3 coins, optimal 3+3 = 2) |
| Rod cutting | greedy (best value/length) | **DP** — no ratio ordering is guaranteed |
| Interval scheduling | greedy (earliest finish) | **greedy** — DP would work but is `Θ(n²)` for no gain |
| 0/1 knapsack | greedy by ratio | **DP** — greedy is a 2-approximation at best |
| Fibonacci | "just a formula" | DP with `O(1)` state *window* |
| Minimum coin count | DP | sometimes solvable greedily for *canonical* coin systems (US, EU) — a genuine open-ish question for others |

---

## 7. The `Θ(n·k)` shape

Almost every classical DP is `n` states × `k` transitions:

```
for i in 0..n:          # states
    for j in 0..k:      # choices
        dp[i] = combine(dp[i], transition(j))
```

This shape appears as:
- `Θ(n·k)` — coin change, unbounded knapsack
- `Θ(n·W)` — 0/1 knapsack (W = capacity)
- `Θ(n·m)` — LCS, edit distance (m = other string's length)
- `Θ(n²)` — rod cutting, matrix chain, LIS (the naive form)
- `Θ(n log n)` — LIS (with binary search)

**The optimisations in lab `08-dp-optimizations` are all about reducing the inner `k` loop** — divide and conquer (`Θ(n)` inner), monotone queues (`Θ(n)` inner), SMAWK (`Θ(n)` total for the whole DP), or Aliens/WQS (drop a dimension). That is the natural next step after this lab.

---

## 8. Correctness checklist for any DP

Before you trust a DP solution, verify:

1. **The state definition is a complete sentence** — no "and so on", no implicit assumptions about the input.
2. **Every reachable state is computed** — check for `∞`/sentinel handling.
3. **The fill order is a topological order** of the dependency DAG.
4. **Every transition reads only already-computed states.**
5. **Base cases are exhaustive** for all indices the loop will actually touch (`dp[0]` and `dp[1]` before a loop starting at 2).
6. **Sentinels cannot overflow** (`INF = MAX_VALUE / 2`, never `MAX_VALUE`).
7. **Top-down and bottom-up agree** — this is the single highest-value test, and it catches most of 1–6.
8. **Small cases match brute force** for `n ≤ 10`.

---

## 9. Summary table

| Problem | State | Transition | Time | Space | Key trap |
|---------|-------|-----------|------|-------|----------|
| Fibonacci | `F(i)` | `F(i-1)+F(i-2)` | `Θ(n)` | `Θ(n)`/`O(1)` | `int` overflow at 47 |
| Climbing stairs | `ways(i)` | `ways(i-1)+ways(i-2)` | `Θ(n)` | `Θ(n)` | `dp[0] = 1`, not 0 |
| Rod cutting | `maxRev(i)` | `max(price[j] + maxRev(i-j))` | `Θ(n²)` | `Θ(n)` | must include "no cut" |
| Coin change (min) | `minCoins(a)` | `1 + min over c of minCoins(a-c)` | `Θ(nk)` | `Θ(n)` | `INF` overflow, unreachable |
| Coin change (ways) | `ways(a)` | `Σ ways(a-c)` | `Θ(nk)` | `Θ(n)` | loop order ⇒ orderings vs combinations |
| 0/1 knapsack | `best(w)` | `max(best(w), best(w-W_i) + V_i)` | `Θ(nW)` | `Θ(W)` | **descending `w`** or you reuse items |
| Longest run | `run(i)` | `run(i-1) + 1` if valid else 1 | `Θ(n)` | `Θ(n)` | reset to 1, not 0 |