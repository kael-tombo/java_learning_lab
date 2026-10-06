# deep-learning-deep — Math Foundation

## 1. Convolution as a Linear Map

A 2D convolution is a linear operator; `im2col` turns it into a matrix multiply:

```
out = col2im(W' * col(im)) + b      W' is (C_out*k*k) x (C_in*k*k)
```

Parameter count: `k^2 * C_in * C_out`, independent of `n`. A dense layer covering the same
receptive field needs `(k*n)^2 * C_out` parameters — for `k=3, n=224, C=64` that is 2.9e9
versus 36,864.

Output size: `floor((n + 2p - k)/s) + 1`.

**Receptive field recurrence**: `r_l = r_{l-1} + (k_l - 1) * j_{l-1}`, with jump
`j_l = j_{l-1} * s_l`. For `L` 3x3 stride-1 layers: `r = 1 + 2L`. With stride 2 every other
layer: `r` grows by 4 per two layers.

## 2. Attention Derivation

```
score_ij = q_i . k_j / sqrt(d_k)
attn_ij  = softmax_j(score_ij)                (row sums to 1)
out_i    = sum_j attn_ij v_j
```

**Why the scaling.** Assume `q_i` and `k_j` have i.i.d. zero-mean unit-variance entries.
Then `q_i . k_j = sum_{d=1}^{d_k} q_d k_d` has mean 0 and variance `d_k`, so the standard
deviation is `sqrt(d_k)`. Dividing by `sqrt(d_k)` restores unit variance.

**What saturation does.** For a logit with standard deviation `s`, the softmax entropy is
approximately `log(d) + s^2/2` for small `s`, and collapses toward 0 as `s` grows. With
`d_k = 64`, unscaled scores have `s = 8`; softmax over 64 positions is nearly a one-hot with
near-zero gradient. Scaled, `s = 1`, entropy ~4.1 nats, healthy gradient. This is the
entire reason the factor exists.

**Gradient of softmax** (why saturation kills learning):

```
d attn_ij / d score_ik = attn_ij (delta_jk - attn_ik)
```

Both terms are bounded by `attn`, which goes to zero as saturation sets in. Vanishing
gradients, from arithmetic rather than depth.

## 3. Multi-Head Analysis

For `H` heads each of dimension `d_h = d_model / H`:

```
head_h = softmax(Q_h K_h' / sqrt(d_h)) V_h
MultiHead = Concat(head_1..head_H) W_O
```

Parameters: `4 * d_model^2` (Q, K, V, and output projections) regardless of `H`. Heads
count therefore changes representation, not cost. Practical default: `d_head` in 64-128.

The FFN: `2 * d_model * d_ff`, typically `4 * d_model * d_model * 2 = 8 * d_model^2`. So
**the FFN holds twice the parameters of attention** in a standard block. Attention is the
interesting part; it is not the parameter-heavy part.

