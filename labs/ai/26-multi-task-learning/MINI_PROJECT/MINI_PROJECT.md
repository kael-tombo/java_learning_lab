# Multi-Task Learning — Mini Project

**Goal**: a three-task shared-trunk trainer in pure Java with a live weight controller —
small enough to read, big enough to exhibit every pathology from THEORY.

## Model

- Trunk: 2-dimensional input, 6 hidden units, tanh. Heads: linear scalar per task
  (3 heads, weights by hand from a fixture).
- Tasks (data hand-written, 16 points each): MSE regression, logistic classification
  (2 classes), quantile-style ABS loss (a third family, different scale on purpose).
- Backprop implemented per-op with derivative comments; use loops, no matrix library.

## Controller requirements

1. Weight modes selectable at runtime: `uniform`, `inverse-noise` (sigma = sqrt of a
   running loss EMAs), `GradNorm-inspired` (scale weights per step so that per-task
   gradient norms become near-equal — a 1e-3-tolerance loop within each step is fine).
2. After every 100 steps print: per-task loss, per-task gradient norm, combined gradient
   norm, and current weight triple.
3. A conflict probe: every 100 steps print the pairwise cosine matrix of the three
   per-task gradients.

## Required observations in your final report

- Which mode produced the smallest max/min loss-spread at step 1000.
- Whether any mode drove a task's loss UP by step 500 (the negative-transfer signature).
- The single cosine pair that went below `-0.5` during training, if any, and whether the
  GradNorm-inspired mode softened it.

## Acceptance criteria

- Compiles with `javac --release 21`; fully deterministic under fixed seed.
- All.stdout rows are 4-dp rounded; capture 11 printed checkpoints (step 0, 100, ...,
  1000) in a commented block or a log file.
- Statement of scope: results on 16-point fixtures say NOTHING about large-scale regimes;
  keep the word "surprising" tied to what you actually observed.

## Stretch

Add a fourth task with a deliberately conflicting objective (e.g., predicting the inverse
of task A's target) and rerun the probe matrix — describe (2 sentences) how the cosine
history differs.
