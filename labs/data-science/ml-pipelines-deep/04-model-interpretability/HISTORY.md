# Model Interpretability — History (confident facts only)

## What can be said safely
- Shapley values come from Lloyd Shapley's cooperative game theory
  (1950s); the efficiency/symmetry/dummy/additivity characterization
  is the standard textbook presentation. Their ML attribution use is
  much later.
- Ribeiro et al., "Why Should I Trust You?" (2016), introduced LIME:
  local interpretable model-agnostic explanations via perturbed
  sampling plus local surrogates. The year and authors are the safe
  citation.
- Lundberg and Lee (2017) introduced SHAP, unifying several
  attribution methods under Shapley values. The year and authors are
  the safe citation; venues should be checked in library catalogs
  rather than asserted here.
- Permutation importance and partial dependence are standard textbook
  tools (Hastie, Tibshirani, Friedman present PDP and variable
  importance); they predate the 2016-2017 local-explanation wave.
- The accuracy-interpretability discussion runs through the Breck and
  Sculley programs on production ML: explanations serve audit and
  debugging before they serve stakeholder persuasion.

## Mechanism depth on the existing entries
- Permutation importance deepened: shuffling preserves the marginal
  distribution while breaking the conditional link, which is why the
  demo reports importance as baseline minus permuted accuracy
  (1.0 - 0.6667 = 0.3333) rather than a model-internal weight.
- PDP deepened: the grid-average construction is what creates both its
  strength (marginal response in data-distribution terms) and its
  weakness (averaging over feature combinations with no observed
  support, such as mismatched height/weight pairs).
- LIME deepened: the 2016 contribution was the perturbed-sample plus
  kernel-weight plus local-surrogate recipe; the demo slope near 4.0
  against the true gradient 2x0 = 4 shows the recipe working where the
  kernel width keeps samples genuinely local.
- SHAP deepened: the 2017 contribution was unifying prior attribution
  methods as Shapley-value estimators; the demo split 5.5/4.5 of 10.0
  is the efficiency axiom made checkable on a two-player game.

## What this lab does not claim
No priority claims beyond the named papers, no venue/year assertions
where uncertain, no adoption statistics. Axioms are stated as axioms;
paper contributions are described at concept level.
