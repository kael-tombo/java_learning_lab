# Variational Autoencoders — Exercises

Each task builds on the `ElboArithmetic` class from CODE_DEEP_DIVE; compile with
`javac --release 21 -encoding UTF-8`.

## 1. Shift the encoder mean

Set `mu = 1.5` (variance stays 0.25) and recompute the bound by hand first: KL grows with
`mu^2`, reconstruction worsens with `(x - mu)^2`. Verify the two deltas against the
program; state which term contributed more to the total drop.

## 2. Prove the MC gap shrinks like 1/sqrt(n)

The 50k-draw estimate landed at `-2.360082`, about `0.002` above the closed form. Run the
estimate at `n = 2,000` and `n = 200,000` and report the deviations. They should not
shrink exactly as the square-root law predicts (few draws waste noise in both
directions); say what you actually observe before asserting anything.

## 3. Tightness check by construction

Extend the sweep to verify the claim "the posterior `N(x/2, 0.5)` is exact" for a second
datapoint `x = -2.0` as well. The gap column must print `0.0` in both cases; any other
value means your decoder variance or your `lnPdf` is wrong.

## 4. Beta reweighting, conceptually tested

Report the sweep rows when the KL term is multiplied by `beta in {0.5, 2, 10}`. Note that
multiplying changes the objective, not the truth: once `beta` differs from 1 the result
is no longer a bound on `log p(x)`. Write one sentence saying which beta pulls the sweep's
middle entry closest to the prior.

## 5. Two-dimensional extension

Duplicate the scalar machinery with independent coordinates: `q = N([1, -1], diag(0.25,
0.25))`, unit decoder variance per coordinate. The bound factorizes; check
programmatically that the 2D ELBO equals the sum of the two 1D ELBOs you already trust.

## Honesty rule

Every numeric claim gets a source line: either "observed" from your run or "derived" from
your by-hand algebra with the arithmetic shown, never both.
