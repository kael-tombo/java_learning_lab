# A/B Testing & Experimentation - Mathematical Foundations

**Track:** mlops  |  **Lab:** lab10  |  **Level:** Advanced

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
| `n = 2 (z_{1-a/2} + z_{1-b})^2 sigma^2 / delta^2` | Sample size for means - the MDE-driven horizon |
| `z = (p1 - p2) / sqrt(p1(1-p1)/n1 + p2(1-p2)/n2)` | Two-proportion z - standard A/B test |
| `power = P(reject | true effect)` | Power - 1 - beta, fixed before launch |
| `delta_MDE = (z_{1-a/2} + z_{1-b}) sigma sqrt(2/n)` | MDE - the effect you can actually see |
| `false positive with peeking ~ alpha x looks` | Peeking inflation - why fixed horizons or sequential tests |
| `guardrail breach: lower bound < -delta_guard` | Non-inferiority - stop regardless of primary metric |

## Why the Math Matters

Experimentation is power analysis plus error-rate control: how large a sample you need, what peeking does to your alpha, and how guardrails bound the downside.


---

## 1. Sample size and MDE

```text
n_per_arm = 2 (z_{1-alpha/2} + z_{1-beta})^2 sigma^2 / delta^2
for proportions: n = (z_{a/2} sqrt(2 p_bar (1-p_bar)) + z_b sqrt(p1(1-p1)+p2(1-p2)))^2 / (p1-p2)^2
```

Sample size is the arithmetic consequence of the effect you want to detect, the error rates you accept and the variance of the metric. Fixing it before launch is what makes 'no significant difference' interpretable.

**Worked example.** Baseline conversion 4%, want to detect a 0.2% relative lift (4.008% to 4.016%), alpha 0.05, power 0.8: n is roughly 190k per arm, about 8 days at 1M sessions/day. An MDE of 0.5% would need 12k per arm, under a day.


---

## 2. Two-proportion significance

```text
p_hat_pool = (x1 + x2) / (n1 + n2)
SE = sqrt(p_pool (1 - p_pool) (1/n1 + 1/n2))
z = (p1 - p2) / SE,  two-sided p = 2 (1 - Phi(|z|))
```

The pooled standard error is correct under the null that the rates are equal, which is what the test assumes. Using unpooled standard errors is a conservative variant that is valid but slightly less powerful.

**Worked example.** p1 = 0.0402 with n1 = 200k, p2 = 0.0400 with n2 = 200k: p_pool = 0.0401, SE = 0.000632, z = 0.317, p-value 0.75. Nowhere near significance; the MDE at this n is about 0.18 percentage points.


---

## 3. Peeking inflates the false positive rate

```text
per-look alpha under independence ~ 1 - (1 - alpha)^k
for alpha = 0.05 and k = 10 looks: ~40% false positive
fixed horizons or sequential boundaries correct this
```

Repeated uncorrected looks behave like multiple hypothesis testing. The inflation is severe: ten daily looks turn a 5% error rate into roughly 40%. Sequential designs fix it while still permitting early stopping for harm.

**Worked example.** A test run for 14 days with daily significance checks has an effective false positive rate near 50% if run until 'significant'. That is how teams ship noise.


---

## 4. Guardrail non-inferiority

```text
for each guardrail: lower bound of the effect CI > -delta_guard
breach if lower bound <= -delta_guard
```

A guardrail is a one-sided test that the treatment is not worse than the control by more than an agreed margin. Because it is one-sided and pre-specified, it can stop an experiment for harm without stopping it for benefit.

**Worked example.** Latency guardrail: control p99 180 ms, treatment 196 ms, delta_guard 10%. Effect +16 ms is +8.9%, and with a tight interval the lower bound stays above +10 ms, so it passes. At +25 ms the bound crosses and the test stops.


---

## 5. Sequential testing with alpha control

```text
group sequential: O'Brien-Fleming or Pocock boundaries per look
alpha spending function alpha(t) with total <= alpha
always-valid: confidence sequence valid at every t
```

Alpha-spending approaches pre-plan a boundary schedule that spends a fixed total error rate across looks. Always-valid confidence sequences are the modern alternative: valid at every time point with no pre-planned looks.

**Worked example.** O'Brien-Fleming spends very little alpha early and most at the end, so an early stop requires an enormous effect. Pocock spends evenly, so early stops are easier but the final test is weaker.


---

## Cheat Sheet

- `n = 2 (z_{1-a/2} + z_{1-b})^2 sigma^2 / delta^2` - Sample size for means
- `z = (p1 - p2) / sqrt(p1(1-p1)/n1 + p2(1-p2)/n2)` - Two-proportion z
- `power = P(reject | true effect)` - Power
- `delta_MDE = (z_{1-a/2} + z_{1-b}) sigma sqrt(2/n)` - MDE
- `false positive with peeking ~ alpha x looks` - Peeking inflation
- `guardrail breach: lower bound < -delta_guard` - Non-inferiority

## Numerical Traps

- Computing sample size after seeing the effect you want to detect.
- Using unpooled standard errors without realising it costs power.
- Running daily significance checks and stopping at first crossing.
- Comparing arms without checking the sample ratio first.
- Deciding on a p-value without translating the effect into business units.

## Self-Check Problems

1. Compute required n per arm for a 4% baseline detecting a 10% relative lift at alpha 0.05, power 0.8.
2. Run a two-proportion test on counts 802/200000 versus 800/200000 and interpret.
3. Compute the false positive rate over 10 daily looks at alpha 0.05 and explain the fix.
4. Design a latency guardrail with a non-inferiority bound and decide pass or fail for a given effect and interval.
5. Compare O'Brien-Fleming and Pocock boundaries qualitatively for early stopping behaviour.
