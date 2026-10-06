# MINI_PROJECT — Distribution Diagnostics and Stable Tails

**Track:** statistics  |  **Lab:** lab02  |  **Level:** Foundational

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

**Brief.** Build a distribution toolkit with log-space tails, seeded samplers, and diagnostics that detect when a family is wrong.

**Timebox.** 3 hours

## 1. Why This Project Exists

The value here is not evaluating four formulas; it is knowing when the formula you are using does not apply.

## 2. Requirements

- Normal, binomial, Poisson and exponential with verified normalisation.
- Log-space evaluation with a stability comparison against the naive formula.
- Normal approximation with a continuity correction and an automatic validity gate.
- Seeded samplers validated against theoretical moments with sampling-aware tolerances.
- Overdispersion detection on real-shaped operational data, with an alternative model compared.
- Monte Carlo estimator with intervals and a convergence check.
- A backoff simulation connecting the exponential distribution to a real design decision.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Implement the four distributions; verify normalisation | A verified suite |
| 2 | 30m | Log-space evaluation and a stability report | A before/after comparison |
| 3 | 30m | Normal approximation with continuity correction and validity gate | A gated approximation |
| 4 | 30m | Seeded samplers with moment validation | Validated samplers |
| 5 | 35m | Overdispersion detection with an alternative model | A dispersion analysis |
| 6 | 25m | Monte Carlo estimate with intervals and convergence | An interval report |
| 7 | 25m | Backoff simulation with a policy recommendation | A recommendation with numbers |

## 4. Architecture Sketch

```text
 observed process
    |
 classify: count | waiting time | continuous
    |
 family assumption check (independence, constant rate)
    |
 [1] evaluate (log space, verified normalisation)
 [2] approximate (validity gate + continuity correction)
 [3] sample (seeded, moment-validated)
 [4] diagnose (dispersion ratio, rate variation)
    |                        |
 normal family          overdispersed --> alternative model
    |                        |
 [5] Monte Carlo with intervals
 [6] backoff simulation --> policy recommendation
```

## 5. Implementation Notes

- Construct the overflow case deliberately; lambda = 200, k = 800 makes the failure obvious.
- Sampling validation needs sampling-aware tolerances or it will reject correct samplers.
- Overdispersion analysis is more valuable than another distribution: it tells you the model is wrong.
- Tie the exponential distribution to retry backoff so the mathematics has an operational consequence.

## 6. Deliverables

1. Verified distribution suite with a stability report.
1. Gated normal approximation with continuity correction.
1. Validated seeded samplers and a moment-check table.
1. Overdispersion analysis with an alternative model, plus a backoff recommendation.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | Normalisation verified; tails stable; approximation gated |
| Validation | 25% | Samplers moment-checked with sampling-aware tolerances |
| Diagnosis | 25% | Overdispersion detected with a justified alternative |
| Communication | 10% | Clear report connecting distributions to decisions |
| Reproducibility | 10% | Seeded throughout with intervals on estimates |

## 8. Stretch Goals

- Add importance sampling for rare-event probability estimation.
- Add a negative binomial and a Weibull, comparing likelihoods on real data.
- Add simulation-based calibration for a model with hard-to-evaluate tails.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Normal, binomial, Poisson and exponential with verified normalisation.
- [ ] Log-space evaluation with a stability comparison against the naive formula.
- [ ] Normal approximation with a continuity correction and an automatic validity gate.
- [ ] Seeded samplers validated against theoretical moments with sampling-aware tolerances.
- [ ] Overdispersion detection on real-shaped operational data, with an alternative model compared.
- [ ] Monte Carlo estimator with intervals and a convergence check.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
