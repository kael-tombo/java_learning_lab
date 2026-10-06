# THEORY — Digit DP

## 1. The Shape of the Problem

Almost every digit-DP question is the same question wearing different clothes:

> Count (or sum, or minimise) the integers `x ∈ [0, N]` such that `predicate(x)` holds,
> where `predicate` is defined **digit by digit**.

The reason this is a DP and not a loop over `[0, N]` is that `predicate` is naturally a
function of the *decimal expansion* of `x`, read left to right. Brute force costs `Θ(N)`;
digit DP costs `Θ(d · K · 10)` where `d = digits(N) ≤ 19` and `K` is the size of the
"extra state" the predicate needs to remember.

## 2. The Two Mandatory Flags

### `tight` — the bound flag

Read `N` as a string `n[0..d)`. While scanning left to right we maintain `tight ∈ {0,1}`
meaning "the prefix I have written so far is character-for-character equal to `N`'s prefix".

- If `tight == 1`, the next digit may be anything in `[0, n[pos]]`.
- If `tight == 0`, the prefix is already strictly smaller, so the next digit is free: `[0,9]`.

After choosing digit `x`, the flag updates as `tight' = tight && (x == n[pos])`.

**Invariant (tight).** If `tight == 1` then the written prefix is exactly `N`'s prefix and is
`≤ N` lexicographically (equal). If `tight == 0` then the written prefix is strictly less
than `N`'s prefix. *Proof.* Induction on `pos`. Base `pos = 0`, empty prefix equals the empty
prefix of `N`, so `tight = 1`. Step: with `tight = 1`, `x ≤ n[pos]`; if `x < n[pos]` the new
prefix is strictly smaller (flag → 0) and no later digit can recover equality, so it stays 0
forever; if `x = n[pos]` it stays 1. With `tight = 0` any `x` is allowed and the prefix remains
strictly smaller. ∎

`tight` is what makes the DP *bound-aware*. Drop it and you are counting over all `d`-digit
strings — which happens to be the right thing for `[0, 10^d)`, i.e. `N = 10^d − 1`.

### `started` — the leading-zero flag

`007` and `7` are the same number, but they are different *strings*. Any predicate that is not
invariant under leading zeros (digit sum, "first digit is nonzero", "no two adjacent equal
digits") must know whether the number has started. Hence `started ∈ {0,1}`:

- `started == 0` and we pick digit `0` → still not started, digit contributes nothing.
- `started == 0` and we pick `x > 0` → `started` becomes 1, digit contributes `x`.
- `started == 1` → digit contributes `x`.

Leading zeros are *free* when the predicate is position-independent (e.g. divisibility by `m`,
since `007 ≡ 7 (mod m)`), so that case can drop the flag and halve the state space.

## 3. The Recurrence

For a **counting** DP with extra state variable `s` (digit sum so far, remainder mod `m`,
last digit, subset mask — whatever the predicate needs):

```
count(pos, s, tight, started)
  = Σ over x in [0, (tight ? n[pos] : 9)] of
      count(pos + 1, s', tight', started')
  with s' = f(s, x, started), base count(d, s, ...) = [s == target]
```

Memoised over `(pos, s, tight, started)` this is `Θ(d · K · 10)` time, `Θ(d · K)` space
(`K` = number of reachable `s` values). Iterated with rolling arrays it is `Θ(K)` space.

**Invariant (soundness + completeness).** `count(pos, s, tight, started)` equals the number of
length-`(d − pos)` digit completions of the current prefix that yield a valid full number with
aggregate `s`. *Soundness* holds because the digit range for `x` is exactly the set that keeps
the prefix `≤ N` (by the tight invariant). *Completeness* holds because the ranges for
distinct `x` are disjoint and their union is the full legal range, so every legal completion is
counted in exactly one summand. ∎

## 4. From Counting to Summing

To compute `Σ x` over the valid set instead of the count, carry a second accumulator. If the
written prefix has value `p`, extending it with digit `x` gives value `10p + x`. So:

```
ways[pos+1][s'][t']  += ways[pos][s][t]
sums[pos+1][s'][t']  += 10 * sums[pos][s][t] + x * ways[pos][s][t]
```

Both accumulators use the *same* transition. This is the single most useful trick in digit DP:
one extra array buys you "sum of all qualifying numbers", "sum of squares" (needs
`100p² + 20px + x²`, so carry `ways`, `sums`, `sumsq`), etc.

## 5. Divisibility: Precomputation Wins

Counting numbers `≤ N` divisible by `m` with the naive DP is `Θ(d · 10 · m)` *per query*. But
the remainder update `r' = (10r + x) mod m` depends only on `r` and `x` — **not on the
position**. So precompute once:

```
ways[len][r] = # of length-len digit strings (leading zeros allowed) with value ≡ r (mod m)
ways[0][0] = 1
ways[len+1][(10r + x) % m] += ways[len][r]   for all r, x
```

Cost `Θ(d · m · 10)` once; each subsequent query becomes `Θ(d · 10)`. For `q` queries this is
the difference between `Θ(q · d · m · 10)` and `Θ(d · m · 10 + q · d · 10)`.

## 6. Closed Forms — Always Check First

| Quantity | Closed form | Beats the DP by |
|----------|-------------|------------------|
| Sum of digit sums over `0..10^d − 1` | `45 · d · 10^(d−1)` | `Θ(1)` vs `Θ(d·s·10)` |
| Average digit sum over `0..10^d − 1` | `4.5 · d` | `Θ(1)` |
| Count of palindromes ≤ `N` (`d` digits) | `9 · 10^(⌈d/2⌉ − 1)` | `Θ(d)` vs `Θ(d·10)` |
| `d`-digit binary strings with no `11` | `F_{d+2}` (Fibonacci) | `Θ(d)` vs `Θ(d·10)` |
| Count of `k`-digit numbers with digit sum `s` | coefficient extraction from `(1+x+…+x^9)^k` | FFT |

For `N = 999…9` the digit DP degenerates to "all strings", which is exactly where these
closed forms apply. Recognising `N = 10^k − 1` is a free speedup of many orders of magnitude.

## 7. When *Not* to Use Digit DP

- **`N` is small** (`N < 10^6`): a plain loop is simpler and faster.
- **The predicate is not digit-local** (e.g. "is this a valid date", "does the decimal expansion
  of `1/N` terminate") — the state you need may not be finitely bounded by the digit count.
- **You need the actual numbers, not the count** and there are few of them — then filter, don't DP.
- **`N` has ~10^5 digits** given as a string: then `d` is the dominant parameter and you need a
  `Θ(d·K)` algorithm with tiny constants (matrix exponentiation / polynomial products), not a
  `Θ(d·K·10)` one.

## 8. Common State Encodings

| Predicate | Extra state `K` | Size |
|-----------|-----------------|------|
| digit sum `= s` | current sum | `s + 1` |
| divisible by `m` | remainder `mod m` | `m` |
| no two adjacent equal digits | last digit | `10` |
| strictly increasing digits | 10-bit subset mask | `2^10` |
| digit `x` absent | last digit (or a bool) | `10` |
| palindrome | position mirrored to `d − 1 − pos` | `10` |
| `x` mod `m` in a set | remainder | `m` |

The state must be **exactly** the information the predicate's future depends on and nothing
more. Every extra dimension multiplies by `K`.