# 10-numerical-computing - Numerical Computing
## Overview
Log-sum-exp subtracts the max before exponentiating to avoid overflow. Float32 has ~7 decimal digits: repeated 0.1 adds accumulate error; float64 (~16 digits) stays exact here.
## Key formulas
- lse = m + log(sum e^(z_i - m)), m = max z.
- 0.1 is periodic in binary: neither float type stores it exactly.
## What the snippets show
- Mt10A: 1002.4076 stable vs Infinity naive.
- Mt10B: err32=1.44 vs err64=0.0000.
## Try it
Compute softmax of [1000,1001,1002] via lse and confirm weights [0.09,0.245,0.665].
## Formula reference
- lse = m + log(sum e^(z_i - m)); softmax_i = e^(z_i - lse).
- fp32 ~7 digits, fp64 ~16; machine eps 2^-23 vs 2^-52.
- Kahan summation compensates accumulation error in long sums.
## Worked example
- Diffs [-2,-1,0]: e^-2 0.1353, e^-1 0.3679, sum 1.5032, log 0.4076.
- lse 1002.4076; softmax row = [0.0900, 0.2447, 0.6652].
- 0.1 error: float32 sum off by 1.44/10000 = 1.4e-4 relative.
## Pitfalls
- exp of large logits overflows; always subtract max first.
- float32 reductions over millions of terms drift; accumulate in fp64.
- Comparing floats: use tolerances, never ==.
## Connections
- Stable softmax powers attention and CE heads.
- Log-domain arithmetic recurs in HMM/CTC-style losses.
## Exercises
1. Softmax [1000,1001,1002] via lse.
2. Sum 1e6 x 0.1 in float vs double.
3. Trigger exp overflow without the max trick.
