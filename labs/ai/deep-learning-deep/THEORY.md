# deep-learning-deep — Theory

Track-level theory for the ten deep learning modules: CNNs, sequence models, attention,
transformers, positional encodings, normalization, KV cache, and inference optimization.

## 1. CNN Fundamentals

Convolution slides a filter over the input, sharing weights across positions:

```
out[i][j] = sum_{u,v} in[i+u][j+v] * k[u][v] + b
output size = floor((n + 2p - k) / s) + 1
```

- **Parameter sharing** is the point: a 3x3x64x64 conv has 36,864 parameters regardless of
  image size. A dense layer would be size-dependent and would not generalize to new sizes.
- **Receptive field**: one 3x3 conv sees 3x3; stacking `L` of them with stride 1 grows the
  field by 2 per layer (`2L+1`). Depth buys receptive field; pooling or stride buys it
  faster while losing resolution.
- **Padding choice**: `same` preserves resolution (needed for segmentation), `valid`
  shrinks it (fine for classification since the final layer is global).
- **Dilation** widens the receptive field without extra parameters or downsampling — the
  standard tool when the field must grow but resolution must not drop.
- Translation equivariance is exact; translation invariance comes only from pooling or
  global average pooling.

## 2. CNN Architectures

| Model | Contribution |
|-------|--------------|
| LeNet-5 | Conv + pool + fully connected; the template |
| AlexNet | ReLU, dropout, GPUs, huge convs |
| VGG | 3x3 stacks, homogeneous depth; showed depth wins |
| ResNet | Skip connections; made 50+ layers trainable |
| EfficientNet | Compound scaling (depth, width, resolution together) |
| MobileNet | Depthwise separable convolution; mobile FLOP budget |
| ConvNeXt | Convolution arranged like a transformer block |

- **Depthwise separable convolution**: depthwise (per-channel spatial) then pointwise
  (1x1 channel mixing). `k^2 * C` + `C * C'` parameters versus `k^2 * C * C'` — for
  `k=3, C=C'=64`, 576 versus 36,864 parameters, a 64x reduction for a small accuracy cost.
- The ResNet finding generalizes: **skip connections help every deep architecture**,
  including recurrent ones (highway connections) and transformers (residual streams).
- Modern practice: residual blocks + normalization + strong augmentation, and depth
  determined by the deployment budget, not by a leaderboard.

## 3. RNN, LSTM, GRU

A recurrent layer applies the same weights at every timestep, so it can process any length
with `O(1)` parameters per step.

```
h_t = tanh(W_x x_t + W_h h_{t-1} + b)
```

- **BPTT**: the gradient backpropagates through the whole unrolled graph, so the same
  vanishing-gradient product reappears across time.
- **LSTM** adds a cell state and three gates: forget, input, output.

```
f_t = sigma(W_f [h_{t-1}, x_t] + b_f)
i_t = sigma(W_i [h_{t-1}, x_t] + b_i)
o_t = sigma(W_o [h_{t-1}, x_t] + b_o)
c_t = f_t .* c_{t-1} + i_t .* tanh(W_c [h_{t-1}, x_t] + b_c)
h_t = o_t .* tanh(c_t)
```

- **GRU** merges input and forget gates and drops the cell state: two gates, faster, often
  as good on small tasks.
- The additive cell update `c_t = f_t .* c_{t-1} + ...` is the key: the gradient path is a
  **sum** through time with a multiplicative gate bounded by 1, so it neither explodes nor
  vanishes as easily as a product.
- Failure: LSTM does not fix long-range dependencies, it makes them learnable. For very
  long sequences, attention is the better tool.

## 4. Seq2Seq with Attention

Encoder-decoder without attention compresses the entire input into one fixed vector — a
bottleneck that loses detail and lengthens the gradient path.

Bahdanau (additive) attention:

```
e_ij  = v' tanh(W [h_{i-1}, s_j])
alpha_ij = softmax_j(e_ij)
c_i   = sum_j alpha_ij s_j
```

Luong (multiplicative) attention: `e_ij = s_i' W s_j`, which is faster and works well with
dot-product attention.

- **Teacher forcing** trains with ground-truth previous tokens; at inference the model
  consumes its own output, so exposure bias appears. Scheduled sampling and beam search
  are the two practical mitigations.
- **Beam search** keeps the `k` best partial sequences; the length penalty matters because
  beam search otherwise favours short outputs.

## 5. Transformer From Scratch

Scaled dot-product attention:

```
Attention(Q,K,V) = softmax(Q K' / sqrt(d_k)) V
```

The `1/sqrt(d_k)` is not a tuning knob. For `d_k` independent unit-variance dot products,
the variance of `Q K'` is `d_k`, so without scaling the softmax saturates and its gradient
vanishes.

- **Multi-head**: `h` heads in parallel, each with its own projection, concatenated and
  projected. Heads specialize; the count matters less than the total width.
