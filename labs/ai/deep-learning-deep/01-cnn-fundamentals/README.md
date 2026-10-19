# 01-cnn-fundamentals - CNN Basics
## Overview
Convolution slides a KxK kernel with stride S and padding P: out = (W-K+2P)/S+1 per side. Params = Cout*(Cin*K*K) + Cout bias; same-padding (P=1,K=3,S=1) preserves size.
## Key formulas
- out = (W - K + 2P)/S + 1.
- params = Cout*Cid*K*K + Cout.
## What the snippets show
- Dl01A: four verified size cases (24/32/15/3).
- Dl01B: 608-param count plus hand-checked -4 outputs.
## Try it
Compute 224/7/3/2 by hand ((224-7+6)/2+1 = 112) and confirm in code.
## Formula reference
- Out = (W - K + 2P)/S + 1; same conv: P = (K-1)/2 at S = 1.
- Params = Cout*(Cin*K*K) + Cout; FLOPs ~= 2 * params * out_h * out_w.
- Valid (P = 0) shrinks; full padding grows; stride skips positions.
## Worked example
- (28-5)/1+1 = 24; (32-3+2)+1 = 32; (32-3)/2+1 = 15.5 -> 15 floor.
- (7-3)/2+1 = 3 exact; kernel [[1,0],[0,-1]] differences all -4.
- 8*3*25 = 600 weights + 8 biases = 608.
## Pitfalls
- Non-divisible sizes floor silently; check pooling chains end-to-end.
- Padding leaks border artifacts; valid avoids them at size cost.
- Channels-first vs last mixups transpose the wrong dims.
## Connections
- LeNet lab stacks these layers into a full budget.
- Separable convs factor this operation (advanced-architectures lab).
## Exercises
1. Verify 224/7/3/2 gives 112 by hand.
2. Count params for Cout = 16, Cin = 8, K = 3.
3. Convolve a constant patch; predict output.
