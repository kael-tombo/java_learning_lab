# Self-Supervised Learning — Mini Project

**Goal**: a self-contained "embedding auditor" — build a molecular set of synthetic 2D
"instances", augment them with fixed transforms, train cosine-ranked vectors by hand
gradient steps, and watch a representation learn to cluster.

## Data

- 10 synthetic vectors placed on 3 clusters (corner, center band, diagonal stripe), all
  coordinates fixed by hand in the source.
- Augmentations (deterministic, no RNG): scale-shear by a small matrix per view-index.

## Model pipeline (all loops, no libs)

1. `Encoder`: 2-4-2 dense net with tanh; implement per-layer forward and analytic
   backward for the e2-mean-square surrogate (document the chain rule per operation, this
   is where bugs live).
2. `Augmentor`: fixed transform stack producing exactly two views per instance.
3. `LossNce`: InfoNCE in batch form (10 instances = 20 views; positives per instance
   pair; one-sided negatives = other instances' first views), `tau = 0.2`.
4. Update rule: vanilla gradient descent, `lr = 0.05` manual; print loss at iterations
   1, 100, 500, 1000.

## Expected behavior to verify (acceptance criteria)

- The initial mean loss is near `log(10) = 2.303` (uniform ranking over one-sided
  candidates) within network-init slop; quote the actual first value in your log.
- After training, the mean pairwise cosine within clusters must exceed the cross-cluster
  median; quote both aggregates.
- A seedy claim to test and kill: rising loss with lr = 0.5 means your backward pass has
  a sign bug; fix backprop instead of lowering the rate blindly.

## Reporting

- Print the embedding matrix after training (4-dp rounding).
- One-paragraph write-up: which augmentation pair was easiest to align, relating to
  transform strength? What did you do to keep the run deterministic? Where could the
  "clustering" conclusion overreach? (synthetic data caveat goes here verbatim).
