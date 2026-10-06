# classical-ml-deep

Deep track for classical machine learning in Java 21 — ten modules from linear regression
through gradient boosting, dimensionality reduction, clustering, and anomaly detection.
Every algorithm is implemented by hand: no external dependencies, no frameworks.

## Track Contents

Ten sub-modules, each with its own theory, exercises, quiz, and a `*Algorithm.java` plus
test pair under `src/`:

| # | Module | Focus |
|---|--------|-------|
| 01 | `01-linear-regression` | OLS closed form, gradient descent, R-squared, adjusted R-squared, multicollinearity |
| 02 | `02-logistic-regression` | Sigmoid, log-odds, cross-entropy, Newton-Raphson, IRLS, multiclass softmax |
| 03 | `03-svm-theory` | Maximum margin, support vectors, Lagrangian dual, kernel trick, RBF, SMO |
| 04 | `04-decision-trees` | ID3 info gain, C4.5 gain ratio, CART Gini, pruning, regression trees, missing values |
| 05 | `05-random-forest` | Bootstrap aggregation, random subspace, OOB error, feature importance, proximity |
| 06 | `06-gradient-boosting` | Forward stagewise, XGBoost histogram/quantile, LightGBM GOSS/EFB, CatBoost ordered TS |
| 07 | `07-dim-reduction-pca` | Covariance matrix, eigenvalue decomposition, explained variance, kernel PCA |
| 08 | `08-clustering-kmeans` | k-means++, Lloyd/Elkan/Hartigan-Wong, elbow/silhouette/gap |
| 09 | `09-clustering-dbscan` | Epsilon/minPts, core/border/noise, DBSCAN vs HDBSCAN, OPTICS, hierarchical |
| 10 | `10-anomaly-detection` | Z-score, IQR, isolation forest, LOF, autoencoder, one-class SVM |

## Track-Level Documents

| File | What it is |
|------|-----------|
| `INDEX.md` | Module list with one-line focus per module |
| `THEORY.md` | Mechanism, assumption, and failure mode for each of the ten modules |
| `EXERCISES.md` | ~85 tagged exercises across all modules plus four cross-module tasks |
| `QUIZ.md` | 15 multiple-choice questions with answer key and score guide |
| `FLASHCARDS.md` | 60-row recall table |
| `MATH_FOUNDATION.md` | Derivations with worked numbers: normal equations, boosting, PCA, k-means, DBSCAN |
| `CODE_DEEP_DIVE.md` | Java implementations: QR solve, IRLS, SMO-style SVM, SVD/PCA, k-means++, DBSCAN, LOF |
| `VISION.md` | Mastery path, milestones, anti-goals, 30-day plan |
| `MINI_PROJECT.md` | A tabular ML workbench: 14 phases, 14 milestones |
| `REAL_WORLD_PROJECT.md` | Credit risk scoring platform with governance and monitoring |

## How to Work Through This Track

1. **Read `THEORY.md`** and note the failure mode of each algorithm. The failure modes
   are what make the knowledge durable; the formulas are lookup-able.
2. **Work `EXERCISES.md`** in module order. Each module starts at **E** and ends at **H**;
   the hard exercises are where the intuition actually forms.
3. **Retake `QUIZ.md`** until 13/15 with no misses on the collinearity, CatBoost,
   DBSCAN-noise, and imbalanced-metric questions.
4. **Drill `FLASHCARDS.md`** on a 20-minute daily cadence.
5. **Do `MATH_FOUNDATION.md`** after the exercises — the derivations are the difference
   between recognizing a formula and understanding why it holds.
6. **Implement from `CODE_DEEP_DIVE.md`** without reading ahead; compare afterwards.
7. **Build the mini project**, then design the real-world project for a domain you care
   about.

## What You Will Be Able To Do

- Explain what each algorithm assumes and the specific way it fails when that assumption
  breaks.
- Choose between linear, kernel, tree, and ensemble models on tabular data with a
  defended argument.
- Diagnose a model that is not learning — leakage, imbalance, collinearity, wrong
  objective, wrong split.
- Implement the core algorithms from scratch and verify them against numerical
  properties rather than against a reference library.
- Report the right metric for the problem: PR-AUC for imbalance, calibration error for
  probabilities, learning curves for bias-variance, not accuracy for anything.
