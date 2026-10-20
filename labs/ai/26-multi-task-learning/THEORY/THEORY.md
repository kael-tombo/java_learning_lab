# Multi-Task Learning — Theory

**Multi-task learning (MTL)** trains one model to solve several tasks at once, betting
that shared representations will help tasks regularize and transfer to each other. The
architecture typically splits into a shared trunk plus per-task heads.

## The core mechanism

- Shared trunk: earlier layers encode generic structure; heads stay task-specific.
- Combined loss: the training signal is a weighted sum of per-task losses, and the *choice
  of weights* is a first-class design decision, not a detail.
- Gradient interactions: two heads share one parameter update; if their gradient
  directions disagree, the joint step contradicts itself — the classical conflict that the
  weighting methods below try to manage.

## The gradient-domination trap

Scales differ: a regression MSE, a classification cross-entropy, and a ranking loss place
their numbers on completely different ranges. Averaging them naively lets the
largest-magnitude loss own the update. Widely used families of fixes:

- **Uncertainty weighting**: treat a per-task noise parameter as learned and reweight loss
  terms by those parameters; at concept level it down-weights noisy or
  difficult-to-scale tasks.
- **GradNorm-style balancing**: adjust weights dynamically so gradient magnitudes even
  out (plus auxiliary terms for relative task speeds).
- **Gradient surgery**: project conflicting task gradients to be orthogonal before the
  step so neither overturns the other (our second snippet demonstrates equal-conflict
  projection).

Note the assumptions: task losses are differentiable scalars; per-task weights are
positive; the shared trunk is differentiable to both heads. Fast-moving variants exist
beyond this list; the lab pins itself to the classical three above (weighting schemes and
their monotone effects) rather than recent hybrids.

## Transfer vs interference

Sharing sometimes HURTS: mismatched tasks (say, disease-classification of text vs
photo-region crops) can cause negative transfer. Practical signals: monitor per-task loss
trajectories separately; if a task plateaus while others improve, suspect interference,
reweight, or split the trunk.

## Where Java fits

All the mechanics above operate on small vectors of derivatives; with 2 heads and 2
parameters you can implement and verify weighted sums and orthogonality projections
exactly — CODE_DEEP_DIVE shows those numbers, and the mini project expands them.
