# Probability Distributions - Vision & Where This Is Going

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

## 1. The Future State

Distributions remain the vocabulary for reasoning under uncertainty, with heavy-tailed and compound families replacing normals wherever real operational data lives. The frontier is diagnostics: knowing which family a process belongs to, quickly, rather than assuming it.

The test of that future state is boring: a new engineer ships a change to probability distributions on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- The variable is classified before a family is chosen.
- Assumptions are checked, especially rate constancy and independence.
- Tails are evaluated in log space with stated approximation validity.
- Simulations are seeded and reported with intervals.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Evaluate | PDF, PMF and CDF for the four standard families. |
| L2 | Approximate | Normal approximations with validity checks and continuity correction. |
| L3 | Sample | Seeded samplers validated against theoretical moments. |
| L4 | Diagnose | Detect overdispersion and rate variation, and choose alternatives. |

## 4. Behaviours to Build

Check the assumptions before trusting the family. Evaluate tails in log space. Seed everything, and report simulation results with intervals.

## 5. Anti-Vision (the failure mode we are avoiding)

- A Poisson model on hourly traffic that visibly varies with time of day.
- A tail probability computed as 1 minus a CDF in double precision.
- A simulation reported without a seed, an interval or a validation check.

## 6. Technology Shifts That Change the Work

1. Heavy-tailed and compound distributions for operational metrics like latency and claim size.
1. Automatic family selection with diagnostic tests rather than assumption by habit.
1. Bayesian posterior predictive checks replacing goodness-of-fit tables.
1. Simulation-based calibration for models whose tails cannot be evaluated.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement the four standard distributions with verified normalisation.
- **60 days.** Make all tail evaluation stable and gate approximations with validity checks.
- **90 days.** Build validated seeded samplers and detect overdispersion with an alternative model.

## 8. How To Tell You Are Actually Getting Better

- I check assumptions before trusting a family.
- My tails are computed stably.
- My approximations state their validity conditions.
- My simulations are reproducible and reported with intervals.

## 9. Principles That Should Not Change

- **Distinguish discrete from continuous distributions** Distinguish discrete from continuous distributions and pick between them
- **Implement normal, binomial, Poisson** Implement normal, binomial, Poisson and exponential densities and CDFs
- **Compute CDF values without a lookup table, using approximations with stated error** Compute CDF values without a lookup table, using approximations with stated error

> Most statistical mistakes with distributions are not arithmetic errors; they are confident applications to data the family does not describe.
