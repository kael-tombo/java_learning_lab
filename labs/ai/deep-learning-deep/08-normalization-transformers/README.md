# 08-normalization-transformers - Normalization
## Overview
LayerNorm: (x - mean)/sqrt(var+eps) * g + b per token; output zero-mean unit-variance before affine. RMSNorm skips centering: x/rms(x) * g, cheaper with similar stability.
## Key formulas
- LN = g (x-mean)/sqrt(var+eps) + b.
- RMS = g x/sqrt(mean(x^2)+eps).
## What the snippets show
- Dl08A: LN with mean/var certificate.
- Dl08B: RMS values plus rms=2.1602.
## Try it
Add constant 10 to inputs: LN unchanged, RMS outputs change (centering matters).
## Formula reference
- LN(x) = g (x - mean)/sqrt(var + eps) + b over feature dim.
- RMS(x) = g x/sqrt(mean(x^2) + eps): translation-sensitive by design.
- Pre-norm: x + Sublayer(Norm(x)); post-norm: Norm(x + Sublayer(x)).
## Worked example
- var([1,2,3]) = (1+0+1)/3 = 0.6667; std 0.8165; -1/0.8165 = -1.2247.
- Square-sum check: 1.5+0+1.5 = 3.0 = n (unit variance certificate).
- RMS 2.1602; 2/2.1602 = 0.9258 middle entry.
## Pitfalls
- eps too small in fp16: sqrt of tiny var overflows outputs.
- Normalizing across batch in transformers breaks independence; use per-token.
- Forgetting affine after norm limits expressivity (keep g,b).
## Connections
- BatchNorm lab covers the batch-statistics sibling.
- Init schemes assume stable norms like these.
## Exercises
1. Prove LN shift-invariance numerically.
2. Normalize [5,5,5]; handle zero variance.
3. Apply learned g = 2; rescale outputs.
