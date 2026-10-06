# Quiz — Knapsack Variants

15 questions. Each key gives the reason.

---

## Q1
Explain why the loop direction in 0/1 knapsack is *part of the specification*.

<details><summary>Answer</summary>

The recurrence is `Dᵢ[w] = max(Dᵢ₋₁[w], Dᵢ₋₁[w−wᵢ] + vᵢ)` — both terms must come from the **previous** item's row.

- **Descending** `w`: `w − wᵢ < w` has not yet been updated this pass ⇒ both reads are from `Dᵢ₋₁`. ✔ 0/1.
- **Ascending** `w`: `w − wᵢ` was already updated ⇒ the recurrence becomes `max(Dᵢ₋₁[w], Dᵢ[w−wᵢ] + vᵢ)`, which is exactly the **unbounded** recurrence.

**Test that catches it:** `items = [(1,3)], W = 10` → `3` (0/1) vs `30` (unbounded). A suite without such a case cannot detect the swap.
</details>

## Q2
`dp[w] = 0` initialisation: correct for "at most", wrong for "exactly". Why?

<details><summary>Answer</summary>

- **At most `w`:** the empty set is always feasible with value 0 for *every* `w`, so `0` is the correct initial value.
- **Exactly `w`:** `w` is only reachable if some subset sums to `w`. `0` claims every weight is reachable with value 0, so `items = [(2,3)], W = 3` returns `0` instead of `-1`.

Use `-∞` (actually `MAX_VALUE/2`, with a reachability check) for the "exactly" convention. And `NEG = Integer.MIN_VALUE` **overflows** when you add `vᵢ` to it.
</details>

## Q3
State the binary-splitting decomposition and prove it covers every count.

<details><summary>Answer</summary>

**Decomposition:** `c = 13 → {1, 2, 4, 6}`, generally `{1, 2, 4, …, 2^{m−1}, c − (2^m − 1)}` with `2^m ≤ c < 2^{m+1}`.

**Proof of completeness.** Powers `1..2^{m−1}` represent every `k ∈ [0, 2^m − 1]`. For `k ∈ [2^m, c]`: `k − r ≥ 2^m − r > 0` and `k − r ≤ c − r = 2^m − 1`, so `k − r` is representable by the powers and adding the `r`-bundle gives `k`. ∎

`⌈log₂(c+1)⌉` bundles. **The requirement is that every count is a subset sum — a partition is not enough** (`{4,4,4}` is a partition but not a complete sequence).
</details>

## Q4
Derive the monotone-queue transition for bounded knapsack.

<details><summary>Answer</summary>

```
newDp[w] = max over k in [0, c] of ( dp[w − k·p] + k·q )
```

Group by `r = w mod p`, write `w = r + t·p`, substitute `s = t − k`:

```
newDp[r + t·p] = t·q + max over s in [t−c, t] of ( dp[r + s·p] − s·q )
```

Define `X(s) = dp[r + s·p] − s·q`. **A sliding-window maximum of width `c+1`**, maintained by a monotone deque in `Θ(1)` amortised per state ⇒ `Θ(W)` per item type, `Θ(nW)` total, **independent of `c`**.

Window `[t−c, t]` includes both endpoints — using `< t−c` for expiry gives "at most `c−1`".
</details>

## Q5
Why is fractional knapsack solvable greedily but 0/1 is not?

<details><summary>Answer</summary>

Fractional knapsack is an LP whose vertices have at most one fractional variable; the greedy solution has exactly that form, and the exchange argument (move `δ` weight from a lower-ratio item to a higher-ratio one, gaining `δ·wₐ·(vₐ/wₐ − v_b/w_b) > 0`) proves optimality.

0/1 forbids splitting, so that exchange is unavailable, and the problem is **weakly NP-complete**. Greedy by ratio gives a `2`-approximation, tightened to **`11/9`** by Martello–Toth.
</details>

## Q6
State the `11/9` bound and why it matters in practice.

<details><summary>Answer</summary>

Greedy-by-ratio on 0/1 knapsack satisfies `greedy ≥ (11/9)·OPT − (6/9)·v_max`, hence `greedy ≥ (11/9)·OPT` whenever `OPT ≥ 6·v_max`. The bound is **tight**.

**Why it matters:** `Θ(n log n)` with a `1.2222` guarantee beats a `Θ(nW)` exact answer whenever `W` makes the DP infeasible. That is an engineering trade, not a theoretical nicety — and it is the honest answer for large portfolio/budget problems.
</details>

## Q7
The bitset subset sum: complexity, loop order, and the shift pitfall.

<details><summary>Answer</summary>

- **Complexity:** `Θ(nW/64)` word operations, `Θ(W/8)` bytes — a **`64×`** win on both.
- **Loop order:** **descending**, or the source word already contains this item's contribution and you get unbounded subset sum. Test: `a = [5,5], W = 10` must be `false`.
- **Pitfall:** `bits[i−wordShift−1] >>> (64 − bitShift)` with `bitShift == 0` becomes `>>> 0` in Java (shift counts are masked to 5/6 bits), OR-ing in the whole previous word. **Guard with `if (bitShift != 0)`** — and test with a weight of exactly 64.
</details>

