# Model Interpretability — Flashcards

Q: Global vs local explanation?
A: Global describes the model everywhere (importance ranks, PDP);
local explains one prediction (LIME coefficients, SHAP shares).

Q: Permutation importance definition?
A: Baseline accuracy minus accuracy after shuffling one feature.
Demo: 1.0 - 0.6667 = 0.3333 for x1.

Q: Why does correlation distort permutation ranks?
A: Shuffling one of a correlated pair leaves the other carrying the
signal, understating both. Read joint behavior.

Q: PDP in one sentence?
A: Model output vs one feature, averaged over the other features'
observed values at each grid point.

Q: LIME concept (Ribeiro 2016)?
A: Sample near x0, weight by proximity, fit an interpretable
surrogate, read its coefficients as the local explanation.

Q: Demo LIME numbers?
A: f(x)=x^2 at x0=2: slope 3.9999999999999982 (true gradient 4.0),
intercept 4.057135543484657.

Q: SHAP concept (Lundberg/Lee 2017)?
A: Shapley-value attribution: average marginal contribution over
joining orders; unique under the four axioms.

Q: The four Shapley axioms?
A: Efficiency (shares sum to total gain), symmetry (equals share
equally), dummy (non-contributors get zero), additivity (values add
across games).

Q: Demo Shapley numbers?
A: phi1=5.5, phi2=4.5, sum=10.0=v({1,2}), efficiency holds.

Q: Interpretability-vs-accuracy framing?
A: Simple models read directly but may underfit; rich models need
post-hoc tools whose faithfulness and stability must be checked.

Q: The stability caveat in one line?
A: Every explanation depends on settings (seeds, widths, baselines) —
rerun perturbed before acting.
