# A/B Testing & Experimentation

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

## 1. The Problem This Solves

Two models, one decision. Ship the new one because its offline metric is better, or keep the old one because it is safer? The only honest way out is a well-designed experiment on live traffic.

Offline metrics predict offline. Every serious ML organisation needs a live experimentation capability, including the sequential-testing discipline that stops you from peeking.

## 2. Learning Objectives

- Design a randomised experiment with power, MDE and a fixed horizon
- Compute significance for proportions, means and ratios correctly
- Understand why peeking inflates false positives and what to do about it
- Interpret practical significance alongside statistical significance
- Run a shadow test when you cannot risk user-facing exposure
- Design a sequential test or a fixed-horizon plan with alpha control

## 3. Core Concepts

### 3.1 Randomisation is the whole design

Everything else is bookkeeping. Assignment must be random and consistent, otherwise treatment and control differ in ways no amount of statistics repairs. Hash-based assignment on user id gives stability without state.

### 3.2 Power, MDE and horizon

Power is the probability of detecting a real effect. MDE is the smallest effect worth detecting at your sample size. These are three quantities traded against each other, and deciding them before the experiment is what prevents an underpowered test being declared 'no significant difference'.

### 3.3 Peeking is a real problem

Checking significance daily and stopping when it crosses 0.05 inflates the false positive rate far above 5%. Either fix the horizon in advance, or use a sequential test (group sequential, always-valid) that controls the error rate while allowing early stopping.

### 3.4 Guardrail metrics protect the downside

A model can improve conversion and increase complaints, refunds or latency. Guardrails are non-inferiority bounds checked continuously; if a guardrail is breached, you stop regardless of how good the primary metric looks.

### 3.5 Shadow tests when exposure is unacceptable

A shadow test scores the challenger on live traffic without affecting decisions. It cannot measure business outcomes directly, but it measures score distribution, latency and disagreement, which catches most catastrophic problems before exposure.

### 3.6 Practical versus statistical significance

A 0.2% lift detected at p = 0.001 may be worth less than its rollout cost. Report the effect size with an interval, translate it to business units, and make the decision on value rather than on a p-value.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `n = 2 (z_{1-a/2} + z_{1-b})^2 sigma^2 / delta^2` | Sample size for means | the MDE-driven horizon |
| `z = (p1 - p2) / sqrt(p1(1-p1)/n1 + p2(1-p2)/n2)` | Two-proportion z | standard A/B test |
| `power = P(reject | true effect)` | Power | 1 - beta, fixed before launch |
| `delta_MDE = (z_{1-a/2} + z_{1-b}) sigma sqrt(2/n)` | MDE | the effect you can actually see |
| `false positive with peeking ~ alpha x looks` | Peeking inflation | why fixed horizons or sequential tests |
| `guardrail breach: lower bound < -delta_guard` | Non-inferiority | stop regardless of primary metric |

## 5. How the Pieces Fit Together

1. State the primary metric, the minimum detectable effect, alpha, power and the horizon before launching.

2. Define guardrail metrics with non-inferiority bounds and a stop rule.

3. Assign traffic by a stable hash on user id, with an exposure fraction you can ramp.

4. Pre-register the analysis: the test statistic, the horizon and the stopping rule.

5. Monitor guardrails continuously; check the primary metric only at planned look points.

6. Decide on effect size with an interval, in business units, not on the p-value alone.

## 6. Assumptions and Invariants

- Assignment is random, stable per unit, and independent of the outcome
- Only one primary metric drives the decision; guardrails are separate
- Alpha, power, MDE and the horizon were fixed before data collection
- Sample ratio mismatch is checked, since it invalidates everything downstream
- Guardrail thresholds have non-inferiority bounds agreed in advance
- Decisions translate the effect into business units

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Test declared a winner after 3 days of daily peeking | repeated uncorrected looks | fixed horizon or a sequential test with alpha control |
| Sample ratio mismatch not checked | assignment bug or bot traffic | assert SRM on every check before looking at metrics |
| No difference found and the test shipped anyway | underpowered design | compute power and MDE before launch, not after |
| Conversion up 40%, complaints up 300% | no guardrails | non-inferiority guardrails with a stop rule |
| Result depends on excluding outliers after the fact | post-hoc filtering | pre-register inclusion and exclusion rules |
| Winning arm introduced novelty effects | short horizon on a new experience | extend the horizon or exclude novelty-sensitive segments |
| Users in both arms | non-sticky assignment | hash on user id, not session |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `SplittableRandom / stable hash on user id` | assignment without state and stable across sessions |
| `AtomicLongArray per arm per metric` | concurrent metric counters with SRM checks |
| `NormalDistribution quantile function` | z-values for power and MDE |
| `record Experiment(String id, String primaryMetric, int alpha, double power, Instant horizonEnd)` | the pre-registered plan |
| `Interleaved guardrail evaluation` | non-inferiority checks that can stop early |

## 9. Where This Sits in the Larger System

- **labs/ml/lab10** supplies the evaluation protocol used offline before any live test.
- **mlops/lab03** is where a winning challenger is promoted.
- **mlops/lab08** supplies the drift and quality monitoring that runs alongside a test.
- **mlops/lab07** gates on offline evaluation so live tests start from a sound baseline.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Design a randomised experiment with power, MDE and a fixed horizon
- [ ] 0 — cannot yet — Compute significance for proportions, means and ratios correctly
- [ ] 0 — cannot yet — Understand why peeking inflates false positives and what to do about it
- [ ] 0 — cannot yet — Interpret practical significance alongside statistical significance
- [ ] 0 — cannot yet — Run a shadow test when you cannot risk user-facing exposure
- [ ] 0 — cannot yet — Design a sequential test or a fixed-horizon plan with alpha control

## 11. Summary Checklist

- [ ] I fixed alpha, power, MDE and the horizon before launching.
- [ ] Assignment is random and sticky per unit.
- [ ] I check sample ratio mismatch before reading any metric.
- [ ] Guardrails have non-inferiority bounds and a stop rule.
- [ ] I avoid uncorrected peeking.
- [ ] The decision uses effect size in business units, not just a p-value.
