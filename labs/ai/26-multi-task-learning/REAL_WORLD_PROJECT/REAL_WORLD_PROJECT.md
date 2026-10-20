# Multi-Task Learning — Real-World Project

**Goal**: a Java design-and-probe of a shared-feature fraud & churn service: one trunk
serving two heads (a risk scorer and a retention predictor) — prototype math and the
monitoring needed to detect interference.

## Why this pairing is realistic

Fraud risk and churn propensity naturally share signals (spending patterns, tenure,
complaint volume), making the joined-training assumption plausible but unproven. This
project forces you to instrument the claim instead of asserting it.

## Build components

1. `FeatureStore` (self-made 8-dim synthetic customers, 200 rows, seeded).
2. `DualHead` model: one 8-8 tanh trunk, two linear heads; analytic backprop, hand
   verified against finite differences on 5 random parameter taps (print max abs error,
   must be below `1e-5`).
3. `WeightScheduler` with three modes (uniform, loss-EMA inverse, gradient-magnitude
   balancing) selectable by flag; publish per-mode AUC-proxy style metric per head
   (rank-agreement with the hand-written truth mask is fine).
4. `InterferenceMonitor`: per-head loss + gradient cosine each 200 steps; raises a
   sentinel line `DOMAIN-CONFLICT` when cosine < -0.4.

## Deliverables and honesty requirements

- Table comparing the three modes at steps {200, 1000, 3000}: both losses; annotate the
  step/mode pair where each head hit its own best.
- A caveat paragraph: with synthetic truths the numbers are illustrative only; the thing
  being tested in production is whether the interference monitor ever fires, and what
  the escalation path would be (pause shared tuning, re-run single-head, compare).
- A decision rule you would actually apply: define one numeric threshold on relative head
  loss growth over 7 pseudo-days that triggers split-training, and justify it from your
  observed trajectories (not from intuition).

## Constraints

`javac --release 21`, no third-party jars, runtime printed rows in ASCII only; keep the
whole prototype single-file under ~400 lines so the review is mechanical.
