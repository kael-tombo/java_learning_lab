# QUIZ — Digit DP

1. What are the two flags that almost every digit DP needs, and what does each guard against?
2. Give the exact time complexity of counting numbers `≤ N` with digit sum `= S`, in terms of `d = digits(N)` and `S`.
3. Why does `tight` update as `tight' = tight && (x == n[pos])` rather than just `x == n[pos]`?
4. When can you drop the `started` flag entirely?
5. What is the trap when the forbidden digit is `0`?
6. State the closed form for the total digit sum over `[0, 10^k − 1]` and the average.
7. How many `d`-digit palindromes are there in `[0, 10^d − 1]`?
8. Give the recurrence transition for counting numbers divisible by `m`.
9. What does the `ways[len][r]` precomputation buy, and what is its cost?
10. How do you convert a counting DP into a summing DP?
11. For "strictly increasing digits", why is the subset-mask state overkill and how many states do you actually need?
12. What is the extra state for "no two adjacent equal digits", and its size?
13. Why does `(pos, sum, rem)` become redundant when `S ≡ 0 (mod 9)`?
14. Counting `x ≤ N` with digit sum `S` where `S > 9d`: what's the answer and why is pruning safe?
15. Give a concrete counter-example where dropping `tight` produces a wrong answer.

---

## Answers

1. **`tight`** guards the upper bound `≤ N` (it stops the scan from writing a prefix larger than
   `N`'s). **`started`** guards leading zeros (it distinguishes the number `7` from the string
   `007`, which matters for digit sum, first-digit rules, and adjacency rules).
2. `Θ(d · S · 10)` time with rolling arrays, `Θ(S)` space. The three factors are: `d` positions,
   `S + 1` reachable partial sums, `10` digit choices per state. Memoised (not rolled) it's
   `Θ(d · S)` space.
3. Because once the prefix is strictly smaller than `N`'s it can never become equal again, no
   matter what digits follow. So `tight` is *absorbing at 0*: `0 && anything = 0`. Writing
   `x == n[pos]` alone would re-tighten the flag and wrongly cut off valid smaller completions.
   Counter-example: `N = 150`, writing `1,0,…` — the second digit `0 < 5` so the prefix `10` is
   already smaller, yet `0 == n[1]` would keep `tight = 1` and forbid a `9` in the last position.
4. When the predicate is invariant under leading zeros — divisibility by `m`, "contains digit 5",
   "does not contain digit 3", digit frequency counts. Since `007 ≡ 7 (mod m)`, the padding
   cannot change the truth value. It halves the state space (drops `K` by 2).
5. Two semantics are defensible: (a) leading zeros are *not* the digit `0`, so `1007` is
   "allowed" for "no zeros" — needs `started`; (b) the padded representation `0007` contains
   zeros, so nothing qualifies — drop `started`. You must pick one and document it, because
   they disagree exactly on numbers shorter than `N`.
6. Total `= 45 · k · 10^(k−1)`; average `= 4.5 · k`. Derivation: each of the `k` positions is
   uniformly distributed over `0..9` with mean `4.5`, so the mean digit sum is `4.5k`, and there
   are `10^k` numbers.
7. `9 · 10^(⌈d/2⌉ − 1)`. A palindrome is determined by its first `⌈d/2⌉` digits; the leading one
   is nonzero (`9` choices) and the rest are free (`10` each). `d`-digit palindromes are
   therefore `9 · 10^(⌈d/2⌉−1)`, and you sum that over `d = 1..k` to cover `[0, 10^k − 1]`.
8. `dp[pos+1][(10·r + x) mod m][t'] += dp[pos][r][t]` for each digit `x` in the legal range,
   with `t' = t && (x == n[pos])` and `s'` updated per the extra state. Remainder starts at 0
   and the answer is `dp[0][0][1]`.
9. The remainder update `r' = (10r + x) mod m` depends only on `r` and `x`, never on `pos`. So
   `ways[len][r]` can be built once for all `len ≤ d` at `Θ(d · m · 10)` and reused: each query
   then costs only `Θ(d · 10)`. For `q` queries this replaces `Θ(q · d · m · 10)` with
   `Θ(d·m·10 + q·d·10)`.
10. Carry a second accumulator `sums` alongside `ways` and use the value update `p → 10p + x`:
    `sums' += 10·sums + x·ways`, while `ways' += ways`. Same transition shape, one extra array.
    The reason it works: `Σ (10p_i + x_i) = 10·Σ p_i + x·(count)`.
11. With strictly increasing digits, once a digit appears it can never repeat, and the used set
    is always a prefix of `{1,…,9}` in sorted order (plus possibly a `0` that must be first).
    So the mask is determined by the *count* of digits used, not by which ones — `11` reachable
    states instead of `1024`.
12. `lastDigit`, size `10`. The transition is `x != lastDigit`. Note `lastDigit` must be
    initialised to a sentinel (e.g. `10`) when `started == 0`, or the first digit is wrongly
    rejected if you forbid `0`.
13. Because `x ≡ digitSum(x) (mod 9)` for every `x`. So if the digit sum is forced to a
    multiple of 9, then `x mod 9 = 0` for free, and the `mod m` remainder is determined by the
    sum only when `m` divides 9. Carrying `rem` anyway costs `(S+1)·m` instead of `S+1`.
14. Answer `0`. A `d`-digit number's digit sum is at most `9d`, so no valid number exists. Pruning
    states with `s > S` is sound because `s` is nondecreasing along any path — digits are only
    ever added, so once `s` exceeds the target no continuation can come back under it.
15. `N = 20`, predicate "even last digit". With `tight` dropped you enumerate all 2-digit
    strings `00..99` and get `50`. Correct answer is `11` (`0,2,4,6,8,10,12,14,16,18,20`).
    `tight` is not an optimisation you can switch off — it defines the problem.