## 4. Sinusoidal Positional Encoding

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
```

Two structural properties:

1. **Uniqueness**: different frequencies mean no two positions have the same vector.
2. **Relative offsets as linear combinations**:

```
PE(pos + m) = R_m * PE(pos)
```

where `R_m` is a rotation depending only on `m`. This is why the encoding supports lengths
never seen in training — `R_m` exists for every `m`.

**Geometric frequency spacing**: frequencies range from 1 down to `1/10000`, so low
dimensions encode coarse position and high dimensions encode fine position.

## 5. RoPE

Apply a block-diagonal rotation to `Q` and `K`:

```
q'_i = R(i) q_i,   k'_j = R(j) k_j
q'_i . k'_j = q_i' R(j-i) k_j'
```

The inner product depends only on `i - j` — **relative position emerges from an absolute
rotation**. No learned parameters, no interpolation table, and it composes with the causal
mask unchanged.

Cost: `R(i)` is block-diagonal 2x2 rotations, so the elementwise multiply is cheaper than
an attention-matrix offset bias. For context extension, **interpolating the frequency
spectrum** (dividing positions by a factor) buys longer context at some quality cost.

## 6. ALiBi

Add to the scores, per head `h`:

```
score_ij += -m_h * |i - j|
```

No parameters, no positional vectors. Geometric distance is a strong prior for language
modelling, and the bias is *monotone in distance*, so it extrapolates to any length
unchanged. Heads with larger `m_h` learn local patterns; smaller `m_h` learn long-range.

## 7. LSTM Gradient Path

Cell state recurrence: `c_t = f_t .* c_{t-1} + i_t .* g_t`.

```
dL/dc_T = dL/dc_t * (prod_{k=t+1..T} f_k) + (direct terms)
```

Because `f_k in (0,1)`, the product decays at worst exponentially if all gates close, but
in practice gates learn to stay near 1 on the gradient-carrying path. Compare with the
vanilla RNN's pure product `prod (W_h' diag(tanh'))`, which decays as
`(||W_h|| * 1)^T` — exponential in `T`.

**Parameter count**: LSTM has 4 gates each with `d_h + d_in` inputs and `d_h` outputs, so
`4 * ((d_h + d_in) * d_h + d_h)` per layer. GRU has 3 gates minus the extra cell output
(`W` and `U` combined): `3 * ((d_h + d_in) * d_h + d_h) + 2 * d_h`. Ratio is about 3/4.

## 8. KV Cache Arithmetic

```
cache_bytes(token) = 2 * L * H * d_head * bytes
```

Example: `L=32, H=32, d_head=128, FP16`: `2 * 32 * 32 * 128 * 2 = 524,288 bytes` = 512 KB
**per token per sequence**.

| Context | Per sequence | 32 concurrent |
|---------|--------------|---------------|
| 2,048 | 1.0 GB | 32 GB |
| 8,192 | 4.0 GB | 128 GB |
| 32,768 | 16.0 GB | 512 GB |

**This is the real constraint on context length and batch size.** Weights are a fixed cost
(7B params at INT8 = 7 GB); the cache scales with `batch x context`, and it is usually
larger.

Reductions:

```
MQA:  cache = 2 * L * 1 * d_head * bytes          -> 1/H of MHA
GQA:  cache = 2 * L * (H/g) * d_head * bytes       -> g/H of MHA
Sliding window w: cache = 2 * L * H * d_head * w * bytes   (bounded)
```

## 9. Arithmetic Intensity of Decode

Each decode step performs `2 * P` FLOPs (one multiply-accumulate per weight, times two for
the two matmuls) and reads `P * b` bytes of weights:

```
arithmetic_intensity = FLOPs / bytes = 2 / b
```

For FP16 weights (`b=2`): intensity **1 FLOP per byte**. A GPU delivering 300 TFLOPS and
1.8 TB/s is compute-bound only above ~1.8 FLOP/byte. At intensity 1, it is firmly
**bandwidth-bound**: the roofline time per token is

```
t_token = P * b / bandwidth
```

For a 7B model at INT8 (`b=1`) on 1.8 TB/s: `7e9 / 1.8e12 = 3.9 ms/token` = 256
tokens/second for a single sequence, regardless of arithmetic. Every optimization that
reduces bytes read is a direct multiple on throughput:

| Optimization | Bytes per token | Effect |
|--------------|-----------------|--------|
| FP32 baseline | 4 | 1x |
| FP16 | 2 | 2x |
| INT8 | 1 | 4x |
| GQA (g=8, H=32) | KV cache /4 | more concurrency, not speed per sequence |
| Speculative (accept 3 of 4) | 1 per 3.3 tokens | ~3.3x |

## 10. Quantization Error in Attention

Round weights to a grid of step `s`: error `e` uniform on `[-s/2, s/2]`, so
`E[e^2] = s^2/12`. For symmetric INT8, `s = max|w| / 127`.

Activation outliers matter: if activations `x` have a large dynamic range driven by a few
channels, per-tensor activation quantization loses precision on the bulk. AWQ's response is
activation-aware scaling — identify salient weight channels (top `p%` by activation
magnitude) and protect them from scaling, scaling the rest instead.

For KV cache quantization, keys and values have different sensitivity: **value quantization
is generally more damaging than key quantization**, because values are summed with attention
weights while key errors distort the softmax logits before normalization.

## 11. FlashAttention: Online Softmax

Exact attention without materializing `S = QK'`:

For each block, rescale previously accumulated statistics:

```
m_new = max(m_old, max(S_block))
l_new = exp(m_old - m_new) * l_old + sum(exp(S_block - m_new))
O_new = exp(m_old - m_new) * O_old + (exp(S_block - m_new) / l_new) @ V_block
```

Algebraically identical to the naive computation — the running max keeps the exponentials
stable. The win is memory traffic: the `n x n` score matrix never reaches HBM, so the
operation becomes IO-bound on `Q`, `K`, `V` alone, which is `O(n d)`.

Measured: 2-4x speedup and 5-10x memory reduction on long sequences, with outputs matching
naive attention to within floating-point error.

## 12. Continuous Batching Arithmetic

With static batching of size `B` and sequence lengths `l_1..l_B`, GPU idle time is
`(B * max(l) - sum(l)) / (B * max(l))`. With lengths uniform on `[1, L]`, expected idle
fraction is `~1/3`.

