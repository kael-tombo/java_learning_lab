# 03-rnn-lstm-gru - RNNs, LSTMs, GRUs
## Overview
RNN: h_t = tanh(Wxh x + Whh h + b); gradients vanish over long gaps. LSTM adds input/forget/cell/output gates (4 param blocks); GRU merges to update/reset/new (3 blocks).
## Key formulas
- h_t = tanh(Wxh x_t + Whh h_{t-1} + b).
- Gate params: 4*(hd + h^2 + h) LSTM; 3x for GRU.
## What the snippets show
- Dl03A: hidden-state trajectory with hand-checked first step.
- Dl03B: 416 vs 312 param inventory.
## Try it
Set Whh=0 and confirm each h depends only on its own x.
## Formula reference
- h_t = tanh(Wxh x + Whh h + b); BPTT multiplies Whh^T diag(1-h^2).
- LSTM: i,f,g,o gates; c_t = f*c + i*g; h_t = o*tanh(c_t).
- GRU: z,r gates; n candidate; h = (1-z)*n + z*h_prev.
## Worked example
- Step 1: 0.8*1 = 0.8 -> tanh 0.6640; step 2 adds 0.5*0.6640 = 0.332.
- Gate blocks: each h*d + h*h + h = 32+64+8 = 104; x4 = 416, x3 = 312.
- Ratio 312/416 = 0.75 exactly: one fewer gate block.
## Pitfalls
- tanh saturation kills BPTT gradients; LSTM cells bypass via addition.
- Stateful vs stateless batching: hidden carryover leaks across batches.
- d/h naming: d input dim, h hidden dim; keep consistent.
## Connections
- Attention replaced recurrence for long range (next lab).
- Gates reuse sigmoid from activations lab.
## Exercises
1. Zero Whh; confirm memoryless outputs.
2. Count GRU vs LSTM for d = 16, h = 32.
3. Unroll 5 steps with constant x = 1.
