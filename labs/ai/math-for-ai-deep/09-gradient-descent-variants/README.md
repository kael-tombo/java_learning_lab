# 09-gradient-descent-variants - GD Variants
## Overview
Momentum smooths with velocity; RMSprop scales by sqrt of running squared-grad average; Adam combines both with bias correction (divide by 1-b^t early on).
## Key formulas
- RMSprop: v = b v + (1-b) g^2; w -= lr g/(sqrt(v)+eps).
- Adam: bias-corrected mhat, vhat version of the same.
## What the snippets show
- Mt09A: three rules compared on identical state.
- Mt09B: two-step RMSprop cache trajectory.
## Try it
Feed constant g=0.5 for 5 RMSprop steps and watch v converge to 0.25.
## Formula reference
- Momentum: v = mu v + g; Nesterov: gradient at w - lr mu v.
- RMSprop: v = b v + (1-b) g^2; step lr g/(sqrt(v)+eps).
- Adam bias correction divides by (1-b^t); friends: AdamW, AdaFactor.
## Worked example
- g = 0.8: RMSprop v = 0.1*0.64 = 0.064; step 0.1*0.8/0.2530 = 0.3162.
- w: 2 -> 1.6838; next g = -0.4: v = 0.0576+0.016 = 0.0736.
- Adam t1 equals RMSprop+momentum t1 combined: mhat 0.8, vhat 0.64.
## Pitfalls
- eps inside sqrt; per-parameter scales differ wildly across layers.
- Adam generalizes slightly worse sometimes; try SGD late-phase.
- Stale moments after data shift; reset or warm up.
## Connections
- Backprop supplies g; schedulers scale lr over time.
- BatchNorm interacts with weight decay handling (AdamW decouples).
## Exercises
1. Feed g = 0.5 x5; watch v approach 0.25.
2. Zero b1 in Adam; compare t1 step.
3.  alternate signs; see cache smooth them.
