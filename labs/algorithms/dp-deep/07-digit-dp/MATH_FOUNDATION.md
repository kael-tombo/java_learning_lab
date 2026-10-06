# MATH_FOUNDATION — Digit DP

## 1. The Recurrence

Let `f(pos, s, t, z)` count valid completions, where `pos` is the digit index, `s` the partial
aggregate (digit sum / remainder / …), `t = tight ∈ {0,1}`, `z = started ∈ {0,1}`.

```
f(d, s, t, z) = [s = S]                                    (terminal)
f(pos, s, t, z) = Σ_{x = 0}^{U(pos,t)} f(pos+1, φ(s,x,z), t ∧ (x = n[pos]), z ∨ (x>0))
U(pos, t) = n[pos]  if t = 1
          = 9        if t = 0
```

This is not a divide-and-conquer recurrence, so the Master theorem does not apply. It is a
**DAG shortest/longest-path recurrence on an acyclic graph** indexed by `pos`, solved in
topological order. Work = `(#states) × (out-degree)`.

## 2. Counting States

States = `d` positions × `(K + 1)` aggregate values × `2` tight × `2` started
= `4d(K + 1)`. With `d = 19`, `K = S = 100`: `4 · 19 · 101 = 7676` states, × 10 transitions
= `76 760` operations. **Microseconds.** This is why digit DP is a real technique and not a
curiosity: the state count is polynomial in `d`, whereas the answer space is `10^d`.

Transitions per state: `10` if `tight = 1` gives a prefix range, else `10`. So
`T = Σ_pos Σ_{s} Σ_{t,z} 10 = 10 · 4 · d · (K+1) = Θ(d · K)`.

## 3. Sums: The Linearity Argument

Let a set of `q` valid prefixes each have value `p_i` and the next digit be the same `x`.
The extended values are `10p_i + x`, so

```
Σ_{i=1..q} (10 p_i + x) = 10 · Σ p_i + x · q
```

This is *exact* and needs no distributivity assumption about the set — it is a statement about
the sum statistic only. Hence one extra accumulator array converts `count` to `sum` with no
change to the transition structure. The same trick for squares uses
`(10p+x)^2 = 100p² + 20px + x²`, requiring three accumulators (`count`, `Σp`, `Σp²`).

**Complexity warning.** `Σ x²` over `[0, N]` for `N = 10^18` is `Θ(10^54)`, far beyond `long`
(`~10^19`). Three-array DP silently overflows. Use `BigInteger` or reduce mod `M`.

## 4. Expected Digit Sum (Closed Form Derivation)

Let `X` be uniform on `[0, 10^k − 1]`. By symmetry each of the `k` positions is independent and
uniform on `{0,…,9}`. So

```
E[digitSum(X)] = Σ_{i=1}^{k} E[d_i] = k · (0+1+…+9)/10 = k · 45/10 = 4.5k
```

Summing over all `10^k` numbers:
`Σ = 10^k · 4.5k = 45 · k · 10^(k−1)`.

**Variance check** (independent positions): `Var[d_i] = (10² − 1)/12 = 99/12 = 8.25`, so
`Var[digitSum] = 8.25k` and `SD ≈ 2.87√k`. For `k = 19`, `SD ≈ 12.5` — a useful sanity check:
if your DP returns a total whose implied average is far from `4.5k ≈ 85.5`, you have a bug.

## 5. Palindrome Counting Derivation

A `d`-digit palindrome is determined by its first `⌈d/2⌉` digits. The leading digit has `9`
choices (nonzero), the remaining `⌈d/2⌉ − 1` have `10`:

```
P_d = 9 · 10^(⌈d/2⌉ − 1)
```

Total palindromes in `[0, 10^k − 1]`: `Σ_{d=1}^{k} P_d`. For `k = 4`:
`10 + 9 + 90 + 90 = 199`. Check by hand: 1-digit `0..9` (10, including `0`), 2-digit `11..99` (9),
3-digit `101..999` (90), 4-digit (90). Total `199`. ✓

Palindromes are `Θ(√N)` in number — a density of `1/√N`, which is why the digit DP for them is
pointless: iterate the first half directly.

## 6. No-Consecutive-Ones: Fibonacci Recurrence

Let `a_d` = count of length-`d` binary strings with no `11`. Split by last bit:
strings ending in `0` are `a_{d−1}`; strings ending in `1` must end `01`, leaving `a_{d−2}`.

