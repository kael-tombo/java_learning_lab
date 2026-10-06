# MINI_PROJECT — Pre-Registered Experiment with Honest Inference

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

**Brief.** Design a powered test, run it, and report the result with an effect size, an interval and an honest conclusion.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

Everything in this lab exists to prevent one specific failure: a confident claim that a small noisy difference is a result.

## 2. Requirements

- Pre-registered plan: hypothesis, direction, alpha, power, sample size and stopping rule.
- Implementation of one-sample, Welch two-sample, paired t and chi-square, all verified by hand.
- Effect size and confidence interval attached to every result, structurally.
- Assumption checks with reporting notes for violated assumptions.
- Power and MDE computed before data collection; achievable MDE reported.
- Simulation measuring the false positive rate of a daily-look process versus a fixed-horizon process.
- Written analysis reporting the decision in business units.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Pre-registration with power and sample size | A plan with real arithmetic |
| 2 | 40m | Implement the tests with effect sizes and intervals | A verified suite |
| 3 | 25m | Assumption checks with reporting notes | Assumption-violation handling |
| 4 | 30m | Run on realistic data; report effect and interval | A result with magnitude |
| 5 | 30m | False positive simulation for daily looks | An inflation measurement |
| 6 | 25m | Non-significant result reported with power | An honest inconclusive report |
| 7 | 30m | Business translation and decision memo | A decision memo |

## 4. Architecture Sketch

```text
 pre-registration: H0, direction, alpha, power, n, stopping rule
     |
 data collection (fixed horizon)
     |
 [1] assumption checks --> notes when violated
 [2] statistic + df + p from the correct distribution
 [3] effect size + confidence interval (attached, always)
     |
 decision: significant --> effect interval -> business units
           inconclusive --> power + interval (never "no effect")
     |
 simulation: false positive rate, daily-look vs fixed-horizon
```

## 5. Implementation Notes

- Write the plan before writing the data pipeline, or you will rationalise the outcome.
- Include one deliberately underpowered case and report it honestly.
- The daily-look simulation makes the inflation concrete; use your own metric if you have one.
- The decision memo must be writable without mentioning a p-value.

## 6. Deliverables

1. Pre-registration document with power arithmetic.
1. Verified test suite with effect sizes attached by construction.
1. False positive comparison between daily looks and a fixed horizon.
1. Analysis write-up plus a decision memo in business units.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Design | 25% | Pre-registered with real power and sample size arithmetic |
| Correctness | 25% | Tests verified, correct df, assumptions checked |
| Honesty | 30% | Effect size and interval always; power on inconclusive |
| Discipline | 10% | Multiple looks and multiplicity accounted for |
| Communication | 10% | Decision memo in business units |

## 8. Stretch Goals

- Add a sequential design and compare time-to-decision at equal error rates.
- Add permutation and bootstrap alternatives for assumption-light results.
- Add equivalence or non-inferiority framing for a practical-significance question.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Pre-registered plan: hypothesis, direction, alpha, power, sample size and stopping rule.
- [ ] Implementation of one-sample, Welch two-sample, paired t and chi-square, all verified by hand.
- [ ] Effect size and confidence interval attached to every result, structurally.
- [ ] Assumption checks with reporting notes for violated assumptions.
- [ ] Power and MDE computed before data collection; achievable MDE reported.
- [ ] Simulation measuring the false positive rate of a daily-look process versus a fixed-horizon process.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
