# Model Interpretability — Internals

## Permutation engine
Holds the scored baseline, then per feature generates K shuffled column
copies (seeded), scores each, and averages drops. Shuffling is a column
permutation in place on a copied matrix; the model is never retrained
inside this loop. Cost is features times shuffles times scoring passes.

## PDP engine
Caches background rows once, then per grid point broadcasts the grid
value across the background copy and scores. Vectorize across grid
points; reuse the same background for all features so curves are
comparable. Flag grid points whose neighborhood holds few background
rows.

## LIME engine
Samples neighbors (Gaussian or discrete perturbations around x0),
evaluates the model per neighbor, weights by the kernel, and solves
weighted least squares in closed form for low-dimensional surrogates.
The demo's 5-point fit is the minimal shape; production uses hundreds
of neighbors with feature selection on the surrogate.

## SHAP engine
Enumerates coalitions for few features (2^n evaluations) or samples
orders/permutations for many. Each evaluation needs a baseline-filled
input for absent features — the baseline choice is load-bearing. The
efficiency sum is checked before returning; violations indicate
inconsistent value-function construction.

## Stability layer
Wraps every engine: rerun with perturbed seed/width/baseline, report
rank correlation (permutation), curve bands (PDP), coefficient ranges
(LIME), attribution ranges (SHAP). Unexplained variance across reruns
blocks stakeholder release.