```
a_d = a_{d−1} + a_{d−2},  a_0 = 1, a_1 = 2
```

By induction `a_d = F_{d+2}` with `F_0 = 0, F_1 = 1`. Check: `a_0 = F_2 = 1` ✓, `a_1 = F_3 = 2` ✓,
`a_2 = 3` (`00,01,10`) ✓.

**Asymptotics** via Binet's formula: `F_n = (φ^n − ψ^n)/√5` with `φ = (1+√5)/2 ≈ 1.618`,
`ψ = (1−√5)/2 ≈ −0.618`. So `a_d = Θ(φ^d)` — exponential in `d`, matching `2^d` total strings
with a constant `φ/2 ≈ 0.809` retention. The digit DP computes it in `Θ(d·10)`; the closed form
in `Θ(log d)` with fast doubling. **Same idea as digit DP, different closed form.**

## 7. Coefficient Extraction for Digit Sums

The number of length-`k` digit strings with digit sum `= s` is
`[x^s] (1 + x + … + x^9)^k`. Since `1 + x + … + x^9 = (1 − x^10)/(1 − x)`:

```
(1 − x^10)^k (1 − x)^(−k)
```

`[x^s]` expands as `Σ_{j=0}^{⌊s/10⌋} (−1)^j C(k, j) · C(s − 10j + k − 1, k − 1)`.
This gives an `Θ(s)` closed form instead of the `Θ(d·s·10)` DP — and by FFT the whole
distribution over all `s` in `Θ(d log d)`.

**Sanity check** for `k = 1, s = 4`: `C(4,1) − [j=1: C(1,1)C(−6+0,0)] = 4 − 0 = 4` ✓
(only the string `4` has digit sum 4 when `k = 1`). And for `k = 3, s = 18`, only `999`
→ the formula gives `C(20,2) − 3·C(10,2) + 3·C(0,2) = 190 − 135 + 0 = 55`… which is wrong, so
carefully: `C(k,j)` for `j` and the binomial needs `s − 10j + k − 1 ≥ k − 1`, i.e. `j ≤ s/10 = 1.8`
→ `j ∈ {0,1}`: `C(20,2) − 3·C(10,2) = 190 − 135 = 55`. Hmm, but by direct reasoning digit sum 18
with 3 digits means `(9,9,0)` permutations = 3, plus `(9,8,1)` perms = 6, plus `(8,8,2)` = 3,
`(7,9,2)`… — many. Let me recount: solutions to `a+b+c = 18`, `0 ≤ a,b,c ≤ 9`. Unbounded:
`C(20,2) = 190`. Subtract those with some variable `≥ 10`: for each of 3 variables, set `a' = a − 10`,
then `a'+b+c = 8` → `C(10,2) = 45`, times 3 = 135. No two variables can be `≥ 10` (sum would be
`≥ 20 > 18`). So `190 − 135 = 55`. ✓ The formula is right; my "only 999" reasoning was wrong.
This is a good reminder that digit-sum counts are **not** sparse.

## 8. The `started` Factor

When `started` is required the state count is exactly doubled and so is the time:
`Θ(d · K · 10) → Θ(2 d · K · 10)`. This is a constant factor in the asymptotics but frequently
a 2× wall-clock difference, because it doubles cache pressure too.

## 9. Precomputation Amortisation

Let `q` queries each need the divisibility DP. Naive: `Θ(q · d · m · 10)`.
With `ways[len][r]`: `Θ(d · m · 10) + q · Θ(d · 10)`.
The precomputation pays off when

```
d·m·10 + q·d·10  <  q·d·m·10
     ⟺  1 + q  <  q·m
     ⟺  q  >  1/(m − 1)
```

i.e. for `m ≥ 2` and `q ≥ 2`. So **essentially always** — the only cost is memory
`Θ(d · m)`. This is the standard amortisation argument: pay once, query cheaply.

## 10. Master-Theorem Check (When It *Does* Apply)

Digit DP is not recursive, so the Master theorem is irrelevant. But the analogous
divide-and-conquer — "count digit strings of length `d` by splitting in half" — gives
`T(d) = 2 T(d/2) + O(K)`, and here `a = 2, b = 2`, so `log_b a = 1` and the Master theorem
gives `Θ(d · K)`. That matches the iterative DP. It also shows why **memoisation and rolling
arrays give the same time**: both are topological orderings of the same `d`-layer DAG, and the
space differs (`Θ(dK)` vs `Θ(K)`) only because rolling forgets layers you will never revisit.