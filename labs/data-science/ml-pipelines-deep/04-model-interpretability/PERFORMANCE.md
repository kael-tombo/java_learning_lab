# Model Interpretability — Performance

## Cost structure
Permutation importance costs features times shuffles times a scoring
pass each — linear and parallel across features. PDP costs grid points
times background size times scoring — the background multiplier
dominates. LIME costs neighbors times model calls plus one small least
squares solve. Exact Shapley is exponential in features; sampling
converts it to a budgeted approximation.

## Throughput tactics
- Score once per (feature, shuffle) with batched model calls rather
  than one call per row.
- Share one background sample across all PDP features and cache model
  outputs per background row where the model is deterministic.
- Parallelize coalition evaluations; they are independent given the
  value function.

## Latency tactics
- Local explanations for single predictions need small neighbor counts
  and cached backgrounds to meet interactive budgets.
- Precompute global artifacts (ranks, PDP grids) on release; serve
  them as static reports rather than recomputing per request.

## Approximation honesty
Sampled SHAP and few-shuffle importance are estimates with spread —
report the spread from the stability reruns, not just the mean. A fast
explanation without uncertainty is a guess with formatting.

## Scale honesty
Demo costs (6 rows, 5 neighbors, 2 players) illustrate mechanics only.
Production budgets follow the complexity statements above, sized to
the team's model-call cost and feature count.
