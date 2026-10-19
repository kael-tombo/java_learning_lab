# 09-advanced-architectures - Advanced Architectures
## Overview
Residuals (y = x + F(x)) give gradients an identity path, enabling very deep nets. Depthwise-separable convolutions split spatial and channel mixing, cutting params ~K^2 x. Stochastic depth drops whole residual branches in training.
## Key formulas
- Residual: y = x + F(x); dL/dx includes identity term.
- Separable params: Cin*K + Cin*Cout vs Cout*Cin*K.
## What the snippets show
- Nn09A: residual add plus 192 vs 88 param count.
- Nn09B: survival-path expectation 357/1024.
## Try it
Change K to 5 in Nn09A and watch the savings ratio improve.
## Formula reference
- Residual: y = x + F(x); gradient dL/dx = dL/dy (I + dF/dx).
- Depthwise separable: Cin*K*K + Cin*Cout vs Cout*Cin*K*K.
- Stochastic depth: keep block with prob p_l, rescale survivors.
## Worked example
- [1,2] + [0.1,-0.1] = [1.1,1.9]: identity dominates, F refines.
- 1D-kernel convention here: std 8*8*3 = 192; dw 8*3 + 8*8 = 88; ratio 0.4583.
- Survival paths 1.8^10 = 357.0 of 1024 exactly as printed.
## Pitfalls
- Dimension mismatch needs projection shortcut (1x1 conv).
- Separable convs lose cross-channel spatial coupling; stack more of them.
- Dropping too aggressively (low p) destabilizes early training.
## Connections
- DenseNet concatenates instead of adding (feature reuse variant).
- Boosting adds weak learners; residuals add layer refinements.
## Exercises
1. Set K = 5; recompute std vs separable counts.
2. Zero F(x); confirm identity passthrough.
3. Compute survival paths for keep 0.8, 5 layers.
