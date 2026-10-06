# 07 — Digit DP

<div align="center">

**Digit DP: Counting · Summing · Minimising · Remainders · Divisibility · Overlapping Ranges**

</div>

---

## Learning Objectives

- Recognise the digit-DP shape: state = `(position, tight, carry/remainder)` and an accumulator
- Implement `count(n)` — numbers in `[0, n]` with a digit predicate — in `Θ(d · k · 10)`
- Implement `sum(n)` by swapping the "one way" DP for a "value-carrying" DP
- Explain why the **tight** (already-equal) flag is what makes it bound-aware
- Handle divisibility, digit-sum, "no adjacent equal digits", palindromes, and ranges
- Recognise the overcounting trap: `leading zeros` and the `started` flag
- State the closed forms (`Θ(1)` for digit-sum and palindrome counts) and know when they beat the DP

## Prerequisites

- `01-dp-classics` — the framework
- Modular arithmetic, `long` overflow discipline
- `19-number-theory` / `39-number-theory-advanced` for the number-theory variants

## Estimated Time

- **Theory**: 85 minutes
- **Practice**: 140 minutes
- **Exercises**: 70 minutes
- **Total**: 5 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Digit DP state | `dp[pos][tight]` for counting; add `carry`/`rem` for aggregates |
| `tight` flag | the prefix built so far equals `n`'s prefix — bounds the next digit |
| Transition | try `d` in `[0, (tight ? n[pos] : 9)]` |
| Leading zeros | `007` is `7`; decide whether they matter (digit sum, divisibility) |
| `started` flag | whether a non-zero digit has appeared — for "no leading zero" problems |
| Counting DP | accumulates a **count**; every path adds `1` at the end |
| Value-carrying DP | accumulates a **sum/product**; every path adds its value |
| `O(1)` memory | rolling two arrays of size `k` |
| Closed form | digit sum `= 45·d·10^{d−2}`; palindromes `= 9·10^{⌈d/2⌉−1}` |
| Precomputation | `f[len][r]` = number of `len`-digit suffixes with remainder `r` mod `m` |

## Complexity Snapshot

| Problem | Time | Space | Notes |
|---------|------|-------|-------|
| Count numbers ≤ `n` with digit-sum `= s` | **`Θ(d · 10 · s)`** | `Θ(s)` | `d` = digits |
| Sum of digit sums ≤ `n` | **`Θ(d · 10 · s)`** | `Θ(s)` | |
| Count ≤ `n` divisible by `m` | `Θ(d · 10 · m)` | `Θ(m)` | precompute `Θ(d·m)` |
| Count ≤ `n` with no two adjacent equal digits | **`Θ(d · 10)`** | `Θ(10)` | last digit in the state |
| Count ≤ `n` with strictly increasing digits | `Θ(d · 10 · 10)` | `Θ(100)` | subset mask |
| Count palindromes ≤ `n` | `Θ(d · 10)` | `O(1)` | **closed form**: `9·10^{⌈d/2⌉−1}` |
| Sum of numbers ≤ `n` with digit-sum `= s` | `Θ(d · 10 · s)` | `Θ(s)` | value-carrying |
| Count `≤ n` avoiding digit `x` | `Θ(d · 10)` | `Θ(10)` | |
| Min/max number with digit-sum `= s` | `Θ(d · s · 10)` greedy | `Θ(s)` | greedy, not DP |
| `n`-digit binary strings without consecutive 1s | `Θ(d · 10)` | `Θ(10)` | Fibonacci closed form |
| Overlapping range `[a, b]` | `Θ(d · k · 10)` | | |

**The general shape:** `Θ(d · K · 10)` where `K` is the extra state (sum target, modulus, last digit). `d ≤ 19` for `long`, so the DP is almost always small — **the interesting parameter is `K`.**

## Algorithms Covered

### Counting ≤ n with digit sum = s
```java
dp[pos][sum][tight]
base: dp[0][0][1] = 1
transition: for each digit d allowed, dp[pos+1][sum+d][tight && d == n[pos]] += dp[pos][sum][tight]
answer: sum over tight of dp[d][s][*]
```

### Sum ≤ n with digit sum = s
Same state, but the accumulator carries **partial values**:
```java
sumDp[pos+1][sum + d][nt] += dp[pos][sum][tight] * 1          // count
sumDp[pos+1][sum + d][nt] += sumDp[pos][sum][tight] * 10 + dp[pos][sum][tight] * d
```
**This is the key extension:** the value of a prefix `p` extended by digit `d` is `10p + d`, so both the *count* and the *sum of values* follow the same transition with one extra term.

### Precomputation for divisibility
```java
// ways[len][r] = number of `len`-digit strings whose value ≡ r (mod m), leading zeros ALLOWED
ways[0][0] = 1
for len in 0..D:
    for r in 0..m-1:
        for digit in 0..9:
            ways[len+1][(10*r + digit) % m] += ways[len][r]
```
`Θ(D · m · 10)` once, then each query `≤ n` is `Θ(D · 10)`. **Turns `q` queries into `Θ(D·m·10 + q·D·10)` instead of `Θ(q·D·m·10)`.**

### Closed forms worth knowing

| quantity | closed form |
|----------|-------------|
| Count of `d`-digit numbers | `9·10^{d−1}` |
| **Total digit sum of all `0..10^d − 1`** | `45 · d · 10^{d−1}` |
| Average digit sum over `0..10^d − 1` | `4.5 d` |
| **Count of palindromes ≤ `n` (`d` digits)** | `9 · 10^{⌈d/2⌉ − 1}` |
| `d`-digit binary strings without `11` | `F_{d+2}` (Fibonacci) |

**These beat the DP by a large constant and by clarity.** Always check for a closed form before writing a DP.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/digitdp/` | Count/sum/min/max digit DP templates |
| `src/test/java/com/alglab/digitdp/` | Brute-force cross-validation for small `n` |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | `n = 0`, `n = 9`, `n = 10^k`, leading-zero cases |
| `BENCHMARK/` | DP vs closed form vs precomputation |
| `MINI_PROJECT/` | Digit-DP table visualiser |
| `REAL_WORLD_PROJECT/` | Counting-format validator / PIN-range enumerator |
| `CHALLENGE/` | Multi-constraint digit DP, digit-DP with `long` overflow care |
| `DIAGRAMS/` | `tight` flag propagation, table fills |