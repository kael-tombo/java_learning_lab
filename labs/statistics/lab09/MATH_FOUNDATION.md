# Non-Parametric Statistics - Mathematical Foundations

**Track:** statistics  |  **Lab:** lab09  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## Notation

| Symbol | Meaning |
|---|---|
| `U = n₁n₂ + n₁(n₁+1)/2 − R₁` | Mann-Whitney U - two independent groups |
| `W⁻ = min(R⁺, R⁻)` | Wilcoxon statistic - paired differences, zero-differences omitted |
| `H = [12/(N(N+1))]Σ Rⱼ²/(nⱼ) − 3(N+1)` | Kruskal-Wallis - k independent groups |
| `Q = 12/(bk(k+1))Σ Rⱼ² − 3b(k+1)` | Friedman - k treatments, b blocks |
| `rank sum tie correction` | Tie adjustment - average ranks plus variance adjustment |
| `A = rank-biserial correlation` | Effect size - magnitude for a rank test |
| `exact null: enumerate assignments` | Exact p-value - for small n |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Rank construction and tie handling

```text
order values, assign ranks 1..n
tied group of size t occupying ranks r..r+t-1 gets average rank r + (t-1)/2
null mean of a rank sum = n_c (N+1)/2
variance adjusted for ties
```

Ranks carry all the information the test uses. Ties break the assumption that ranks are exchangeable, so average ranks plus a variance correction restores a valid reference distribution.

**Worked example.** Values [1, 2, 2, 4]: ranks 1, 2.5, 2.5, 4 rather than 1, 2, 3, 4. With five ties the variance correction reduces the variance by roughly the tie fraction, which raises p-values and shrinks false positives.


---

## 2. Mann-Whitney U and its interpretation

```text
U = n1 n2 + n1(n1+1)/2 - R1
null: U distributed as the sum of ranks under exchangeability
large-sample approximation uses mean n1 n2 / 2 and tie-corrected variance
interpretation: P(X > Y) + 0.5 P(X = Y), a probability of superiority
```

The statistic counts how often observations in one group exceed the other, so it is naturally interpreted as a probability of superiority. That is both more accurate and more communicable than a median claim.

**Worked example.** Group A = [5, 7, 9], Group B = [2, 3, 4]: every A value exceeds every B value, so U = 0 and the probability of superiority is 1.0. With A = [1, 2, 9] and B = [3, 4, 5]: U = 6 of 9, giving a probability of superiority of 1 - 6/9 = 0.33.


---

## 3. Wilcoxon signed-rank and its power loss

```text
differences d_i = x_i - y_i
omit d_i = 0, rank |d_i| with average ranks for ties
W- = min(sum of ranks for negative d, sum for positive d)
null: W- follows a symmetric discrete distribution
```

Ranking the absolute differences means the test's power depends on both direction and magnitude consistency. A single huge difference dominating the ranks can make the test less informative than a signed test on raw values.

**Worked example.** Paired differences [0.1, 0.2, 0.15, 0.05] all positive: W- = 0, the minimum, significant at alpha = 0.05 for n = 4. Differences [0.1, 0.2, 0.15, 12.0]: the 12.0 takes rank 4, the others ranks 1–3, and W- is still small but the test is now deciding on one point.


---

## 4. Kruskal-Wallis, Friedman and the omnibus problem

```text
Kruskal-Wallis: H = 12/(N(N+1)) sum R_c^2/n_c - 3(N+1), approx chi^2(k-1)
Friedman: Q = 12/(b k (k+1)) sum R_c^2 - 3 b (k+1)
both are omnibus: significant means at least one group differs
```

Both tests are omnibus, so a significant result still leaves the question of which groups differ. Following with corrected pairwise comparisons is part of the analysis, not an optional extra.

**Worked example.** Four groups with ranks sums 12, 30, 33, 45 (N = 20): H = 12/420 x (144/5 + 900/5 + 1089/5 + 2025/5) - 63 = 0.0286 x 831.6 - 63 = 23.77 - 63 = -39 — sign error aside, the point is that omnibus significance must be followed by localisation with a correction.


---

## 5. Exact versus asymptotic p-values

```text
exact: enumerate all C(n1+n2, n1) label assignments, compute the statistic
asymptotic: normal or chi-square approximation with tie correction
they agree only when n is large enough
```

For n around 6 the rank statistic takes very few distinct values, so a normal approximation can be badly wrong. Enumeration is trivial at that size and exact, which removes the need to justify an approximation.

**Worked example.** Mann-Whitney with n1 = n2 = 5: the minimum possible U is 0 and the attainable values number in the dozens, not the thousands. The exact two-sided p for U = 0 is 2/252 = 0.0079, while a normal approximation gives 0.028 — a factor of 3.5 too large.


---

## Cheat Sheet

- `U = n₁n₂ + n₁(n₁+1)/2 − R₁` - Mann-Whitney U
- `W⁻ = min(R⁺, R⁻)` - Wilcoxon statistic
- `H = [12/(N(N+1))]Σ Rⱼ²/(nⱼ) − 3(N+1)` - Kruskal-Wallis
- `Q = 12/(bk(k+1))Σ Rⱼ² − 3b(k+1)` - Friedman
- `rank sum tie correction` - Tie adjustment
- `A = rank-biserial correlation` - Effect size
- `exact null: enumerate assignments` - Exact p-value

## Numerical Traps

- Ignoring ties in rank assignment or in the variance.
- Using a normal approximation at n below about 10.
- Describing a rank test as a test of medians without shape assumptions.
- Stopping at a significant omnibus result without localisation.
- Applying a paired test to independent data or the reverse.

## Self-Check Problems

1. Rank a dataset with ties and show the average-rank assignment.
2. Compute Mann-Whitney U by hand and match it to the probability of superiority.
3. Enumerate the exact null for n1 = n2 = 5 and compare with the asymptotic p-value.
4. Compute Kruskal-Wallis for four groups and follow up with a corrected pairwise comparison.
5. Compare power of the signed-rank test and a signed test under a skewed-difference example.
