# 05-transformer-from-scratch - Transformer
## Overview
Attention(Q,K,V) = softmax(QK^T/sqrt(d_k)) V. Scaling by sqrt(d_k) keeps dot products in softmax range. Multi-head splits d across heads; each head holds its own Q,K,V,O projections plus a 2-layer FFN.
## Key formulas
- Attention = softmax(QK^T/sqrt(d_k)) V.
- Per-head QKVO = 4*d*dk (here dk=d/heads toy: 128/head, 256 total).
## What the snippets show
- Dl05A: complete 2x2 score-to-weight computation.
- Dl05B: param budget for a d=8 toy block.
## Try it
Scale scores by 10x and confirm the distribution sharpens toward argmax.
## Formula reference
- Attention(Q,K,V) = softmax(QK^T/sqrt(d_k)) V; multi-head concat + W_O.
- Per block: 4 d^2 attention + 2 d d_ff FFN params (biases extra).
- Residual + LayerNorm around each sublayer (pre- or post-).
## Worked example
- Scores 1/sqrt(2) = 0.7071 diagonal; row softmax e^0.7071/(e^0.7071+1) = 0.6698.
- Symmetry: rows mirror because Q = K = I here.
- Toy d=8: 4*64 = 256 MHA; FFN 2*8*32 = 512.
## Pitfalls
- Forgetting sqrt(d_k): large-d softmax saturates to one-hot.
- Mask placement: causal vs padding masks differ; test both.
- Head dim vs model dim bookkeeping; dk = d/heads usually.
## Connections
- Variants lab: causal masks, GQA sharing, FlashAttention tiling.
- Positional lab supplies the order signal attention lacks.
## Exercises
1. Scale scores x10; observe sharpening.
2. Count params for d = 16, 4 heads.
3. Use Q != K; recompute one row.
