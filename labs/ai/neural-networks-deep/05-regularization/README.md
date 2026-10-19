# 05-regularization - Regularization
## Overview
L1 adds lambda|w| (sparsity), L2 adds lambda/2 w^2 (shrinkage/weight decay). Dropout zeroes units with prob p in training and rescales survivors by 1/(1-p) so expectations match inference.
## Key formulas
- Loss = base + lambda|w|_1 + (lambda/2)|w|_2^2.
- Inverted dropout: out = mask*x/(1-p).
## What the snippets show
- Nn05A: penalty arithmetic on fixed weights.
- Nn05B: exact rescaled mask output.
## Try it
Raise lambda to 1.0 and see L1 dominate the toy loss.
## Formula reference
- L2 shrinks w *= 1/(1+lr lambda) per step (weight decay); L1 soft-thresholds.
- Dropout p: train mask/(1-p), test identity; effective ensemble of subnets.
- Early stopping + augmentation regularize without touching loss.
## Worked example
- L1 2.2 vs L2 2.54 on [0.5,-1.5,0.2]: L1 dominated by |-1.5| linearly.
- Halved L2 term 1.27 < L1 2.2 here; ranking flips for small weights.
- Mask [1,0,1,0] p=0.5: [1,2,3,4] -> [2,0,6,0], mean preserved (2.5 -> 2.5).
## Pitfalls
- Dropout on tiny layers harms more than helps; skip input-layer dropout usually.
- Forgetting eval mode (dropout still on) corrupts validation scores.
- L1 + correlated features picks one arbitrarily.
## Connections
- Weight decay appears inside AdamW decoupled from gradient.
- Pruning is post-hoc sparsity; L1 is training-time sparsity.
## Exercises
1. Set lambda = 1.0 and compare L1 vs L2 totals.
2. Apply mask [1,1,0,0] p = 0.5 to [2,4,6,8].
3. Prove inverted dropout preserves expectation.
