# 02-mlp-backprop - MLP and Backprop
## Overview
MLP stacks affine maps with nonlinearities; backprop applies the chain rule layer by layer, giving (p - t) x style gradients at a sigmoid+cross-entropy head.
## Key formulas
- Forward: h = sigma(W1 x + b1); o = W2 h + b2.
- Head gradient: dL/dz = p - t; dL/dW = (p-t) x.
## What the snippets show
- Nn02A: full numeric forward pass (h=[0.5622,0.4134], out=0.1720).
- Nn02B: gradient values plus one descent step.
## Try it
Zero W2 in Nn02A and confirm the output collapses to b2.
## Formula reference
- h = sigma(W x + b); o = V h + c; dL/dV = (p-t) h^T at CE head.
- Hidden delta: (V^T (p-t)) * sigma'(z); then dL/dW = delta x^T.
- Gradient check: central differences must match to ~1e-5.
## Worked example
- z1 = 0.4*0.5 + 0.1*(-0.5) + 0.1 = 0.25 -> sigmoid 0.5622.
- z2 = -0.2*0.5 + 0.3*(-0.5) - 0.1 = -0.35 -> sigmoid 0.4134.
- out = 0.6*0.5622 - 0.4*0.4134 = 0.1720; dL/dw = -0.2251 verified.
## Pitfalls
- Forgetting the sigma' factor silently passes wrong gradients.
- Vanishing gradients in deep sigmoid stacks; prefer ReLU + good init.
- Mean vs sum loss changes lr scale; be consistent.
## Connections
- Optimizers consume these gradients (momentum/Adam labs).
- Init schemes keep this forward pass variance stable.
## Exercises
1. Zero W2 and confirm output equals b2.
2. Backpropagate dL/do = 1.0 one layer by hand.
3. Check the gradient with central differences.
