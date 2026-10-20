# Explainable AI — Exercises

JDK 21+, `javac --release 21 -encoding UTF-8`; start from the snippets in
CODE_DEEP_DIVE.

## 1. Orderings, not shortcuts

Rewrite Snippet 1 to iterate all `n! = 2` orderings explicitly (feature lists
`[x0, x1]` and `[x1, x0]`), accumulating `delta` per subset step, then divide by `2!`.
Report whether the results match the closed average form; they must (`3.0`, `6.0`).

## 2. Baseline sensitivity

Move the baseline to `(1, 1)`. Evaluations change: `f(bar)` becomes `4.0`, and with the
instance still `(2, 3)` the subset set reads `{empty: 4.0, {x0}: 5.5, {x1}: 8.0,
both: 9.5}`. Compute the new phi values by hand first (expect `phi_0 = 1.5` and
`phi_1 = 4.0` after both orderings average), confirm by running, and write what the
efficiency check now evaluates to (it must still close: `4.0 + 5.5 = 9.5`).

## 3. Non-additive interaction feature

Change the black box to `f = 1.5*x0 + 2*x1 + 0.5*x0*x1 + 0.5` and recompute the four
subset evaluations with the instance still `(2, 3)`. The interaction makes
`phi_0 = 4.5` and `phi_1 = 7.5`; show the intermediate margins in a table and state which
subset steps absorbed the interaction (`x0` entering solo vs after `x1`).
Also confirm the sum: `phi_0 + phi_1 = 12.0 = f(x) - f(bar)` with `f(x) = 12.5`.

## 4. Weighted LIME, mild nonlinearity

Make the black box `f = 1.5*x0 + 2*x1 + 0.2*x0^2` and rerun Snippet 2's fit WITHOUT the
quadratic term in the surrogate design matrix. Quote residuals for the four grid rows;
the largest residuals now sit away from the instance. Then narrow the grid to a smaller
radius around the instance and report how the surrogate coefficients move — compare
against the unweighted fit from CODE_DEEP_DIVE.

## 5. Explanation audit rap sheet

For the interactive case in Exercise 3, print per-ordering deltas as a JSON-ish line per
feature. Verify additivity yourself (sum = `f(x) - f(bar)`), and write two lines: one
claim you WOULD put in a stakeholder summary, one claim you would refuse (causal
phrasing), with your justification.

## Evidence rule

For any figure quoted in your submission, the grep-able string must exist in a run log
you keep (name pattern: `xaie-<task>.log`); in doubt, rerun.
