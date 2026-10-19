# 08-normalization-layers - Normalization
## Overview
BatchNorm normalizes over the batch (gamma/beta affine after); LayerNorm over features (batch-size independent); RMSNorm drops mean-centering, scaling by root-mean-square only.
## Key formulas
- y = gamma (x-mean)/sqrt(var+eps) + beta.
- RMS: x / sqrt(mean(x^2)+eps) * g.
## What the snippets show
- Nn08A: full normalize+affine arithmetic.
- Nn08B: LN vs RMS side by side on [1,2,3].
## Try it
Set gamma=1, beta=0 and verify outputs are exactly zero-mean.
## Formula reference
- BatchNorm: batch stats + running averages; gamma/beta learnable.
- LayerNorm: per-token stats; RMSNorm: scale-only, no centering.
- Pre-norm vs post-norm placement changes transformer training dynamics.
## Worked example
- [1,3,5,7]: mean 4, dev [-3,-1,1,3], var (9+1+1+9)/4 = 5.
- Normalized: [-1.3416,-0.4472,0.4472,1.3416]; x2+1 gives snippet outputs.
- RMS([1,2,3]) = sqrt(14/3) = 2.1602; 1/2.1602 = 0.4629 matches.
## Pitfalls
- BatchNorm batch-size 1 breaks; use LayerNorm/RMSNorm there.
- Train/eval stat mismatch shifts outputs; freeze running stats properly.
- eps placement inside sqrt; 1e-5 typical, 1e-6 for fp16.
## Connections
- Transformers standardize on LayerNorm/RMSNorm (batch-independent).
- Init + norm jointly control activation scale.
## Exercises
1. Set gamma = 1, beta = 0; verify zero mean.
2. Add 10 to inputs; compare LN vs RMS shifts.
3. Normalize [5,5,5]; handle the zero-variance case.
