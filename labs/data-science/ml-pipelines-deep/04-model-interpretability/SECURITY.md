# Model Interpretability — Security

## Threats specific to explanations
- Explanation gaming: a model with discriminatory logic presents
  benign attributions (fairwashed explanations). Mitigate by auditing
  the model directly (slice metrics, counterfactual tests), never the
  explanation alone.
- Perturbation probing: explanation APIs that evaluate arbitrary
  neighbor inputs leak model behavior to extraction attacks. Mitigate
  with rate limits and by explaining from cached backgrounds rather
  than live model calls where possible.
- Baseline manipulation: a chosen SHAP baseline hides a feature's
  contribution. Mitigate by fixing baselines in versioned config and
  reporting sensitivity to the choice.
- Over-disclosure: local explanations reveal training-row details via
  neighbor construction. Mitigate by sampling neighbors from
  aggregates, not by retrieving nearest real rows for display.

## Controls
- Version and hash explanation configs (seeds, widths, baselines)
  alongside the model version they explain.
- Gate stakeholder release on stability reruns; unstable attributions
  stay internal.
- Log explanation requests with the same care as predictions when
  they carry personal data.

## Demo connection
The kernel-width exercise is the miniature of baseline/width
sensitivity: same model, different settings, different story. Fixing
settings in config is the control, and the stability rerun is the
audit.
