# Principal Component Analysis - Vision & Where This Is Going

**Track:** ml  |  **Lab:** lab08  |  **Level:** Intermediate

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

PCA stays the default first move for linear preprocessing, but the frontier has moved to embeddings for non-linear structure and to supervised projections when the label matters. Its role shifts from 'feature reduction' to 'conditioning for the next stage'.

The test of that future state is boring: a new engineer ships a change to principal component analysis on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- The transform artifact contains mean, scale and components as one versioned unit.
- Scaling or not is an explicit, recorded decision.
- k is chosen by downstream validation, with cumulative variance as a diagnostic.
- Interpretations are stated at the component level when features are correlated.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Reduce | Fit PCA, keep 95%, plot the scores. |
| L2 | Decide correctly | Justify scaling, choose k by validation, check the spectrum. |
| L3 | Condition | Use PCA to fix collinearity or dimensionality for another model, and prove the gain. |
| L4 | Go beyond linear | Compare against an embedding or a supervised projection on the same task. |

## 4. Behaviours to Build

State the scaling decision before fitting. Choose k with a validation curve. Treat components as the interpretable unit, not coefficients.

## 5. Anti-Vision (the failure mode we are avoiding)

- SVD because a tutorial said PCA, on a sparse count matrix.
- A PCA transform shipped without its mean and scale.
- k = 95% variance rule quoted as a decision.
- PCA loadings presented to a stakeholder as feature importance.

## 6. Technology Shifts That Change the Work

1. Autoencoders and embedding models replacing PCA where structure is non-linear.
1. Supervised dimensionality reduction when the label carries the signal.
1. Incremental and randomised PCA for streaming and very wide data.
1. Whitening and kernel PCA as preprocessing for k-means and k-NN in embedding spaces.

## 7. Your 30/60/90 Commitment

- **30 days.** Implement PCA by eigendecomposition and verify explained ratios sum to 1.
- **60 days.** Cross-check against SVD and explain the numerical difference.
- **90 days.** Choose k by downstream validation, compare with an embedding, and ship a versioned transform with a drift check.

## 8. How To Tell You Are Actually Getting Better

- I can derive PCA from the constrained optimisation.
- I justify the scaling decision explicitly.
- I choose k with a validation curve.
- My transform artifact is complete enough to reproduce scoring exactly.

## 9. Principles That Should Not Change

- **Derive PCA as the projection that maximises variance** Derive PCA as the projection that maximises variance
- **Implement PCA via eigendecomposition of the covariance matrix** Implement PCA via eigendecomposition of the covariance matrix and via SVD of the centred data
- **Compute explained variance ratio** Compute explained variance ratio and choose k with a cumulative-variance target

> PCA is where you learn that retained variance and retained signal are different things — a lesson that outlasts the algorithm.