Continuous batching eliminates this: the scheduler admits a new sequence whenever one
finishes. Expected utilization approaches the compute limit, which is the throughput
multiplier. In practice 2-5x over static batching — the single largest serving win
available short of better hardware.

## 13. Speculative Decoding Acceptance

Draft `k` tokens; the target verifies all `k` in one forward pass. If `alpha` is the
probability the draft model agrees with the target:

```
E[accepted tokens] = sum_{i=1..k} alpha^i
```

With `alpha = 0.8`, `k = 5`: `0.8 + 0.64 + 0.512 + 0.41 + 0.328 = 2.69` tokens per target
pass. If a target pass costs `T` and the draft costs `T_d`:

```
speedup = E[accepted] / (1 + k * T_d / T)
```

With `T_d/T = 0.05` and `k = 5`: `2.69 / 1.25 = 2.15x`. With `k = 8`, `alpha = 0.8`:
`sum_{i=1..8} 0.8^i = 3.33`, `3.33 / 1.4 = 2.38x` — diminishing returns because more
speculative tokens are wasted.

## Worked Numbers

- **Conv parameters**: 3x3 conv, `C_in = 64`, `C_out = 64` -> `9 * 64 * 64 = 36,864`.
  Depthwise separable: `9*64 + 64*64 = 576 + 4096 = 4,672`. Ratio 7.9x. For `k=3, C=64`
  the dense-separable saving is closest to the theoretical `k^2 = 9` when
  `C_in ≈ C_out`.
- **Receptive field**: 50 layers, 3x3 stride 1 -> `1 + 2*50 = 101`. With stride 2 every 4th
  layer, the field at layer 50 is `1 + sum over strides`, and the feature-map resolution
  drops by `2^12` — the actual constraint on deep plain CNNs.
- **Attention scaling**: `d_k = 64`. Unscaled logit std = 8. Softmax entropy for
  `s=8` over 64 keys is < 0.05 nats (near one-hot, gradient ~1e-3). Scaled `s=1`: entropy
  ~4.1 nats, gradients ~1e-2 to 1e-1. Roughly 100x gradient magnitude difference.
- **KV cache**: `L=32, H=32, d=128, FP16`, context 8,192 -> `2 * 32 * 32 * 128 * 2 *
  8192 = 4.29 GB` per sequence. A 7B model in FP16 is 14 GB. At batch 8 the cache alone is
  34 GB — larger than the weights. This is why GQA exists.
- **GQA saving**: 32 heads, 8 KV groups -> `1/4` of the cache, 2.1 GB per sequence at 8,192
  context. Batch 16 fits in 34 GB.
- **Decode bandwidth**: 7B at INT8, 1.8 TB/s -> `7e9 / 1.8e12 = 3.89 ms` per token = 257
  tok/s for one sequence. At batch 32, if compute allows, throughput could reach ~8,000
  tok/s; batch is limited by cache memory, not compute.
- **Static versus continuous batching**: `B=16`, lengths uniform `[1,1024]` -> mean 512,
  static utilization `512/1024 = 50%`; continuous approaches 90%+. ~1.8x throughput from
  batching alone.
- **Speculative**: `alpha=0.8, k=5, T_d/T=0.05` -> 2.15x. Drafting too long (`k=10`) ->
  `sum = 3.58`, `3.58/1.5 = 2.39x` — 2% more speedup for 2x the draft cost.
- **FlashAttention memory**: naive `n x n` FP16 at `n = 32,768` = 2 GB per head per layer.
  FlashAttention needs only `O(n d)` = 8 MB. 256x reduction, which is why long context
  without tiling is infeasible.

## Self-Check Questions

1. Derive why attention is divided by `sqrt(d_k)`.
2. Compute the output shape of a convolution for `n=27, k=5, s=2, p=2`.
3. Compute the receptive field for 20 layers of 3x3 with stride 2 every 5th layer.
4. Derive the KV cache size for a 40-layer, 40-head, `d_head=128` model at 16,384 context
   in INT8, and the GQA-8 equivalent.
5. Show that the softmax gradient vanishes as the score standard deviation grows.
6. Derive the LSTM cell-state gradient path and compare with the vanilla RNN product.
7. Compute the expected accepted tokens for speculative decoding at `alpha = 0.7, k = 4`.
8. Compute decode tokens/second for a 13B model at FP16 on a 2.0 TB/s device, assuming
   bandwidth-bound operation.
9. Compute static-batching GPU utilization for lengths uniform on `[1, 512]` at batch 32.
10. Show that `PE(pos+m) = R_m PE(pos)` for sinusoidal encodings and state the consequence
    for length extrapolation.
