# 04-seq2seq-attention - Seq2Seq Attention
## Overview
Bahdanau-style attention scores each encoder state against the decoder state, softmaxes to weights alpha, and returns the weighted sum (context vector) so the decoder sees all positions.
## Key formulas
- alpha_i = softmax(score_i); c = sum alpha_i h_i.
- Scores classically v^T tanh(W s + U h); here fixed for arithmetic.
## What the snippets show
- Dl04A: weight computation with sum-to-1 check.
- Dl04B: exact context [0.70,0.80].
## Try it
Set scores equal and confirm uniform weights 1/3 each.
## Formula reference
- score(s, h_i); alpha = softmax(scores); c = sum alpha_i h_i.
- Decoder conditions on c each step; bottleneck of fixed vector removed.
- Coverage/fertility extensions penalize repeated attention.
## Worked example
- Denominator e^1+e^2+e^0.5 = 2.718+7.389+1.649 = 11.756.
- alpha_1 = 7.389/11.756 = 0.6285; check sum 0.2312+0.6285+0.1402 = 1.0.
- c = [0.2*1+0.3*0+0.5*1, 0.2*0+0.3*1+0.5*1] = [0.7, 0.8].
## Pitfalls
- Attention != explanation: weights do not certify causality.
- Long sequences flatten softmax; scale/sharpen or segment.
- Exposure bias: teacher-forced training vs free-run inference.
## Connections
- Transformer self-attention generalizes this to all-pairs.
- RAG retrieval weights echo alignment weights conceptually.
## Exercises
1. Uniform scores; confirm 1/3 weights.
2. Mask alpha_2 = 0; renormalize the rest.
3. Build c for one-hot alpha = [0,1,0].
