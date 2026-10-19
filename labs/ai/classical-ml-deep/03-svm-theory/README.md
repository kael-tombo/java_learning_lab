# 03-svm-theory - Support Vector Machines
## Overview
Max-margin classifier: minimize 0.5||w||^2 subject to y_i(w.x_i+b) >= 1. Margin width is 2/||w||; points with equality are support vectors. Hinge loss max(0,1-yf) powers the unconstrained form.
## Key formulas
- Margin: 2/||w||; distance of x: |w.x+b|/||w||.
- Subgradient: -y x when y f < 1 (plus lambda w), else lambda w.
## What the snippets show
- Cml03A: width 1.0, two support vectors at distance 1.0.
- Cml03B: hinge subgradient training to 4/4 accuracy.
## Try it
Move (2,2) off the plane and confirm only margin points affect the solution.
## Formula reference
- Primal: min 0.5||w||^2 + C sum max(0, 1 - y_i f_i); margin = 2/||w||.
- Dual: sum alpha_i - 0.5 sum alpha_i alpha_j y_i y_j K(x_i, x_j); w = sum alpha y x.
- KKT: alpha > 0 only on support vectors (y f = 1).
## Worked example
- w = [2,0]: ||w|| = 2, margin = 1.0; f(1,0) = -2, distance 1.0.
- f(3,1) = 2, distance 1.0: both bind, both are supports.
- Hinge at m = 0.5: 1 - 0.5 = 0.5 penalty; at m >= 1: zero.
## Pitfalls
- Unscaled features distort ||w||; standardize first.
- C too large overfits noise; too small underfits margin violators.
- Non-separable data needs kernels or slack; linear plane cannot bend.
## Connections
- Hinge subgradient mirrors perceptron update with margin 1 instead of 0.
- Kernels generalize the dot products in the dual.
## Exercises
1. Move (2,2) to (2,0.5) and recompute its distance.
2. Set C = 0.01 in the hinge loop and watch margins widen.
3. Verify KKT: which points have nonzero alpha here.
