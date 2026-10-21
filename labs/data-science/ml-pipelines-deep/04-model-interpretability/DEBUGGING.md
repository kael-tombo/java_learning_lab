# Model Interpretability — Debugging

## Symptom: permutation ranks change run to run
Likely shuffle noise or correlated features splitting credit
arbitrarily. Check: rerun with several seeds and report rank ranges
instead of one ordering. The demo uses a fixed reversal (fully
deterministic); real shuffles need averaging before ranking. Fix:
increase shuffle count, group correlated features, and publish spreads.

## Symptom: LIME explanation contradicts the model's local behavior
Likely kernel width mismatch: too wide averages over curvature, too
narrow fits noise. Check: vary the width (demo 0.3 vs 1.0) and watch
the slope move; compare surrogate predictions against true model
outputs on the neighbors. Fix: pick the width by neighbor fidelity
(R2 of surrogate vs model), not by aesthetics, and report the width.

## Symptom: SHAP values do not sum to prediction minus baseline
Likely inconsistent value function (changed baseline mid-computation)
or a sampling bug. Check the efficiency gate: demo confirms sum 10.0
equals v({1,2}) with efficiency_holds=true. Fix: freeze one baseline,
recompute, and refuse to publish attributions that fail efficiency.

## Symptom: PDP shows effects where no data exists
Likely grid points outside data support averaged over unrealistic
combinations. Check background density per grid point. Fix: rug-plot
or histogram the background under the curve and grey out unsupported
regions.

## Symptom: importance rank crowns an ID column
Likely label leakage through an identifier, not a discovery. Check
with a group-aware split (no shared IDs across folds) and remeasure.
Fix: remove the leaking feature at the pipeline level (lab 02 gate),
not by hiding it from the explainer.

## Debugging checklist
1. Rerun every explanation with perturbed settings.
2. Check efficiency (SHAP) and fidelity (LIME) gates.
3. Verify background support under PDP readings.
4. Confirm ranks survive seed averaging.
5. Audit the model directly before trusting its portrait.
