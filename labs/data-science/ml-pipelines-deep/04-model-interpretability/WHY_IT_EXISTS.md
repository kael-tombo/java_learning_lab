# Model Interpretability — Why It Exists

Interpretability exists because models that cannot be questioned cannot
be trusted with consequential decisions. A credit denial, a medical
flag, a fraud hold — each demands a reason the affected person and the
responsible team can examine. Accuracy alone never supplies that
reason; it only says the model is usually right, not why it is right
here.

The methods also exist for builders, not just stakeholders: permutation
ranks catch leakage features (an ID column topping importance is a
confession), PDP flats catch dead features, local attributions catch
perverse single-case reasoning. Explanation tooling is debugging
tooling with a second audience — and the debugging use is the safer,
better-evidenced one.

## Which question first
Global and local tools answer different questions, and the question
must be fixed before the tool is picked. "Which features drive the
model overall" calls for permutation ranks or PDP curves; "why did
this item score this way" calls for a LIME surrogate or SHAP split
like the 5.5/4.5 demo. Running a global rank to justify a single
denial, or a local slope to describe the whole model, is a category
error no tuning fixes.

## Stability as an existence argument
The methods exist in plural because no single explanation is stable
across settings: permutation ranks move with seed and correlation,
LIME slopes move with kernel width and sample (the slope near 4.0
holds only where width keeps samples local), SHAP shares move with
baseline and grouping. The lab therefore teaches settings-reporting
as part of the method: every attribution ships with the choices that
produced it, and perturbed reruns are the price of quoting it.

## Audit before persuasion
Explanations first serve the builders who must debug and the auditors
who must verify; persuading stakeholders comes second and only where
faithfulness is established. The permutation drop of 0.3333 and the
efficiency check summing to 10.0 are builder-grade facts: recompute
them on the rows and they hold. A chart that cannot be recomputed is
a story, not evidence, and stories do not survive audits.
