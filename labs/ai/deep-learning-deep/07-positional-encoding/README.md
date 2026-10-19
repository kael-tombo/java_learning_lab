# 07-positional-encoding - Positional Encoding
## Overview
Sinusoids PE(pos,2i)=sin(pos/10000^(2i/d)) give each position a unique phase vector. RoPE rotates Q/K pairs by angle proportional to position (relative via angle differences). ALiBi subtracts slope*|i-j| instead of adding vectors.
## Key formulas
- Sinusoid: sin/cos(pos / 10000^(2i/d)); wavelength grows geometrically.
- ALiBi score -= slope * distance; RoPE rotates by theta*pos.
## What the snippets show
- Dl07A: exact PE components plus 628.3 wavelength instance.
- Dl07B: ALiBi linear table and one RoPE rotation.
## Try it
Evaluate pos=0 and confirm PE is [0,1,0,1,...] pattern start.
## Formula reference
- PE(pos,2i) = sin(pos/10000^(2i/d)); PE(pos,2i+1) = cos(same).
- Wavelength 2 pi 10000^(2i/d): 2 pi at i = 0 to 2 pi*10000 at top.
- RoPE: rotate pair by angle pos*theta_i; ALiBi: score -= slope*dist.
## Worked example
- pos 1, d 4: divisors 1, 100; sin(1) = 0.8415, cos(1) = 0.5403.
- sin(0.01) = 0.0100, cos = 1.0000: slow dims barely move per step.
- ALiBi slope 0.5: distances 1,2,4,8 -> -0.5,-1,-2,-4 linear.
## Pitfalls
- Absolute PE extrapolates poorly past training length; relative/RoPE/ALiBi help.
- Even/odd interleave: keep sin/cos pairing aligned in code.
- Learned PE: same table shape, none of the extrapolation structure.
## Connections
- Attention is permutation-equivariant; this is its order input.
- Normalization keeps these added scales stable.
## Exercises
1. Evaluate PE at pos = 0.
2. Show ALiBi bias at dist 16, slope 0.25.
3. Rotate by pi; confirm sign flip.
