# Experimental Design - Vision & Where This Is Going

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

## 1. The Future State

Experimental design converges with causal inference: pre-registration, estimand-first framing and sensitivity analysis as standard practice, with platform-level randomisation replacing one-off studies. The persisting skill is writing the estimand before the design.

The test of that future state is boring: a new engineer ships a change to experimental design on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Estimands are written before designs are fixed and stored with the data.
- Sample sizes come from a power calculation with an inflated variance.
- Randomisation is seeded, recorded and audited.
- Analyses are pre-specified including interactions and planned contrasts.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Size | Sample size from alpha, power and MDE. |
| L2 | Block | Blocking variables chosen in advance with a quantified variance gain. |
| L3 | Structure | Factorial designs with interaction testing and replication. |
| L4 | Pre-specify | Estimand, analysis plan and sensitivity analysis committed before data. |

## 4. Behaviours to Build

Write the estimand first. Compute power before collecting. Block on the dominant nuisance variance. Test interactions before interpreting main effects.

## 5. Anti-Vision (the failure mode we are avoiding)

- A study run without a power calculation and concluded inconclusive.
- Main effects reported on a design with a significant interaction.
- A pilot variance used uncritically to size a definitive study.
- Post-hoc analysis choices presented as pre-specified.

## 6. Technology Shifts That Change the Work

1. Estimand-first framing adopted as standard in platform experimentation.
1. Pre-registration with sequential designs for continuous monitoring.
1. Sensitivity analysis to unmeasured confounding as standard reporting.
1. Response surface methodology for continuous factor levels.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement sample size and power calculations for means and proportions.
- **60 days.** Add blocking with a quantified variance gain and a factorial analysis.
- **90 days.** Write a pre-specified analysis plan and simulate the design to validate the power.

## 8. How To Tell You Are Actually Getting Better

- My estimand is written and estimable.
- My sample size came from a power calculation.
- I blocked on the dominant nuisance variance.
- I test the interaction before reporting main effects.

## 9. Principles That Should Not Change

- **State the estimand** State the estimand and the unit of randomisation explicitly
- **Compute sample size for means** Compute sample size for means and proportions from alpha, power and MDE
- **Choose between completely randomised, blocked** Choose between completely randomised, blocked and factorial designs

> No analysis repairs a design that was never specified, and most unexplained results are exactly that.