- **Causal masking**: position `i` may attend to positions `<= i`, implemented as adding
  `-inf` before the softmax.
- **Feed-forward network**: two linear layers with a nonlinearity, `d -> 4d -> d`, applied
  per position. It holds the majority of parameters in most transformers — attention is
  the famous part but not the parameter-heavy part.
- **Residual + pre-norm** around both sublayers, which is what makes depth trainable.

## 6. Attention Variants

- **Self-attention**: `Q = K = V` from the same sequence.
- **Cross-attention**: `Q` from the decoder, `K, V` from the encoder.
- **Causal attention**: a masked self-attention.
- **RoPE**: applies a rotation to `Q` and `K` by position, so the dot product encodes
  relative distance. Decodes to relative position with no learned parameters and no
  interpolation table.
- **ALiBi**: adds a linear bias `-m * (i - j)` to the scores. No parameters at all, and it
  extrapolates to longer contexts.
- **FlashAttention**: an IO-aware tiling of the same exact attention. Mathematically
  identical; faster because it avoids materializing the `n x n` score matrix in HBM. The
  point is that the attention *maths* was never the bottleneck — memory movement was.

## 7. Positional Encoding

- **Sinusoidal**: `PE(pos, 2i) = sin(pos / 10000^(2i/d))`, `PE(pos, 2i+1) = cos(...)`.
  Unique per position, relative offsets are linear combinations, and the formula extends
  to unseen lengths.
- **Learned absolute**: a lookup table; simple, but does not extrapolate past the trained
  length.
- **Relative position bias**: a learned bias per relative distance, added to the scores.
- **NoPE**: with causal attention and no positional signal at all, models still learn
  position from the mask's asymmetry — but decode badly without it, and long-context
  behaviour is unpredictable.
- Practical: RoPE or ALiBi for modern LLMs; sinusoidal is mostly historical, retained
  because the extrapolation property is instructive.

## 8. Normalization in Transformers

- **LayerNorm** over hidden dimensions, per position. Batch-independent, which matters
  because sequence lengths and batch composition vary.
- **RMSNorm** drops the mean subtraction; one pass instead of two, and empirically equal
  quality. Common in large stacks.
- **Pre-norm vs post-norm**: `x + F(LN(x))` versus `LN(x + F(x))`. Pre-norm keeps the
  residual path identity-like, so gradients reach early layers intact; post-norm requires
  careful warmup at depth. Nearly all modern models use pre-norm, often with a final norm.
- **Sandwich norm** (norm before and after the sublayer) is a middle ground with a small
  cost.
- Gradient checkpointing trades compute for activation memory by recomputing during
  backward; combined with pre-norm it makes very long-context training feasible.

## 9. KV Cache

Autoregressive decoding recomputes all previous keys and values at every step, which is
`O(n^2)` work for one generated token. Caching them makes each step `O(n)`.

```
memory = 2 * layers * heads * head_dim * seq_len * bytes   (K and V)
```

For a 32-layer, 32-head, `d_head = 128` model in FP16: `2 * 32 * 32 * 128 * 2 = 524,288`
bytes **per token**, so 4,096 tokens of context is ~2 GB for one sequence. Cache memory,
not weights, is what limits context length and batch size.

- **MQA**: one key/value head shared across all query heads. **GQA**: a small number of KV
  groups. Both cut cache memory by the group ratio, with a small quality cost.
- **Sliding window**: attend only to the last `w` tokens. Bounded cache; long-range
  information must come from summarization or retrieval.
- **PagedAttention**: manage the cache in fixed-size pages rather than one contiguous
  block, so fragmentation stops wasting memory and sequences can be batched densely.

## 10. Inference Optimization

- **Continuous batching**: add new sequences to a running batch as others finish, instead
  of waiting for the whole batch. This is the largest single throughput win in serving,
  because it keeps the GPU saturated at all times.
- **Speculative decoding**: a small draft model proposes `k` tokens; the target model
  verifies them in one forward pass. Accepted tokens are free, rejected ones cost a little
  extra. Exact same output distribution — not an approximation.
- **Quantization**: GPTQ (weight-only, second-order error compensation), AWQ (activation-
  aware, protects salient channels), GGUF (a portable format for local inference).
- **PagedAttention** and prefix caching for shared system prompts.
- The engineering summary: decode is memory-bandwidth-bound, not compute-bound. Every
  optimization that reduces memory traffic (quantization, GQA, paged cache, batching)
  matters more than one that increases FLOPs.

## Cross-Cutting Judgement

1. **Attention replaced recurrence because it removes the sequential dependency**, not
   because RNNs cannot model sequences.
2. **Pre-norm plus residual is what makes depth work.** Every transformer-scale model
   uses both; removing one hurts disproportionately.
3. **The `1/sqrt(d_k)` factor and the causal mask are the two lines that must be right.**
   Everything else is engineering.
4. **Inference optimization is memory work.** Decode is bandwidth-bound, so bandwidth
   reductions beat FLOP reductions.
