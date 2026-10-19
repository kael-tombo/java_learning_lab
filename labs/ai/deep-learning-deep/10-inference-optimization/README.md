# 10-inference-optimization - Inference Optimization
## Overview
Int8 quantization stores one byte/param (4x smaller than fp32) with <= scale/2 rounding error. Greedy decodes argmax; top-k renormalizes the top k probs. Batching/pipelining raise throughput at latency cost.
## Key formulas
- scale = max/127 (symmetric); err <= scale/2.
- top-k: p'_i = p_i / sum_topk.
## What the snippets show
- Dl10A: codes, scale, error, 4MB->1MB.
- Dl10B: greedy pick plus renorm arithmetic.
## Try it
Set k=1 in Dl10B and confirm top-k equals greedy.
## Formula reference
- Symmetric int8: scale = max|w|/127; q = round(w/scale); err <= scale/2.
- Size: fp32 4B, fp16 2B, int8 1B per param; KV cache scales likewise.
- Sampling: greedy argmax; top-k/top-p truncate then renormalize; temperature divides logits.
## Worked example
- Codes: -1/0.007874 = -127; -0.5 -> -63.5 -> -63; 0.5 -> 63.5 -> 64 (banker's? Math.round half-up: 63.5 -> 64).
- Max err 0.003937 = scale/2 exactly.
- Top-2: 0.6590+0.2424 = 0.9014; 0.6590/0.9014 = 0.7311.
## Pitfalls
- Rounding mode matters at .5 boundaries; document it.
- Temperature 0 equals greedy only in the limit; implement argmax directly.
- Quantized softmax needs care: dequantize logits first.
## Connections
- Model-compression lab covers pruning/distillation companions.
- KV-cache lab: quantization applies to cache too.
## Exercises
1. Set k = 1; confirm equals greedy.
2. Quantize max 2.0; new scale and codes.
3. Apply temperature 2.0 to the logits.
