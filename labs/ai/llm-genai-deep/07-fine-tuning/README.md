# 07-fine-tuning - Fine-Tuning and LoRA
## Overview
LoRA freezes W and trains low-rank delta BA (r << d,k), scaled by alpha/r. Trainable count r*(d+k) vs full d*k: rank 4 on 64x64 is 1/8 the params.
## Key formulas
- Delta = (alpha/r) B A; trainable = r*(d+k).
- Base frozen: only A,B get gradients.
## What the snippets show
- Lg07A: 512 vs 4096 with 0.1250 ratio.
- Lg07B: scale 2.0 and 0.2500 update.
## Try it
Set r=8 and confirm the ratio doubles to 0.25.
## Formula reference
- LoRA: W' = W + (alpha/r) B A; A ~ N(0,1), B = 0 start (delta 0).
- Trainable r(d+k) vs dk full; rank trades capacity for params.
- Target modules usually Q,V (sometimes all); alpha/r scales updates.
## Worked example
- 4*(64+64) = 512; 64*64 = 4096; 512/4096 = 0.125.
- scale 8/4 = 2.0; update 2.0 * B A x with toy values = 0.25.
- r=8 doubles to 1024/4096 = 0.25 (linear in r).
## Pitfalls
- Rank too low for hard style shifts; raise r or target more modules.
- Forgetting base freeze trains everything (not LoRA anymore).
- Merged vs unmerged inference: merge for speed, keep adapter for swapping.
## Connections
- RLHF SFT stage often uses LoRA for efficiency.
- Quantized base + LoRA (QLoRA) compresses further.
## Exercises
1. Set r = 8; confirm ratio 0.25.
2. Scale alpha = 4; recompute update.
3. Count LoRA for d = k = 256, r = 8.
