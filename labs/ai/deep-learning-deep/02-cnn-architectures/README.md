# 02-cnn-architectures - CNN Architectures
## Overview
LeNet-5 (conv-pool-conv-pool-fc-fc-out) totals ~60k params from its stated shapes: 156 + 2416 + 48120 + 10164 + 850 = 61706. Stacked 3x3 kernels grow receptive field additively (3 -> 5) before pooling doubles stride effects.
## Key formulas
- Per-layer params as in 01; receptive field rf += (k-1)*stride_product.
- Pooling halves spatial dims (2x2 s2) without params.
## What the snippets show
- Dl02A: full LeNet budget computed from shapes, plus a toy 1392-param pair.
- Dl02B: rf trace 3/5/6.
## Try it
Change conv2 to 32 maps and recompute the total.
## Formula reference
- LeNet-5: conv5x5/6, pool, conv5x5/16, pool, fc120, fc84, out10.
- Receptive field: rf += (k-1) * stride_product; stride multiplies after pooling.
- Params dominated by first FC (120*400 = 48000 of 61706).
## Worked example
- conv1: 6*25 weights + 6 = 156; conv2: 16*6*25 + 16 = 2416.
- fc1: 120*400 + 120 = 48120; fc2 10164; out 850; total 61706.
- rf: 1 +2 +2 +1 = 6 after k3,k3,pool2 as printed.
## Pitfalls
- Quoting param counts from memory drifts; recompute from shapes.
- FC layers balloon params; modern nets use global average pooling.
- rf arithmetic ignores padding edge effects (approximate at borders).
## Connections
- Residual nets supersede plain stacks for depth.
- Init/norm labs explain why deep stacks train at all.
## Exercises
1. Set conv2 to 32 maps; recompute total.
2. Find which layer dominates the budget.
3. Compute rf after adding another pool.
