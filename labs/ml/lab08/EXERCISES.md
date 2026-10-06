# Principal Component Analysis - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab08
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.ml.lab08.Main
```

## Exercise 1: Derive and implement PCA by eigendecomposition

**Task.** Build the covariance matrix and solve the symmetric eigenproblem.

**Steps**
- Centre and standardise a 4-feature dataset.
- Build the covariance matrix and run Jacobi.
- Sort descending and fix the sign convention.
- Project to 2 components and reconstruct; report the error.

**Deliverable.** A PCA implementation plus a reconstruction error matching 1 - cumulative k.

## Exercise 2: Eigen versus SVD must agree

**Task.** Two routes, one answer — this is the numerics lesson.

**Steps**
- Implement truncated SVD of the centred matrix.
- Relate singular values to eigenvalues via lambda = s²/(n-1).
- Assert components agree up to sign within 1e-8.
- Explain why SVD is preferable at large p.

**Deliverable.** A passing cross-check test and a written numerical argument.

## Exercise 3: Choosing k honestly

**Task.** Beat the 95% convention with evidence.

**Steps**
- Sweep k = 1..p and record cumulative variance.
- Train a downstream model per k; cross-validate.
- Plot validation error against k.
- Choose k from the curve and explain where it sits versus the variance rule.

**Deliverable.** Two curves and a k chosen from the downstream one.

## Exercise 4: Loadings versus importance

**Task.** Show why PCA coefficients are not feature importance.

**Steps**
- Fit PCA on data with two strongly correlated features.
- Compare loadings against a tree's permutation importance.
- Show loadings are unstable across bootstrap samples while components are stable.
- Explain what the component, not the coefficient, means.

**Deliverable.** A comparison table plus a written interpretation rule.

## Exercise 5: Whitening for clustering

**Task.** Fix non-spherical clusters with a linear transform.

**Steps**
- Generate three clusters with different variances.
- Cluster raw: report silhouette.
- Apply PCA then whitening; re-cluster.
- Report the silhouette change and why.

**Deliverable.** Before/after silhouettes with a written explanation.

## Exercise 6: Sparsity stress test

**Task.** See where covariance PCA fails and TruncatedSVD wins.

**Steps**
- Build a sparse term-count matrix.
- Apply PCA with explicit densification; measure cost.
- Apply truncated SVD without centring; measure cost and quality.
- Recommend one for text.

**Deliverable.** A cost comparison and a written recommendation.

## Exercise 7: PCA as leakage canary

**Task.** Prove that fitting PCA on everything leaks.

**Steps**
- Run a pipeline with in-fold versus full-dataset PCA.
- Compare cross-validated scores.
- Quantify the optimism.
- Add a test asserting PCA is fit inside the fold.

**Deliverable.** A quantified optimism number and a regression test.

## Exercise 8: Ship a compression transform

**Task.** Reduce serving payload while monitoring the loss.

**Steps**
- Serialise the PcaModel to a compact text format; reload it.
- Assert reload reproduces predictions exactly.
- Report compression ratio and downstream error delta on a test set.
- Add a drift check comparing incoming variance to the fitted spectrum.

**Deliverable.** A working loader, a parity test and a drift check.


---

## Self-Check Before You Move On

- [ ] I can derive PCA from the constrained optimisation
- [ ] I can justify standardising (or not) for my data
- [ ] I chose k with evidence beyond a variance threshold
- [ ] My transform artifact is complete and self-consistent
