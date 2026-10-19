# 06-weight-initialization - Weight Initialization
## Overview
Xavier (var 1/fanIn, for tanh/sigmoid) and He (var 2/fanIn, for ReLU) keep activation variance stable across layers. Uniform variants use bounds sqrt(6/(in+out)) and sqrt(6/in).
## Key formulas
- Xavier: Var=1/fanIn; He: Var=2/fanIn.
- Uniform Xavier bound: sqrt(6/(fanIn+fanOut)).
## What the snippets show
- Nn06A: closed-form numbers for a 4->3 layer.
- Nn06B: empirical variance 0.0199 matching 0.0200.
## Try it
Sample with Xavier scale on ReLU and watch variance halve per layer conceptually.
## Formula reference
- Xavier: Var = 1/fanIn (tanh/sigmoid); He: Var = 2/fanIn (ReLU halves variance).
- Uniform bounds: sqrt(6/(in+out)) Xavier, sqrt(6/in) He; bias zeros.
- Gain factors exist per nonlinearity (orthogonal init generalizes).
## Worked example
- 4->3 layer: Xavier var 0.25, std 0.5; He var 0.5, std 0.7071.
- Bounds: sqrt(6/7) = 0.9258; sqrt(6/4) = 1.2247.
- 10000 He draws var 0.0199 vs 0.02: sampling error ~0.0005 (1/sqrt(n) scale).
## Pitfalls
- Xavier + ReLU halves variance per layer; deep nets fade.
- Zeros everywhere: symmetric, no learning; randomize.
- Too-large init saturates sigmoids instantly.
## Connections
- Normalization layers relax init sensitivity but do not remove it.
- Residual paths propagate even with small init (identity carries).
## Exercises
1. Compute He bound for fanIn = 512.
2. Sample Xavier on ReLU; predict variance halving.
3. Init all zeros and explain the symmetry trap.
