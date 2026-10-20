# Generative Adversarial Networks — Mini Project

**Goal**: a single-file "two-player stationary" simulator: adversarial learning between a
generator net and discriminator net over a 2D point cloud, all math moved from scalars to
tensors-by-loops.

## Model

- Data: 200 points on the unit ring plus a tight cluster at the origin (two distinct
  shapes, i.e., two modes).
- Generator: latent `z ~` LCG uniform in `[0, 1)^2` mapped through a 2-8-2 stack of
  hand-rolled dense layers with tanh activation (output scaled to `[-1.5, 1.5]`).
- Discriminator: 2-8-1 dense stack with logistic output; batch = 16 real + 16 fake.

## Training rules

- 2,000 alternating steps, rates `1e-2` discriminate / `1e-2` generate, manual
  backpropagation is NOT required: implement forward-mode gradients explicitly for the
  chosen tiny sizes, or drop to a simplified per-coordinate version you can verify.
- Every 250 steps print: mean real score, mean fake score, and the variance of the
  generator's outputs coordinates (a crude mode-coverage proxy: collapsed outputs show a
  coordinate variance near zero).

## Deliverable & acceptance

1. Code compiles with `javac --release 21`; deterministic run given a fixed seed.
2. A stdout table of checkpoints where both score columns are reported.
3. A two-paragraph written analysis: which mode is the generator favoring, and whether the
   output-variance proxy agrees with your read of the score columns.
4. Explicit statement that this is a synthetic playground; do not claim image generation.

## Stretch (optional)

Swap the ring data for three modes and watch coverage degrade; add a diversity nudge by
giving each latent a region prior... document whatever you observe without inventing
claims.
