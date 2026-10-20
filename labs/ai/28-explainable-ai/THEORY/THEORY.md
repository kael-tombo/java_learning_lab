# Explainable AI — Theory

**Explainable AI (XAI)** covers methods that make a model's behavior relatable to humans.
XAI and explainability at large come in three families, the taxonomy that keeps confusing
papers straight: (a) intrinsically interpretable models (sparse linear models, small
trees, scorecards); (b) post-hoc local attributions of a black box (Shapley-style
allocation, local linear surrogates, gradient maps); (c) global summaries (surrogate
trees, ICE/curves, feature-importance rankings).

## The two standard report tools

- **LIME**: probe the black box around the instance being explained with a handful of
  perturbed samples; fit an interpretable (usually sparse-linear) surrogate weighted by
  proximity, and read its coefficients locally. Core claim: the surrogate describes the
  model NEAR THE INSTANTIATION — only the explored corner, not the model overall.
- **SHAP**: borrow the cooperative-game contribution split: treat each feature as a
  "player", average the effect on the prediction over feature subsets. Under the
  classical formulation, game-shapley values are the unique additive allocation with
  (i) an efficiency/axiom property, (ii) a symmetry property for equal players, and (iii)
  a dummy property; for 2 features these reduce to an average of two subset margins —
  the enumeration our snippet runs.

## What explanations can and cannot tell you

The efficiency property gives an exact additive decomposition: base value plus
contributions equals the prediction. What you cannot collect: causal claims (Shapley
describes a predictive association, NOT a counterfactual "if we change X..."), importance
guarantees for correlated features, or certainty for global behavior. Writing "feature X
caused a 3-point change" for linear data happens ONLY when the model is additive, so a
causal phrasing is careless elsewhere.

## Better vs bad practice in reviews

Good: pairwise consistency checks on obvious features, a stated baseline choice, and
demonstrating that the local surrogate actually fits the black box on the neighborhood
that was sampled. Bad: mixing up local and global rankings, or trusting a LIME
coefficient after only a handful of samples with no proximity weighting.

## Java angle

For additive and small linear families, attribution arithmetic is a few loops of double
math; the snippets recompute both tools exactly. What matters for teaching is the
sampling-free setting: the perturbation-on-a-grid trick in Snippet 2 recovers the linear
model's parameters exactly, so every surrogate discipline (weighting, sparsity, baseline
choice) can be inspected without RNG noise.
