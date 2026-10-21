# Model Interpretability — Architecture

## Components
1. Explainer router: maps the stated question to a method (global vs
   local) and records the choice.
2. Background store: reference rows for PDP averaging and SHAP
   baselines, versioned with the dataset.
3. Perturbation sampler: neighbor generator with kernel weights for
   LIME-style surrogates.
4. Surrogate fitter: weighted least squares for local linear models.
5. Attribution engine: coalition enumeration/approximation for Shapley
   values with an efficiency check.
6. Stability checker: reruns explanations under perturbed settings and
   reports spread.
7. Report sink: explanations plus settings into the run record.

## Data flow
Model + dataset version + question -> router -> method with background
data -> raw explanation -> stability check -> report with settings.

## Key interfaces
- `permutationImportance(model, data, seed)`: per-feature accuracy
  drops with shuffle counts.
- `pdp(model, background, feature, grid)`: averaged response curve.
- `limeExplain(f, x0, kernelWidth, n)`: surrogate coefficients.
- `shapley(v, baseline)`: per-feature attributions summing to total.

## Ordering guarantees
Explanations always reference a registered model version and dataset
version; background data never includes test rows used for final
scoring. Stability reruns precede any stakeholder-facing report.

## Scaling notes
Permutation and PDP scale with features times scoring passes; exact
Shapley enumeration is exponential in features (fine for 2, sampled
beyond); LIME scales with neighbor count times model calls. Budget
accordingly and cache background aggregates.
