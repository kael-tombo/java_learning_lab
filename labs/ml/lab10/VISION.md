# Model Evaluation - Vision & Where This Is Going

**Track:** ml  |  **Lab:** lab10  |  **Level:** Intermediate

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

Evaluation moves toward protocol-as-code: versioned evaluation suites that run in CI, offline metrics tracked against online outcomes, and continuous evaluation on shadow traffic. The metric ceases to be a report and becomes a deployment gate.

The test of that future state is boring: a new engineer ships a change to model evaluation on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Every reported number ships with its interval, baseline, protocol and seed.
- Fold strategy is asserted, not assumed: groups split by group, time by time.
- Rare-positive tasks quote PR-AUC and precision at the operating point.
- Thresholds come from cost matrices stored next to the model.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Measure | Compute a confusion matrix and accuracy honestly. |
| L2 | Be careful | Stratified folds, in-fold preprocessing, PR-AUC for rare classes. |
| L3 | Be rigorous | Intervals, paired model comparison, repeated CV. |
| L4 | Gate | Run the protocol in CI and block promotion on regression. |

## 4. Behaviours to Build

Print the confusion matrix first. Choose the protocol that matches how the data was generated. Treat a difference smaller than your interval as no difference.

## 5. Anti-Vision (the failure mode we are avoiding)

- Accuracy on a 1% positive class as a headline.
- Shuffled cross-validation on time series.
- Preprocessing fit before splitting.
- A/B-testing a model on a difference well inside the noise band.

## 6. Technology Shifts That Change the Work

1. Continuous evaluation on shadow traffic with offline/online metric correlation tracking.
1. Evaluation suites as code, gated in CI, with leakage assertions.
1. Slice-based evaluation: performance per segment, not only in aggregate.
1. Statistically rigorous experiment design (sequential testing, CUPED variance reduction).

## 7. Your 30/60/90 Commitment

- **30 days.** Build the metric suite from the confusion matrix and cross-check by hand.
- **60 days.** Implement stratified, grouped and forward-chaining folds with leakage assertions.
- **90 days.** Add bootstrap intervals, a paired comparison between two models, and a reproducible report someone else can rerun.

## 8. How To Tell You Are Actually Getting Better

- I always print the confusion matrix and the trivial baseline.
- My splits match how the data was generated.
- I quote an interval with every headline number.
- I can justify ROC versus PR for my task.

## 9. Principles That Should Not Change

- **Build a confusion matrix correctly** Build a confusion matrix correctly and derive every metric from it
- **Explain why accuracy fails under class imbalance** Explain why accuracy fails under class imbalance and what to use instead
- **Compute ROC-AUC** Compute ROC-AUC and the PR curve, and know which to trust when

> An evaluation protocol is the only thing standing between you and a model that is confidently worse than doing nothing.
