# Visual Guide - Causal Inference

## 1. The DAG sketch

Nodes for treatment, outcome, confounders; arrows for assumed causal
direction. Confounder = arrows into both treatment and outcome.
Collider = two arrows in (never condition). Draw before computing.

## 2. Stratum bars for Simpson

Paired bars per stratum (A vs B recovery) plus a pooled pair. The
visual paradox - B winning every panel but losing the pooled one -
teaches faster than any paragraph.

## 3. Pre-trend twin lines

Two lines (treated, control) across pre-periods continuing to post.
Parallel pre-lines license DiD talk; fan-out post-lines picture the
effect as the gap change, matching the algebra exactly.

## 4. Cutoff scatter

Outcome vs running variable with a vertical cutoff line; look for the
jump at the line and for bunching (manipulation) of density beside it.

## 5. Balance love-plot

Dot per covariate: raw gap vs matched gap against a 0.1 reference line.
Successful matching drags dots left of the line; stubborn dots name the
covariate that still confounds.

## 6. Sensitivity slope

Estimate on the y-axis vs assumed confounder strength on x. The
crossing point where the effect hits zero is the finding's breaking
strength - annotate it, don't hide it.

## 7. Weights waterfall

Stacked bar showing each stratum's gap times its share summing to the
adjusted number. Viewers see which population drives the answer - and
argue with the weights, which is exactly the right argument to have.

## 8. License card

A small card per reported effect: estimate, design icon, assumption in
plain words, breaking strength. Taped to every slide, it stops the
number from traveling without its papers.
