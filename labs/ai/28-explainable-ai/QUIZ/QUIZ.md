# Explainable AI — Quiz

Keys follow each item; classical statements only.

**Q1. What does LIME fit?**
A: A weighted, sparse surrogate (usually linear) to the black box on samples drawn near
one instance; it is a neighborhood claim, not a global model statement.

**Q2. State the SHAP value definition informally and its efficiency property.**
A: Average marginal contribution of a feature over subset orderings; formally
`phi_i = sum_S weight_S * ( f(S u {i}) - f(S) )`, and efficiency says
`f(x) - f(x_bar) = sum_i phi_i`.

**Q3. For a purely additive model, what are the Shapley values?**
A: Exactly the per-feature linear contributions: `phi_j = w_j * (x_j - x_bar_j)`.

**Q4. How many samples does exact Shapley need in general?**
A: `2^n` subsets (or `n!` orderings); tractable only for small `n` or model families with
structure such as additivity/specific tree formulas.

**Q5. Why is a LIME coefficient NOT a causal effect size?**
A: It summarizes local predictive behavior of a fixed model, not a counterfactual
world where the feature is changed; causal claims need interventional data.

**Q6. What changes when correlated features enter Shapley computation?**
A: Subset intervention pushes implausible feature combinations; one must choose between
observational (condition-based) and interventional account — and disclose the choice.

**Q7. In our run, why did LIME's surrogate recover the model exactly?**
A: The toy teacher is linear and the sampled neighborhood is non-degenerate, so OLS
identifies the true coefficients with zero residual.

**Q8. Give one governance-grade reporting habit.**
A: Pin your explaining setup in the artifact: baseline, kernel/weights, sample count,
random seeds, and a residual table — so a reviewer can rerun or challenge it.
