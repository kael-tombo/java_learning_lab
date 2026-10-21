# Model Interpretability — How It Works

## 1. State the explanation question
"Which features drive the model overall?" is global; "why did item 7
score 0.9?" is local. Write the question down — it selects the method:
permutation/PDP for global, LIME/SHAP for local attributions.

## 2. Permutation pass
Baseline accuracy on held-out data, then per-feature shuffle-and-score
loops. The demo loop reverses x1 (index map 5,4,3,2,1,0), dropping
accuracy from 1.0 to 0.6667 for importance 0.3333. Repeat shuffles to
separate signal from shuffle noise before ranking.

## 3. PDP pass
Grid the feature of interest, average predictions over background rows
at each grid point, plot. Read slopes and flats as the model's marginal
habits, and flag grid regions with no data support as untrustworthy.

## 4. LIME pass
Pick x0, sample neighbors, weight by kernel proximity, fit a weighted
linear surrogate, report coefficients. The demo's slope ~4.0 at x0=2
for f(x)=x^2 shows the surrogate recovering the local gradient. Vary
the kernel width and confirm the slope moves — that movement is the
stability caveat made visible.

## 5. SHAP pass
Choose a baseline (e.g. data mean), enumerate coalitions (exact for few
features, sampled for many), average marginal contributions per
feature. Demo: two players give 5.5 and 4.5 summing to 10.0. Check
efficiency (sum equals prediction minus baseline) on every explanation
as a sanity gate.

## 6. Report with settings
Every explanation ships with its knobs: shuffle seed and count, PDP
background sample, LIME kernel width and sample size, SHAP baseline and
grouping. A number without settings is not reproducible and not
actionable.

## 7. Act cautiously
Use explanations to audit (find bugs, bias, leakage features), to
communicate (justify a decision), and to prioritize (which feature to
fix first) — in that order of safety. Never treat an attribution as a
causal claim about the world.
