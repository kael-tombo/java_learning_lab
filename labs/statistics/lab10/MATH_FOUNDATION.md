# Statistical Power & Effect Size - Mathematical Foundations

**Track:** statistics  |  **Lab:** lab10  |  **Level:** Advanced

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
| `d = (̄x₁ − ̄x₂) / sₚ` | Cohen's d - pooled standard deviation |
| `Hedges' g = d / (1 − 3/(4n − 9))` | Bias-corrected d - better for small n |
| `r = d / sqrt(d² + 4)` | Effect size as r - relatable to correlation |
| `power = 1 − β` | Power - 1 minus Type II error |
| `MDE = (z_{1−α/2} + z_{1−β}) σ sqrt(2/n)` | Minimum detectable effect - what your n can see |
| `n = 2 (z_{1−α/2} + z_{1−β})² σ² / δ²` | Required n - inverting power |
| `p1, p2 proportions` | Proportion power - pooled variance under the null |
| `pph = 2 arcsin sqrt(p1) − 2 arcsin sqrt(p2)` | Fisher z for rates - propensity differences |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Cohen's d, pooling and bias

```text
pooled s_p = sqrt(((n1-1)s1^2 + (n2-1)s2^2)/(n1+n2-2))
d = (xbar1 - xbar2)/s_p
Hedges' g = d * (1 - 3/(4(n1+n2)-9))
```

Pooling assumes comparable variances; with unequal variances the alternative is Glass's delta using the control standard deviation. Hedges' correction exists because d is biased upward at small n, which is exactly the regime where the bias matters.

**Worked example.** n1 = n2 = 8, difference 1.0, s = 1.0: d = 1.0 but the correction factor is 1 - 3/(4*16 - 9) = 0.955, so g = 0.955. At n = 20 each, the factor is 0.974 and the difference is negligible, which is why the correction is reserved for small samples.


---

## 2. Power for a two-sample comparison

```text
non-centrality: lambda = delta / (sigma sqrt(1/n1 + 1/n2))
power = P(T_{df, lambda} > t_{1-alpha/2}) + P(T_{df, lambda} < -t_{1-alpha/2})
two-sided needs lambda about 2.8 for 80% power; one-sided about 2.0
```

Power is the probability of rejecting the null under a specific alternative, which is why the alternative must be stated. The gap between two-sided and one-sided power is substantial and is often misjudged.

**Worked example.** delta = 0.5 sigma, n = 64 per arm: two-sided power 0.80. n = 64 one-sided: power 0.90. At n = 20 per arm, two-sided power for d = 0.5 is about 0.26 — the study would miss a medium effect four times out of five.


---

## 3. Minimum detectable effect

```text
MDE = (z_{1-alpha/2} + z_{1-beta}) sigma sqrt(2/n)
for d: MDE_d = (z_{1-alpha/2} + z_{1-beta}) sqrt(2/n)
at alpha 0.05, power 0.8: MDE_d = 2.802 sqrt(2/n)
```

MDE is the honest resolution statement for a fixed sample. It converts a sample size constraint into the actual question 'what could this study have found', which is what reviewers and stakeholders should be told.

**Worked example.** n = 20 per arm: MDE_d = 2.802 sqrt(0.1) = 0.886, so only an enormous effect is detectable. n = 100: 0.396. n = 400: 0.198. Quadr quadrupling the sample halves the detectable effect, as the 1/sqrt(n) law implies.


---

## 4. Power under the wrong alternative

```text
power is a function of the assumed effect: power(d=0.1) << power(d=0.5) << power(d=1.0)
post-hoc power at the observed effect is not informative:
it is a monotone function of the p-value and adds nothing
```

Post-hoc power computed from the observed effect is a deterministic function of the p-value, so it tells you nothing the p-value did not. Retrospective power is only meaningful when computed at the effect you specified before the study.

**Worked example.** A study with n = 50 per arm and p = 0.08: post-hoc power at the observed effect is around 0.40 and is uninformative. Retrospective power at the planned d = 0.5 is 0.48, which correctly explains why an inconclusive result was likely.


---

## 5. Multiplicity and power cost

```text
family-wise alpha via Bonferroni: alpha' = alpha/m
power with alpha' is lower for the same n
required n grows roughly with log(m)
```

Testing many hypotheses costs power as well as error control. Declaring ten outcomes at alpha = 0.05 without adjustment makes each test less powerful and more likely to produce a family-wise error.

**Worked example.** m = 10 comparisons, alpha' = 0.005: with n = 400 per arm, power for d = 0.2 falls from about 0.85 to 0.63. Reaching 0.85 again needs roughly 600 per arm, a 50% increase in cost.


---

## Cheat Sheet

- `d = (̄x₁ − ̄x₂) / sₚ` - Cohen's d
- `Hedges' g = d / (1 − 3/(4n − 9))` - Bias-corrected d
- `r = d / sqrt(d² + 4)` - Effect size as r
- `power = 1 − β` - Power
- `MDE = (z_{1−α/2} + z_{1−β}) σ sqrt(2/n)` - Minimum detectable effect
- `n = 2 (z_{1−α/2} + z_{1−β})² σ² / δ²` - Required n
- `p1, p2 proportions` - Proportion power
- `pph = 2 arcsin sqrt(p1) − 2 arcsin sqrt(p2)` - Fisher z for rates

## Numerical Traps

- Computing power at the observed effect and calling it informative.
- Using an uninflated pilot variance for planning.
- Ignoring sidedness when comparing designs.
- Planning with alpha that ignores the multiplicity correction.
- Quoting Cohen's thresholds as if they were universal.

## Self-Check Problems

1. Compute d and Hedges' g for two groups and show the bias difference at small n.
2. Compute power for a two-sample comparison across n and both sidednesses.
3. Compute the MDE for n = 20, 100 and 400 per arm and express it in business units.
4. Show that post-hoc power is a function of the p-value.
5. Recompute required n after a Bonferroni correction for ten comparisons.
