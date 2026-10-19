# 01-perceptron - Perceptron
## Overview
Perceptron: y_hat = step(w.x + b), update on mistakes only. Converges in finite steps iff data is linearly separable (perceptron convergence theorem); XOR is the classic counterexample.
## Key formulas
- Update: w += (y - y_hat) x; b += (y - y_hat).
- Separable data converges; bound scales with (R/gamma)^2 margin terms.
## What the snippets show
- Nn01A: OR learned exactly (w=[1,1], b=-1).
- Nn01B: XOR stuck at 2/4 after 38 updates.
## Try it
Run Nn01A on AND (labels 0,0,0,1) and read off the learned weights.
## Formula reference
- Output step(w.x + b); mistake-driven update w += (y - y_hat) x.
- Margin gamma: updates bounded by (R/gamma)^2 for separable data.
- voted/averaged variants stabilize the final weights.
## Worked example
- OR weights [1,1], b = -1: scores -1, 0, 0, 1 -> step gives 0,1,1,1.
- XOR best plane gets 2/4: pairs (0,1),(1,0) vs (0,0),(1,1) interleave.
- 38 updates in 10 passes: mistakes never stop, non-separability signature.
## Pitfalls
- Order dependence: different pass orders, different final weights.
- No probabilities: scores uncalibrated; use logistic head for those.
- Feature scaling changes convergence speed sharply.
## Connections
- Logistic regression is the smooth probabilistic sibling.
- MLP stacks perceptron-like units with differentiable activations.
## Exercises
1. Train on AND; read off w and b.
2. Start from w = [5,5], b = 5; count extra updates.
3. Show weights that learn NAND instead.
