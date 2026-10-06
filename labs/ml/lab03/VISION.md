# Decision Trees & Random Forests - Vision & Where This Is Going

**Track:** ml  |  **Lab:** lab03  |  **Level:** Intermediate

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

Trees remain the workhorse for tabular data and the default interpretable model. The direction is not bigger forests but diagnostic ones: honest importance, out-of-distribution detection, and monotonic or shape constraints so the model cannot encode a rule the business forbids.

The test of that future state is boring: a new engineer ships a change to decision trees & random forests on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Every forest reports OOB or held-out error next to its training error.
- Importance is permutation-based with error bars, or omitted entirely.
- Depth and leaf size come from a validation curve and are recorded in the model card.
- Categorical encoding is decided once, documented, and enforced in tests.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Grow a tree | Split on information gain, stop on depth, report accuracy. |
| L2 | Tune the stopping rule | Find the depth/leaf-size knee on a validation curve. |
| L3 | Ensemble properly | Add bagging and feature randomness; quantify diversity and OOB error. |
| L4 | Make it trustworthy | Permutation importance, OOD detection, constrained splits, documented in a model card. |

## 4. Behaviours to Build

Print the tree before the accuracy. Prefer honest held-out numbers over flattering training curves. Treat an identifier column as a bug until proven otherwise.

## 5. Anti-Vision (the failure mode we are avoiding)

- Reporting impurity importance as if it were a business explanation.
- A 20-deep tree shipped because 'more depth means better'.
- 500 trees when 100 made no difference, doubling latency for nothing.
- Feeding raw IDs and then removing the feature that mattered most.

## 6. Technology Shifts That Change the Work

1. Gradient-boosted trees taking over most tabular workloads, with forests as the robust baseline.
1. Explainable Boosting Machines: monotone and shape constraints on inputs and interactions.
1. Quantile forests for uncertainty bands instead of point predictions.
1. Tree-based OOD detection (isolation forests, Mahalanobis in leaf space).

## 7. Your 30/60/90 Commitment

- **30 days.** Implement CART with entropy and a stopping rule; verify the root split by hand.
- **60 days.** Build the forest with per-tree seeds, mtry and OOB error; compare against plain bagging.
- **90 days.** Add permutation importance with repeats and publish a model card stating the depth you chose and why.

## 8. How To Tell You Are Actually Getting Better

- I can quote OOB or held-out error, never training accuracy alone.
- I can explain why my forest is better than a single tree in one sentence involving variance.
- My importance ranking survives a permutation test.
- My forests reproduce exactly across runs.

## 9. Principles That Should Not Change

- **Compute entropy** Compute entropy and Gini impurity and pick the split that maximises impurity reduction
- **Implement CART regression** Implement CART regression and classification trees with a stopping rule
- **Explain bagging: bootstrap resampling plus decorrelated feature subsets** Explain bagging: bootstrap resampling plus decorrelated feature subsets

> A forest you can interrogate is worth more than a slightly higher score you cannot explain.
