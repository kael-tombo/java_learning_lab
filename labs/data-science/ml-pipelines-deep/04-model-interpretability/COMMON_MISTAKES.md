# Model Interpretability — Common Mistakes

## 1. Reading attribution as causation
SHAP 5.5 for player 1 says the model credits it so — not that changing
the real-world feature causes that gain. Attributions describe the
model; causal claims need experiments.

## 2. Publishing one LIME fit
A single kernel width and sample yields one of many defensible local
stories. The demo slope matches truth at width 0.3; other widths give
other slopes. Always report width, sample size, and a rerun spread.

## 3. Ignoring the baseline
SHAP shares depend on the reference point. Changing baselines
redistributes credit without touching the model. Fix the baseline in
versioned config and test sensitivity.

## 4. Ranking correlated features naively
Permutation drops split across correlated partners understate each.
Group them or use joint shuffles before concluding "feature X does not
matter."

## 5. Trusting PDP in empty regions
Averaging over feature combinations no real input occupies describes
model fantasy, not behavior. Overlay data density and distrust curves
where support is thin.

## 6. Explaining without versions
An attribution detached from model and dataset versions is orphaned:
reruns cannot reproduce it. Pin both versions plus explainer settings.

## 7. Using explanations to certify fairness
A benign-looking attribution does not prove benign behavior; models can
present fair portraits while deciding unfairly. Audit slice metrics and
counterfactuals directly.

## 8. Confusing global with local
Applying a global rank to justify one decision (or one SHAP vector to
describe the model) crosses the question boundary. State the question
first, then pick the tool that answers it.