## Q8
`Θ(nW)` is infeasible. What are the alternatives and their triggers?

<details><summary>Answer</summary>

| alternative | time | choose when |
|---|---|---|
| DP by profit `P` | `Θ(nP)` | `P ≪ W` |
| DP by weight capped at `Σwᵢ` | `Θ(n·min(W, Σwᵢ))` | few, heavy items |
| Meet-in-the-middle | `Θ(n 2^{n/2})` | `n ≤ 44`, huge `W`; wins when `2^{n/2} < W` |
| Branch and bound | `O(2ⁿ)` | `n ~ 100`, ratio-friendly instances |
| Greedy by ratio | `Θ(n log n)` | anytime; `11/9` guarantee |

**MITM threshold:** `2^{n/2} < W` ⟺ `n < 2 log₂ W`. For `W = 10⁹` that is `n < 60`.
</details>

## Q9
Multi-dimensional knapsack: why is it not the answer for real allocation problems?

<details><summary>Answer</summary>

`Θ(n · Π Wᵢ)` states. `d = 4`, `Wᵢ = 100` gives `10⁸` states and `10¹⁰` time for `n = 100`. The dimension-count curse makes `d ≥ 3` impractical.

**The real tools** are LP relaxation + branch and bound, or a maintained **Pareto frontier** (`Θ(n·|P|)`, with `|P|` small in practice). Report the frontier size before choosing — that number decides whether it is viable.
</details>

## Q10
Group knapsack. What is the loop nesting, and what goes wrong if you get it wrong?

<details><summary>Answer</summary>

```java
for (group : groups)
    for (int w = W; w >= 0; w--)
        for (item : group)
            dp[w] = max(dp[w], dp[w - item.weight] + item.value);
```

The **group loop must be outermost** so at most one item per group can be taken. Putting it inside the weight loop lets `dp[w - item.weight]` already include an item from the same group ⇒ two items from one group are selected, violating the constraint **silently**.
</details>

## Q11
Fractional greedy: why cross-multiply in the comparator instead of dividing?

<details><summary>Answer</summary>

`(double) vᵢ / wᵢ` rounds, so nearly-equal ratios can be mis-ordered. Cross-multiplication compares `vᵢ·w_j` vs `v_j·wᵢ` as `long`s — **exact** provided `v, w ≤ 10⁹` (products `≤ 10¹⁸ < 2⁶³`).

Mis-ordering matters when you then convert the fractional solution to a 0/1 one: the greedy order is part of the `11/9` guarantee's proof.
</details>

## Q12
Why can you not reconstruct the answer from a `Θ(W)` rolled DP, and what do you do instead?

<details><summary>Answer</summary>

Backtracking needs to know, at each weight, which item caused the improvement — which a rolled array discarded. This is the same trade as lab `01`.

**Options:**
1. `Θ(nW)` `boolean[][]` — simple, memory-hungry.
2. **`long[]` bitset per item** (`n × ⌈W/64⌉ × 8` bytes) — 8× smaller than `int[][]`, 64× smaller than a naive `boolean[][]`.
3. Recompute the decision backwards by re-running the DP from item `i−1` — `Θ(nW)` time, `Θ(W)` space, one extra pass per item.
4. Greedy + local search, and give up exactness.

Option 2 is what real implementations use.
</details>

## Q13
DP by value `P`. State the recurrence and the loop order, and say when it wins.

<details><summary>Answer</summary>

```
dp[p] = minimum weight to achieve value AT LEAST p
init:  dp[0] = 0, dp[p] = +∞
loop:  for p = P down to v[i]:   dp[p] = min(dp[p], dp[p − v[i]] + w[i])
answer: max{ p : dp[p] ≤ W }
```

`Θ(nP)` time, `Θ(P)` space. **Descending** `p`, same 0/1 reason.

**Wins when `P ≪ W`** — small monetary budgets, small counts. Note the roles are swapped: this is a *minimum cost for a given benefit*, the dual of the original.
</details>

## Q14
An `nW` DP for `n = 10⁵`, `W = 10¹²`. What do you ship?

<details><summary>Answer</summary>

Not the DP. Not meet-in-the-middle (`2^{5·10⁴}` — absurd).

**Ship:** fractional greedy by ratio (`Θ(n log n)`) **plus local search** (add one, drop one, swap one), report the fractional and the realised value, and **state the guarantee** (`11/9` for pure greedy; measure the realised gap for greedy+local-search and report it).

**Then be explicit with stakeholders:** the problem is weakly NP-hard, the answer is approximate, here is the error bound, here is the runtime. Silently shipping an exact-looking number from a heuristic is the failure mode to avoid.
</details>

## Q15
State the one meta-lesson from the whole lab.

<details><summary>Answer</summary>

**The framing word is the complexity class.** "At most once" vs "as many as you like" vs "divisible" changes the algorithm, the complexity, and the theory — from `Θ(n log n)` greedy (fractional) through `Θ(nW)` DP (0/1 and unbounded) to weak NP-completeness and `Θ(n 2^{n/2})` MITM (small `n`, huge `W`).

And when the state is boolean, **pack 64 states per machine word** — the bitset subset sum's `Θ(nW/64)` is the same lesson as lab `08`: representation, not cleverness, buys the constant factor.
</details>