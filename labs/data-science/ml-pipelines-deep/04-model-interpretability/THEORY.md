# Model Interpretability — Theory

## 1. Global vs local
A global explanation describes the model everywhere (which features
matter overall, how outputs vary with inputs). A local explanation
describes one prediction (why this item scored this way). Methods do
not transfer automatically: a globally important feature can be
irrelevant at a given point and vice versa. State which question you
answer before picking a tool.

## 2. Permutation importance (concept)
Shuffle one feature's values across rows, remeasure accuracy, and take
the drop: importance = baseline_acc - permuted_acc. Shuffling breaks
that feature's link to the label while preserving its marginal
distribution. Demo: baseline 1.0, permuted-x1 0.6667, importance
0.3333. Correlated features share credit — shuffling one of a pair
understates both — so read joint behavior, not just ranks.

## 3. PDP concept (partial dependence)
Fix the feature of interest at a grid value, average model predictions
over the other features' observed values, plot the averages. The curve
shows the model's marginal response holding the rest at their data
distribution. Caveat: averaging over unrealistic combinations (height
with weight of a child) can describe regions no real input occupies.

## 4. LIME local-surrogate concept (Ribeiro 2016)
To explain prediction f(x0): sample perturbed points near x0, weight by
proximity with a kernel, fit an interpretable model (e.g. linear) to
those weighted samples, read its coefficients as the explanation. Demo
on f(x)=x^2 at x0=2: weighted least squares recovers slope ~4.0
(observed 3.9999999999999982), matching the true gradient 2x0 = 4. The
intercept 4.0571 anchors the local line. Explanations depend on the
kernel width, sample, and surrogate class — all three are choices, not
facts about the model.

## 5. SHAP Shapley-value concept (Lundberg/Lee 2017)
Credit allocation from cooperative game theory: players are features,
the payout is the prediction minus baseline. The Shapley value averages
each player's marginal contribution over all joining orders. Demo game
v({})=0, v({1})=4, v({2})=3, v({1,2})=10: phi1 = 5.5, phi2 = 4.5, sum =
10.0 = v({1,2}), confirming efficiency. The four axioms, stated as
axioms: efficiency (values sum to the total gain), symmetry (identical
contributors get equal shares), dummy (zero-contributors get zero),
additivity (values add across combined games). SHAP's claim is that
Shapley values are the unique attribution satisfying all four.

## 6. Interpretability-vs-accuracy framing
Simple models (small linear, shallow trees) are readable but may
underfit; rich models fit better but need post-hoc tools. The trade is
not a law — sometimes simple models win — but a budget: every unit of
explanation effort buys trust only if the explanation is faithful and
stable. An unstable explanation of an accurate model is worse than none.

## 7. Stability caveats
Permutation ranks shift with seed and correlated features; LIME
coefficients shift with kernel width and sampling; SHAP values shift
with baseline and feature-grouping choices. Report explanations with
their settings and rerun with perturbed settings before acting on them.
