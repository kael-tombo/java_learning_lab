# Explainable AI — Mini Project

**Goal**: a single-file explanation console for a tiny predictors suite: additive,
interaction, and tiny-tree families; read-only attributions, printed as review sheets.

## Model set (hand-coded, no training)

- `AdditiveBox`: `f = 1.5*x0 + 2*x1 + 0.5`.
- `InteractionBox`: `f = 1.5*x0 + 2*x1 + 0.5*x0*x1 + 0.5`.
- `ConjunctionBox`: `f = 1` if `x0 > 1 && x1 > 2` else `0` (a rule-tree).

## Attributions implemented

1. `Shapley.exact(box, instance, baseline)` — full `2^n` subset enumeration with the
   correct subset weights; assert the efficiency sum each call.
2. `Lime.gridSurrogate(box, instance, radius, gridDims)` — per-axis grid around the
   instance, weighted least squares for `AdditiveBox`/`InteractionBox` (unweighted
   variant allowed if you justify it in comments).
3. Print for each box and a fixed instance set of 3 rows: phi vector, surrogate
   coefficients, residuals, and the efficiency closing line.

## Review-sheet acceptance tests (hard asserts)

- `AdditiveBox` phis match `w * (x - bar)` to `1e-9` for every instance tested.
- `ConjunctionBox` at instance `(2, 3)`: the printed phis should both read `0.5` (each
  ordering contributes 0 once the other feature is already high); add one line of your
  own judgment on whether symmetric attribution is a sensible explanation here (the rule
  fires only when both features are high).
- `InteractionBox` phis reproduce the hand enumeration from EXERCISES.

## Report

- A four-line stdout per (model, instance) triple — the "review sheet".
- A markdown paragraph: which family's LIME surrogate was trustworthy, and what phrasing
  you would use with a non-technical stakeholder for each.
- Not in scope, stated explicitly: counterfactual scoring, causal graphs, distributional
  baselines — list them as unknowns rather than half-implement them.
