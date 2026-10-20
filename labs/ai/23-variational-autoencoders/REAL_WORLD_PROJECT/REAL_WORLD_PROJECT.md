# Variational Autoencoders — Real-World Project

**Goal**: a monitoring toolkit for anomaly detection pipelines that report a bound-based
score, Java-side only, with honesty as a first-class deliverable.

## Scenario

Many production anomaly detectors score inputs by a reconstruction error or by a
variational bound. Your job: build the harness that (a) reproduces the scoring math for an
interpretable Gaussian case and (b) makes the limitations visible to the team.

## Build these components

1. `ScoreService`: given a feature vector of two Gaussian-ish scalars (use any self-made
   schema), compute per-feature KL or reconstruction-style terms and a combined score;
   expose thresholds as configuration.
2. `CalibrationRunner`: on labelled synthetic data (class 0 = clean, class 1 = shifted),
   sweep the thresholds and emit a precision/recall table per threshold — reuse the
   score-coverage pattern from the safety lab but with two features.
3. `GapReport`: for each score, state one sentence on bound versus truth: reconstruction
   error is NOT a log-likelihood, and KL-only scores conflate prior-mismatch with novelty.
4. Optional density trick worth knowing conceptually: score by the exact mixture density
   when the decoder variance is known — what the closed-form marginal does for scalar
   Gaussians.

## Write-up checklist (required, graded on candor)

- Where the score can be fooled: shifting a feature the model never uses raises no term;
  give one concrete example with numbers from your own table.
- Distribution shift over time: describe a retraining trigger and what you would watch
  (score drift histograms, per-week summaries).
- Alert fatigue: pick two thresholds from your sweep and justify one for paging versus one
  for a dashboard.

## Deliverables

- Compiling classes, `javac --release 21`, seeded runs, the threshold table.
- A two-page memo with the limitations section first, explicitly labeled as unverified
  beyond the synthetic setting.
