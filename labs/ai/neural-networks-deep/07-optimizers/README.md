# 07-optimizers - Optimizers
## Overview
Momentum accumulates velocity v = mu v + g to speed consistent directions. Adam keeps bias-corrected first/second moments and steps lr*mhat/(sqrt(vhat)+eps) per parameter.
## Key formulas
- Momentum: v = mu v + g; w -= lr v.
- Adam: mhat = m/(1-b1^t); vhat = v/(1-b2^t).
## What the snippets show
- Nn07A: velocity buildup over 3 steps.
- Nn07B: exact Adam mhat/vhat trajectory.
## Try it
Set mu=0 in Nn07A and confirm it reduces to plain SGD (w=0.96,0.92,0.88).
## Formula reference
- SGD: w -= lr g; momentum v = mu v + g; Nesterov looks ahead.
- Adam: mhat/(sqrt(vhat)+eps), defaults b1 0.9, b2 0.999, eps 1e-8.
- Effective step bounded by lr (when vhat ~= mhat^2).
## Worked example
- Momentum velocities 0.4, 0.76, 1.084: geometric series ratio 0.9 + 0.4.
- w after 3: 1 - 0.1*(0.4+0.76+1.084) = 0.7756.
- Adam t2: mhat 0.3474, vhat 0.1250, step 0.1*0.3474/0.3536 = 0.0983.
## Pitfalls
- Adam default eps swamps tiny gradients in fp16; raise or use fp32 master.
- Momentum + noisy grads overshoots ravines; lower lr or mu.
- Comparing optimizers needs equal tuning budgets.
## Connections
- RMSprop is Adam without momentum (beta1 = 0).
- Schedulers (cosine/step) multiply these updates over time.
## Exercises
1. Set mu = 0; verify plain-SGD trajectory.
2. Run Adam 5 steps on g = 0.1 constant.
3. Tune lr so momentum overshoots w < 0.
