# Hypothesis Testing - Mathematical Foundations

**Track:** statistics  |  **Lab:** lab03  |  **Level:** Intermediate

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
| `H₀: μ_A = μ_B vs H₁: μ_A ≠ μ_B` | Two-sample hypothesis - state direction before data |
| `t = (x̄_A − x̄_B) / (s_p sqrt(1/n_A + 1/n_B))` | Two-sample t - Welch unless equal variances |
| `df = n_A + n_B − 2` | Degrees of freedom - pooled version only |
| `z = (x̄ − μ₀) / (σ/sqrt(n))` | One-sample z - known sigma |
| `χ² = Σ(Oᵢ − Eᵢ)² / Eᵢ` | Chi-square - counts, not means |
| `df = k − 1` | Chi-square df - k categories |
| `p = P(T ≥ |t|) under H₀` | p-value - conditional on the null, not P(H₀) |
| `power = P(reject H₀ | H₁ true)` | Power - 1 − beta |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Test statistic and the reference distribution

```text
Welch: t = (xbar_A - xbar_B) / sqrt(s_A^2/n_A + s_B^2/n_B)
df (Welch) = (s_A^2/n_A + s_B^2/n_B)^2 / [ (s_A^2/n_A)^2/(n_A-1) + (s_B^2/n_B)^2/(n_B-1) ]
p = P(T_df >= |t|)
```

The statistic measures the difference in units of its standard error, and the degrees of freedom determine which t distribution to compare against. Welch's df is fractional and always smaller than the pooled version, which is the conservative direction.

**Worked example.** n_A = n_B = 20, means differ by 0.4, s_A = s_B = 1.0: SE = sqrt(2/20) = 0.316, t = 1.265, df = 38, p ≈ 0.21. With unequal variances, say s_A = 1.0 and s_B = 3.0, Welch gives SE = sqrt(0.05 + 0.45) = 0.707, t = 0.566, p ≈ 0.58, whereas the pooled test wrongly reports t = 2.29 and p = 0.03.


---

## 2. Type I, Type II and power

```text
alpha = P(reject H_0 | H_0 true)
beta = P(fail to reject | H_1 true)
power = 1 - beta
power rises with n, with effect size, and with alpha
```

Alpha and beta trade against each other at fixed n. That trade is the reason sample size is computed before the experiment: fixing alpha without considering power leaves you with a test that cannot detect the effect you care about.

**Worked example.** Effect size d = 0.5, alpha = 0.05 two-sided, power 0.80: n = 64 per group. Power 0.50 needs only n = 33, so the same study at half the size would miss half the real effects it was designed to find.


---

## 3. Confidence interval versus p-value

```text
difference estimate d-hat with SE = s/sqrt(n)
CI = d-hat ± t_{1-alpha/2, df} SE
CI excluding 0 is equivalent to p < alpha, but the interval carries magnitude
```

The interval and the p-value encode the same decision, but only one of them tells you the size of the effect and its precision. Reports that give only a p-value force readers to guess the magnitude.

**Worked example.** d-hat = 0.40, SE = 0.12, CI = [0.16, 0.64], p = 0.001. The p-value says 'significant'; the interval says the effect could plausibly be 0.16, which may or may not matter commercially.


---

## 4. Multiple looks and the inflation

```text
under the null, per-look alpha behaves as ~1 - (1 - alpha)^k
k looks at alpha = 0.05: k=2 -> 0.0975, k=5 -> 0.226, k=10 -> 0.401
fix the horizon, or use a sequential design
```

Each additional look is another opportunity to cross alpha by chance. The inflation grows quickly, which is why teams that 'watch and stop' ship noise at a rate far above their nominal 5%.

**Worked example.** A metric monitored daily for 14 days with a stop at first p < 0.05 has an effective error rate near 52%. A sequential design with alpha spending holds the true rate at 5% while still permitting early stopping.


---

## Cheat Sheet

- `H₀: μ_A = μ_B vs H₁: μ_A ≠ μ_B` - Two-sample hypothesis
- `t = (x̄_A − x̄_B) / (s_p sqrt(1/n_A + 1/n_B))` - Two-sample t
- `df = n_A + n_B − 2` - Degrees of freedom
- `z = (x̄ − μ₀) / (σ/sqrt(n))` - One-sample z
- `χ² = Σ(Oᵢ − Eᵢ)² / Eᵢ` - Chi-square
- `df = k − 1` - Chi-square df
- `p = P(T ≥ |t|) under H₀` - p-value
- `power = P(reject H₀ | H₁ true)` - Power

## Numerical Traps

- Interpreting a p-value as P(null | data).
- Using the pooled t when variances are unequal and n is small.
- Declaring equivalence from a non-significant result.
- Testing many times and reporting only the crossing test.
- Choosing a one-sided alternative after seeing the direction.

## Self-Check Problems

1. Compute Welch's t and fractional degrees of freedom for two groups with unequal variances.
2. Derive the per-look false positive inflation for k looks at a given alpha.
3. Compute a confidence interval and verify it excludes 0 exactly when the test is significant.
4. Design a test for a given effect size, alpha and power; report n and the achievable MDE.
5. Take a real metric you track daily, simulate the null, and measure the false positive rate of your current process.
