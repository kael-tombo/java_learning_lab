# AutoML Pipelines - Vision & Where This Is Going

**Track:** mlops  |  **Lab:** lab14  |  **Level:** Advanced

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

AutoML converges on multi-objective tuning that treats accuracy, latency and fairness jointly, with surrogate models warmed from previous runs and early stopping driven by learned convergence prediction. The discipline that matters stays statistical, not algorithmic.

The test of that future state is boring: a new engineer ships a change to automl pipelines on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Search spaces are log-scaled, bounded and pruned before launching.
- Budgets are allocated with early stopping rather than spent uniformly.
- Final numbers come from data not used for selection, against a baseline.
- Every trial is logged with configuration, code version and data version.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Search | Grid or random search over a constrained space. |
| L2 | Allocate | Successive halving so the budget follows the leaders. |
| L3 | Be honest | Nested validation or a final holdout, plus variance across seeds. |
| L4 | Optimise jointly | Multi-objective tuning over accuracy, latency and fairness. |

## 4. Behaviours to Build

Constrain the space, allocate the budget, and never report a best-of-N score as performance. Compare against a baseline every time.

## 5. Anti-Vision (the failure mode we are avoiding)

- A 200-trial search reported as a 4% improvement with no holdout.
- Grid search on a learning rate from 1e-6 to 1.
- A tuned result compared against nothing.
- Selection decided on one validation fold with no variance estimate.

## 6. Technology Shifts That Change the Work

1. Multi-objective tuning producing Pareto fronts over accuracy, latency and cost.
1. Learned convergence predictors enabling aggressive early stopping.
1. Warm-started surrogates across related models and datasets.
1. Population-based methods for robustness across seeds.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement grid and random search over a log-scaled, pruned space.
- **60 days.** Add successive halving and compare budget allocation against uniform.
- **90 days.** Implement nested validation, quantify selection bias, and publish a tuning report with variance.

## 8. How To Tell You Are Actually Getting Better

- My reported improvement is not selection bias.
- My search space is log-scaled and pruned.
- My budget was allocated, not spent uniformly.
- I report against a baseline with a variance estimate.

## 9. Principles That Should Not Change

- **Implement grid, random** Implement grid, random and Bayesian hyperparameter search
- **Allocate budget across configurations with early stopping** Allocate budget across configurations with early stopping
- **Recognise overfitting to the validation set** Recognise overfitting to the validation set and choose a protocol that avoids it

> Tuning is easy to automate and easy to fool yourself with; the statistical discipline is the actual work.
