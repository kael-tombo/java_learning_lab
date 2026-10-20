# Variational Autoencoders — Mini Project

**Goal**: an "ELBO workbench" — a small Java library that holds Gaussian-family VAE math
and a test harness proving each formula numerically.

## Library surface (one file is fine)

- `record Gauss(double mu, double var)` with `klToStd()`, `logPdf(x)`, `plusNoiseVar(v)`
  (the mixture/convolution helper used for exact marginals).
- `Elbo.closedForm(x, Gauss q, double decVar)` returning recon, kl, elbo, and the exact
  marginal via `q.plusNoiseVar(decVar)`; all doubles, no sampling.
- `Elbo.monteCarlo(x, q, decVar, n, seed)` — LCG plus one Box-Muller draw per sample,
  seedable and deterministic.

## Required tests (assert in main, fail loudly on mismatch)

1. `klToStd()` on `N(0, 1)` returns exactly 0.
2. `closedForm` for `x = 0, q = N(0, 1), decVar = 1`: recon must equal
   `-0.5 * (0 + 1 + ln 2pi)` and the bound must equal the marginal `log N(0; 0, 2)` — the
   standard baseline where posterior equals prior.
3. Tightness: for `x` in `{-3, 0, 2}` and the true posterior `N(x/2, 0.5)`, the gap prints
   0 within `1e-9`.
4. MC/ClosedForm agreement at `n = 200000` inside `5e-3` for at least one fixed seed; if a
   seed fails that tolerance, print both numbers instead of asserting (sample noise) and
   document it.

## Report requirements

- A table (rows = four scenarios above) with closed-form vs sampled values side by side.
- One paragraph on when the bound is loose in real models: non-Gaussian decoders, high
  dimensions with unseen codes, and implicit likelihoods are all beyond closed form.

## Constraint

No third-party libraries, `javac --release 21`, deterministic output given the seed; the
whole thing fits comfortably in ~150 lines if you resist feature creep.
