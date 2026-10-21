# Model Interpretability — References

All entries are real publications. Verify editions and venues locally.

1. Ribeiro, M. et al. "Why Should I Trust You? Explaining the
   Predictions of Any Classifier" (2016). LIME local surrogates.
2. Lundberg, S. and Lee, S. "A Unified Approach to Interpreting Model
   Predictions" (2017). SHAP Shapley-value attributions.
3. Hastie, T., Tibshirani, R., Friedman, J. "The Elements of
   Statistical Learning." Partial dependence, variable importance
   background.
4. Sculley, D. et al. "Hidden Technical Debt in Complex Machine
   Learning Systems" (NIPS 2015). Explanations as debugging/audit
   tooling in production.
5. Breck, E. et al. "The ML Test Score: A Rubric for ML Production
   Readiness." Checks that explanations support rather than replace.
6. Molnar, C. "Interpretable Machine Learning." Open-access textbook
   covering permutation importance, PDP/ALE, LIME, and Shapley
   attributions with worked examples; use for background and for
   comparing method assumptions side by side.
7. Shapley, L. "A Value for n-person Games" (1953). The cooperative
   game-theory source of the Shapley value and its axiomatic
   characterization; read for the efficiency/symmetry/dummy/additivity
   framing behind SHAP's claim.
8. Friedman, J. "Greedy Function Approximation: A Gradient Boosting
   Machine" (2001). Gradient-boosting context in which partial
   dependence summaries became standard model-reading tools; pairs
   with the Hastie/Tibshirani/Friedman textbook treatment.
9. Sculley, D. et al. "Machine Learning: The High-Interest Credit Card
   of Technical Debt" (SE4ML workshop, 2014). Short precursor statement
   of the production-debt argument expanded in the 2015 paper above;
   useful for the audit-before-persuasion ordering.

No vendor docs, no invented papers, no benchmark numbers.

## How to read them together
- Pair Molnar's worked examples with the demo numbers here (0.3333,
  slope near 4.0, split 5.5/4.5) to see where textbook and lab agree.
- Read Shapley's axioms beside SHAP's uniqueness claim to separate the
  mathematics (uncontested) from the estimation choices (contested).
- Keep Friedman's PDP context next to the height/weight caveat: the
  averaging construction is the same, and so is the unsupported-region
  risk.
