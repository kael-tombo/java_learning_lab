# 08-optimization-fundamentals - Optimization Fundamentals
## Overview
Convex f (f'' > 0) has one global minimum; GD converges linearly with rate ((k-1)/(k+1))^2 where k is the condition number. Step lr must stay below 2/L (L = smoothness) or updates overshoot.
## Key formulas
- GD: w -= lr f'(w); stable iff lr < 2/L.
- Rate per step: ((k-1)/(k+1))^2.
## What the snippets show
- Mt08A: clean descent to 0.0967 in 5 steps.
- Mt08B: cond 10, rate 0.6694, overshoot demo at lr=0.19.
## Try it
Set lr=0.05 in Mt08A and count extra steps to the same loss.
## Formula reference
- Convex: f'' >= 0 (f(tx+(1-t)y) <= t f(x)+(1-t) f(y)); one global min.
- GD linear rate ((k-1)/(k+1))^2; optimal lr = 2/(L+mu) for quadratics.
- L-smooth: ||grad f(x)-grad f(y)|| <= L||x-y||; stable lr < 2/L.
## Worked example
- f = (w-1)^2: L = 2, mu = 2, k = 1 -> one step with lr 0.5 exact.
- lr 0.2: contraction |1 - 0.2*2| = 0.6 per step; 0.6^4*16 = 2.07... matches t1 2.0736.
- k = 10: rate (9/11)^2 = 0.6694; lr 0.19 vs limit 0.2 oscillates.
## Pitfalls
- Non-convex (neural nets): saddles/plateaus, no global guarantees.
- lr at the edge: fast then divergent; stay comfortably below 2/L.
- Ill-conditioning dominates wall-clock; precondition or adapt.
## Connections
- Momentum/Adam labs accelerate this exact dynamic.
- Init + norm control the effective k of deep nets.
## Exercises
1. Set lr = 0.05; count steps to 0.1 loss.
2. Derive contraction |1 - lr*2| for lr = 0.2.
3. Repeat Mt08A from w = -3.
