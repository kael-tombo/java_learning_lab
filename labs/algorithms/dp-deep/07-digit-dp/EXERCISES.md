# EXERCISES — Digit DP

## Level 1 — Warm Up

### 1.1 Count digits
Implement `countDigits(n)` returning the number of decimal digits of `n`, for `n = 0`
(answer `1`) and `n ≥ 1`. Do not use string conversion.

**Trace:** `countDigits(0)=1`, `countDigits(7)=1`, `countDigits(10)=2`, `countDigits(10^18)=19`.

### 1.2 Count numbers ≤ N with a given digit sum
`countByDigitSum(N, S)` — count `x ∈ [0, N]` with digit sum `S`.
Write the naive `Θ(d·S·10)` DP first, then the `N = 10^k − 1` closed form
`coeff of x^S in (1+x+…+x^9)^k`, and check they agree for `N = 99`.

**Trace (`N = 25, S = 7`):** valid numbers are `7, 16, 25` → `3`.

### 1.3 Total digit sum over `[0, N]`
`sumOfDigitSums(N)`. Verify against the closed form `45·k·10^(k−1)` for `N = 99`
(answer `45·2·10 = 900`).

## Level 2 — Core DP

### 2.1 Count ≤ N divisible by `m`
`countDivisible(N, m)`. State `(pos, rem, tight)`, transition `rem' = (10·rem + x) % m`.
Then convert to the precomputed `ways[len][r]` version and show the speedup for `m = 7`,
`q = 10^4` queries.

**Trace (`N = 20, m = 5`):** multiples are `0, 5, 10, 15, 20` → `5` (note `0` counts).

### 2.2 Sum of numbers ≤ N divisible by `m`
Add the value-carrying accumulator. `rem' = (10·rem + x) % m`, and the prefix value
updates as `10·p + x`. **Pitfall to hit:** if you accumulate the *full* number at the leaf you
need to remember `p` across states, which is `Θ(d·m·10^d)` memory. Carry it in a parallel array.

### 2.3 Count ≤ N with no two adjacent equal digits
State `(pos, lastDigit, tight, started)`. `K = 10`.

**Trace (`N = 12`):** valid = `0,1,2,3,…,9,10,12` — `11` is excluded. Answer `12`.

### 2.4 Count ≤ N avoiding a specific digit `x`
Two variants:
- **Position-independent** (e.g. divisible by `3` *and* no `7`): drop `started`, `Θ(d·10·m)`.
- **Leading-zero sensitive** (e.g. no digit equals the *first* digit): needs `started`.

**Edge case:** `x = 0` — is a leading zero "a 0"? Decide and document.

### 2.5 Count palindromes ≤ N
**Trace (`N = 1221`):** 1-digit `0..9` = 10; 2-digit `11,22,…,99` = 9; 3-digit `101,…,999` = 90;
4-digit ≤ 1221: `1001,1111,1221` = 3. Total `10 + 9 + 90 + 3 = 112`.
Compare with the closed form for `N = 9999`: `9·10^(4/2 − 1) = 90` for 4-digit, plus
`10 + 9 + 90 = 109` → `199`.

## Level 3 — Extended State

### 3.1 Count ≤ N with strictly increasing digits
State `(pos, mask)` where `mask` is a 10-bit set of used digits. `K = 2^10 = 1024`.
**Observation:** increasing digits ⇒ the number has no repeated digits and `mask` is exactly the
leading-ones prefix `2^k − 1`, so you only ever need `11` states, not `1024`. Verify by
enumerating states.

**Trace (`N = 500`):** increasing-digit numbers ≤ 500: 1-digit `1..9` (9), 2-digit `12,13,…,89`
(36), 3-digit `123,124,…,789` (84). Total `129`.

### 3.2 Count ≤ N whose digits are in strictly decreasing order
Same state, mirrored. Note the answer is `2^10 − 1` over all lengths.

### 3.3 Count ≤ N with digit sum `S` **and** divisible by `m`
Two-dimensional state `(pos, sum, rem)`. `K = (S+1)·m`.
**Trace (`N = 999, S = 18, m = 9`):** digit sum 18 forces divisibility by 9, so `rem` is
redundant — answer = coefficient of `x^18` in `(1+x+…+x^9)^3` = `10` (the `999`/`909`/… family).
Use this to discover that redundant state can be *removed*, not just computed.

### 3.4 Count ≤ N with no `11` as a substring
State `(pos, lastWasOne, tight, started)`, `K = 2`. Or use the Fibonacci closed form for
`N = 10^k − 1`.

### 3.5 Count ≤ N where `x mod m ∈ S` (a set)
State `(pos, rem)`. **Trace (`N = 49, m = 5, S = {1,3}`):** `1,3,6,8,11,13,16,18,21,23,26,28,
31,33,36,38,41,43,46,48` → `20`.

## Level 4 — Summing and Optimising

### 4.1 Sum of squares over a digit-DP set
Carry three arrays: `ways`, `sums`, `sumsq`. Since
`(10p + x)^2 = 100p² + 20px + x²`, the update is

```
sumsq' += 100·sumsq + 20·x·sums + x²·ways
sums'  += 10·sums + x·ways
```

**Verify** for `N = 20, m = 5`: valid `0,5,10,15,20`, sum of squares `0+25+100+225+400 = 750`.

### 4.2 Precomputation
Implement `ways[len][r]` for `m` up to `200`, `len` up to `19`. Show that a query for `N` is
`Θ(d·10)` and total for `q` queries is `Θ(d·m·10 + q·d·10)`.
**Measure:** `m = 200`, `q = 10^5` — precompute once vs per-query DP.

### 4.3 Minimum / maximum number with digit sum `S`
Greedy, not DP: to *minimise* a number with digit sum `S` over `d` digits, place digits
right-to-left, each as large as possible (9, 9, …, remainder) — i.e. push mass to the *right*.
**Trace (`d = 4, S = 20`):** `2,9,9,0`? Check: greedy from the right gives `0,9,9,2` →
number `2990`; the minimum is `2990`. Compare to the DP.

## Level 5 — Edge Cases (must all pass)

| Input | Expected | Trap |
|-------|----------|------|
| `N = 0` | 1 number (`0`) | `d` must be ≥ 1, not 0 |
| `N = 0, S = 0` | 1 | is `0`'s digit sum `0` or "empty"? pick and document |
| `N = 9, S = 0` | 1 (`0` only) | leading zeros must not contribute |
| `N = 9, S = 9` | 1 (`9`) | |
| `N = 10^18` | 19 digits | `long` boundary; `10^19` overflows |
| `m = 1` | every number | `rem` always 0 |
| `N = 10^k − 1` | closed form applies | |
| digit-sum target `S > 9d` | 0 | prune the state |
| `x = 0` avoidance | depends on `started` semantics | |

## Level 6 — Stretch

6.1 **Range `[a, b]`**: `count(b) − count(a − 1)`; handle `a = 0` without underflow.
6.2 **`N` as a 10^5-digit string**: the DP is `Θ(d·K)` — argue why the `10` factor and the
      `K` table must both be optimised, and how to reconstruct the answer from the table.
6.3 **Two-sided bound** `x mod m ∈ [lo, hi]` with `lo, hi` also input — `K = m`, but the
      transition is unchanged.
6.4 **Cross-validate**: for every `N ≤ 5000`, compare the DP against a brute-force loop.
      Any mismatch is a bug in your `tight` or `started` logic.