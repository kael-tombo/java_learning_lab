# Experimental Design - Mathematical Foundations

**Track:** statistics  |  **Lab:** lab08  |  **Level:** Advanced

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
| `n = 2 (z_{1α/2} + z_{1−β})² σ² / δ²` | Sample size for means - per-arm, two-sided |
| `n = (z_{α/2} sqrt(2 p̄ q̄) + z_{1−β} sqrt(p1q1 + p2q2))² / (p1−p2)²` | Sample size for proportions - pooled under the null |
| `SE with blocking: σ sqrt(1/n + 1/N · ρ)` | Blocked variance - rho is the correlation within blocks |
| `main effect A = mean(y at A+) − mean(y at A−)` | Factorial main effect - averaged over B levels |
| `interaction AB = (E++ − E+-) − (E-+ − E--)` | Interaction contrast - the term usually skipped |
| `δ = (z_{1−α/2} + z_{1−β}) σ sqrt(2/n)` | Minimum detectable effect - what your design can see |
| `VIF / variance share = 1 − R²_block` | Variance reduction from blocking - quantifies the gain |

## Why the Math Matters

The formulas below are not decoration: each one is the place where a wrong assumption silently produces a plausible number. Knowing which formula applies, and when it stops applying, is the skill this lab builds.


---

## 1. Sample size for means

```text
n per arm = 2 (z_{1-alpha/2} + z_{1-beta})^2 sigma^2 / delta^2
delta is the minimum effect worth detecting
variance inflation factor for k groups: 1 + (k-1) rho within a block
```

Sample size is arithmetic once alpha, power, the effect worth detecting and the variance are fixed. Blocking reduces the variance that appears in the formula, which is where its power gain comes from.

**Worked example.** delta = 0.5 sigma, alpha = 0.05, power = 0.8: n = 2 x 7.85 / 0.25 = 63 per arm. With blocking where within-block correlation rho = 0.6, the variance falls to 1 - 0.6 = 0.4 of the unblocked value, so n drops to about 25.


---

## 2. Sample size for proportions

```text
n = (z_{alpha/2} sqrt(2 pbar qbar) + z_{beta} sqrt(p1 q1 + p2 q2))^2 / (p1 - p2)^2
baseline p1 = 0.10, target p2 = 0.11, alpha = 0.05, power = 0.8
```

Proportions have their own formula because the variance depends on p. The relative effect matters: detecting 10% to 11% needs far more observations than detecting 10% to 20%.

**Worked example.** p1 = 0.10, p2 = 0.11: n ≈ 15,500 per arm. p1 = 0.10, p2 = 0.12: n ≈ 3,900. p1 = 0.10, p2 = 0.20: n ≈ 380. A tenfold difference in required n across three targets that all sound reasonable.


---

## 3. Blocking and the variance reduction

```text
unblocked variance = sigma^2
blocked within-unit variance = sigma^2 (1 - rho)
n_blocked / n_unblocked = 1 - rho
```

Blocking works because similar units have similar outcomes. The correlation within blocks is what gets removed, so the gain is proportional to how homogeneous the blocks are.

**Worked example.** Machine-to-machine variation with rho = 0.5: half the error variance is removed, so the same power needs half the observations. With rho = 0.9, a quarter of the sample — which is why blocking on batch or machine is standard practice in manufacturing experiments.


---

## 4. Factorial effects and interaction

```text
main effect A = mean(y | A=+1) - mean(y | A=-1)
interaction AB = [mean(A+,B+) - mean(A+,B-)] - [mean(A-,B+) - mean(A-,B-)]
interaction significant => report simple effects, not marginal means
```

The interaction contrast measures whether A's effect depends on B's level. When it is significant, the marginal mean difference hides real structure and the analysis must describe the cells.

**Worked example.** Cells: (A+B+) = 10, (A+B-) = 8, (A-B+) = 5, (A-B-) = 2. Main effect of A = 7 - 3.5 = 3.5, which says 'A helps'. Interaction = (10-8) - (5-2) = -1, so A actually helps at B+ and hurts at B-. The marginal main effect is meaningless here.


---

## 5. Confounding and identifiability

```text
confounded when level(A) determines level(B)
effects are then not separately estimable: any (beta_A, beta_B) pair fits
replication within cells or additional factor levels restores identifiability
```

Identifiability is a property of the design matrix, not of the sample size. Adding observations to a confounded design adds precision to an uninterpretable quantity.

**Worked example.** Training data in a study where price was only ever tested at one level per region: price and region effects are confounded, and the price coefficient absorbs regional differences. No sample size fixes this; only varying price within region does.


---

## Cheat Sheet

- `n = 2 (z_{1α/2} + z_{1−β})² σ² / δ²` - Sample size for means
- `n = (z_{α/2} sqrt(2 p̄ q̄) + z_{1−β} sqrt(p1q1 + p2q2))² / (p1−p2)²` - Sample size for proportions
- `SE with blocking: σ sqrt(1/n + 1/N · ρ)` - Blocked variance
- `main effect A = mean(y at A+) − mean(y at A−)` - Factorial main effect
- `interaction AB = (E++ − E+-) − (E-+ − E--)` - Interaction contrast
- `δ = (z_{1−α/2} + z_{1−β}) σ sqrt(2/n)` - Minimum detectable effect
- `VIF / variance share = 1 − R²_block` - Variance reduction from blocking

## Numerical Traps

- Computing n from an under-estimated pilot variance.
- Using a formula for means on proportions, or vice versa.
- Reporting marginal main effects when the interaction is significant.
- Ignoring blocking in the variance used for the power calculation.
- Increasing sample size in a confounded design and expecting clarification.

## Self-Check Problems

1. Compute n per arm for two means with blocking, given a within-block correlation.
2. Compute n per arm for a 10% to 11% baseline conversion change at 80% power.
3. Design a 2x2 factorial with replication and compute main effects and interaction.
4. Show that a confounded design cannot identify separate effects, algebraically.
5. Take a pilot study, estimate its variance, inflate it, and recompute n with justification.
