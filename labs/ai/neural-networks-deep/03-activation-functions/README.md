# 03-activation-functions - Activations
## Overview
Sigmoid squashes to (0,1), tanh to (-1,1), ReLU is max(0,x). Derivatives govern gradient flow: sigmoid saturates (max slope 0.25), ReLU passes 1 for x>0 and 0 otherwise (dead units possible).
## Key formulas
- sigmoid'=p(1-p); tanh'=1-t^2; ReLU'=1 if x>0 else 0.
- Saturation: |z| large -> near-zero gradient for sigmoid/tanh.
## What the snippets show
- Nn03A: value table across -2..2.
- Nn03B: derivative table confirming 0.25/1.0 peaks.
## Try it
Evaluate leaky ReLU (0.01x for x<0) alongside and compare slopes.
## Formula reference
- sigmoid p(1-p) <= 0.25; tanh' = 1 - t^2 <= 1; ReLU' in {0,1}.
- GELU/SiLU smooth ReLU variants; softmax generalizes sigmoid to k classes.
- Dead ReLU: always-negative pre-activation gives permanent zero gradient.
## Worked example
- sigmoid(2) = 0.8808, slope 0.1050 = 0.8808*0.1192.
- tanh(2) = 0.9640, slope 0.0707 = 1 - 0.9293.
- At 0: slopes 0.25 / 1.0 / 0-or-1: tanh steepest, sigmoid flattest.
## Pitfalls
- Sigmoid hidden stacks saturate; reserve sigmoid for gates/outputs.
- ReLU lr too high kills units; monitor dead-unit fraction.
- Tanh inputs should be standardized (zero-centered helps).
## Connections
- Gates in LSTM/GRU are sigmoid by design (0..1 switches).
- Losses pair with output activations: CE+sigmoid/softmax, MSE+linear.
## Exercises
1. Tabulate leaky ReLU (0.01 slope) at -2..2.
2. Find where sigmoid slope drops below 0.01.
3. Prove tanh = 2 sigmoid(2x) - 1 numerically.
