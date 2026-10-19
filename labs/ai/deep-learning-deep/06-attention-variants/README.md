# 06-attention-variants - Attention Variants
## Overview
Causal masking sets future logits to -inf (query i attends to keys <= i). MQA/GQA share KV heads across query heads: KV cache divides by q_heads/kv_heads. FlashAttention tiles the same math IO-efficiently (same outputs).
## Key formulas
- Causal: attn[i,j] = 0 for j > i (renormalized).
- GQA saving factor = q_heads / kv_heads (4x in demo).
## What the snippets show
- Dl06A: masked vs full rows side by side.
- Dl06B: 8192 vs 2048 element counts.
## Try it
Mask row 0 instead and confirm attention collapses to [1,0] trivially.
## Formula reference
- Causal: logits[i,j] = -inf for j > i, then softmax rows.
- GQA: kv_heads < q_heads; KV bytes scale with kv_heads.
- Sliding-window: attend to last w keys; linear-ish in T.
## Worked example
- Row [0.5,1.5]: e^-1 = 0.3679 -> [0.2689, 0.7311] full.
- Masked row 1: only self visible -> [0, 1] exactly.
- 2*4*2*64*2 bytes... elements 2048 vs 8192: factor 4 = 8/2.
## Pitfalls
- Mask dtype: -inf in fp16 becomes NaN via softmax; use large negative.
- GQA weight shapes: kv heads repeat/interleave per implementation.
- Sink tokens: initial positions attract mass; mask design matters.
## Connections
- KV-cache lab quantifies the memory this saves.
- RoPE/ALiBi lab gives length extrapolation companions.
## Exercises
1. Mask row 0 instead; explain the outcome.
2. Compute GQA bytes for kvh = 1.
3. Count hops saved vs full attention toy.
