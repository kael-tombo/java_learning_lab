# Model Interpretability — Interview

## Q: Global vs local — give me one method each.
A: Global: permutation importance (demo drop 0.3333 for x1) or PDP
curves. Local: LIME surrogate coefficients or SHAP attributions for one
prediction. The question selects the tool, never the reverse.

## Q: How does permutation importance work?
A: Shuffle one feature, remeasure accuracy, take baseline minus
permuted. Demo: 1.0 baseline, 0.6667 permuted, importance 0.3333. It
breaks the feature-label link while keeping the marginal distribution.

## Q: What is LIME at concept level?
A: Ribeiro 2016: sample perturbed points near x0, weight by kernel
proximity, fit an interpretable surrogate, read coefficients. Demo on
x^2 at x0=2 recovers slope ~4.0, the true gradient — under width 0.3,
which must be reported.

## Q: State the Shapley axioms.
A: Efficiency (shares sum to total gain — demo 5.5+4.5=10.0),
symmetry (identical contributors share equally), dummy (zero
contribution gets zero), additivity (values add across games). SHAP
(Lundberg/Lee 2017) is the ML attribution built on them.

## Q: Work the demo game by hand.
A: v({})=0, v({1})=4, v({2})=3, v({1,2})=10. Orders (1,2): margins 4
then 6; (2,1): 3 then 7. Averages: phi1=5.5, phi2=4.5. Efficiency holds.

## Q: Why might two LIME runs disagree?
A: Different kernel widths, samples, or surrogate classes — all
settings, not model facts. Stability reruns quantify the spread before
any stakeholder sees the explanation.

## Q: An ID column tops importance. Finding or bug?
A: Bug until proven otherwise: probable label leakage. Verify with
group-aware splits and remove the leak at the pipeline, not by hiding
the feature from the explainer.
