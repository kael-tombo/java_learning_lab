# MINI_PROJECT — Bayesian A/B Evaluation with Verified Posteriors

**Track:** statistics  |  **Lab:** lab06  |  **Level:** Advanced

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

**Brief.** Analyse a conversion experiment as a posterior comparison, with prior checks, convergence diagnostics and a decision probability.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

This is the deliverable a business actually wants: the probability that one option beats another, with its uncertainty.

## 2. Requirements

- Conjugate beta-binomial posterior with an HDI, verified against sampled draws.
- Three defensible priors with a sensitivity analysis and a stated conclusion.
- Prior predictive check that passes before fitting.
- MCMC or sampling with R-hat and effective sample size enforced before summarising.
- P(variant beats control) with a Monte Carlo interval, compared with a point-estimate comparison.
- Posterior predictive check for an alternative model to detect misspecification.
- A report whose headline is a probability.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Conjugate posterior and HDI; verify against samples | A verified posterior |
| 2 | 30m | Three priors with a sensitivity table | A sensitivity conclusion |
| 3 | 25m | Prior predictive check | A passing predictive check |
| 4 | 35m | Sampler with R-hat and ESS enforced | Verified draws |
| 5 | 30m | P(A beats B) with a Monte Carlo interval | A decision probability |
| 6 | 30m | Posterior predictive check on an alternative model | A misspecification detection |
| 7 | 30m | Report with the probability as the headline | A business-facing report |

## 4. Architecture Sketch

```text
 experiment data (conversions / exposures per arm)
    |
 [1] prior predictive check  -> fails? adjust the prior
 [2] three defensible priors -> posterior per arm per prior
 [3] sensitivity table -> conclusion qualified if priors disagree
 [4] sampler with R-hat + ESS enforced before any summary
 [5] HDI per arm, and P(A > B) with Monte Carlo interval
 [6] posterior predictive check on an alternative model
    |
 decision memo: P(variant beats control) as the headline
```

## 5. Implementation Notes

- Run the prior predictive check first; a prior that cannot generate your data makes every later step meaningless.
- Enforce convergence in code so an interval cannot be printed from unverified draws.
- Report the Monte Carlo interval on P(A > B); a bare probability invites over-precision.
- The decision memo should be readable by someone who has never heard the word posterior.

## 6. Deliverables

1. Conjugate posterior with HDI, verified against samples.
1. Prior sensitivity table across three defensible priors.
1. Sampler with enforced diagnostics and a passing prior predictive check.
1. Decision memo whose headline is P(variant beats control) with an interval.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Prior discipline | 25% | Rationale stated, predictive check run, sensitivity reported |
| Inference | 25% | Convergence enforced, HDIs computed correctly |
| Decision | 30% | P(A > B) with a Monte Carlo interval and honest comparison |
| Model checking | 10% | Posterior predictive check catches a misspecification |
| Communication | 10% | Memo readable by a non-statistician |

## 8. Stretch Goals

- Add a model with an over-dispersed likelihood and compare posteriors.
- Add a decision-theoretic layer converting the probability into expected value.
- Extend to a continuous outcome with a conjugate normal model.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Conjugate beta-binomial posterior with an HDI, verified against sampled draws.
- [ ] Three defensible priors with a sensitivity analysis and a stated conclusion.
- [ ] Prior predictive check that passes before fitting.
- [ ] MCMC or sampling with R-hat and effective sample size enforced before summarising.
- [ ] P(variant beats control) with a Monte Carlo interval, compared with a point-estimate comparison.
- [ ] Posterior predictive check for an alternative model to detect misspecification.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
