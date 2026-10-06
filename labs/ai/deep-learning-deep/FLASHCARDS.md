# deep-learning-deep — Flashcards

60 rows. Cover the answer, recall it, then check. Last column is the module.

| # | Question | Answer | Module |
|---|----------|--------|--------|
| 1 | Convolution output size? | `floor((n + 2p - k)/s) + 1` | 01 |
| 2 | Why convolution? | Parameter sharing: weights are independent of spatial position | 01 |
| 3 | Same vs valid padding? | `same` preserves `n`; `valid` shrinks by `k-1` | 01 |
| 4 | Receptive field for `L` 3x3 stride-1 layers? | `2L + 1` | 01 |
| 5 | What does dilation buy? | Wider receptive field at the same parameter count and resolution | 01 |
| 6 | Where does translation invariance come from? | Pooling or global average pooling; convolution gives only equivariance | 01 |
| 7 | Conv parameters for `k x k x C_in x C_out`? | `k^2 * C_in * C_out`, independent of image size | 01 |
| 8 | LeNet-5's contribution? | The conv-pool-FC template that every later CNN refines | 02 |
| 9 | ResNet's contribution? | Skip connections, making depth trainable beyond ~20 layers | 02 |
| 10 | VGG's lesson? | Depth from homogeneous 3x3 stacks beats wide kernels | 02 |
| 11 | Depthwise separable convolution? | Per-channel spatial filter then 1x1 mixing; `k^2*C + C*C'` parameters | 02 |
| 12 | EfficientNet's compound scaling? | Depth, width, and resolution scaled together by one coefficient | 02 |
| 13 | MobileNet's target? | Mobile FLOP budget via depthwise separable convolution | 02 |
| 14 | ConvNeXt's point? | Convolution blocks arranged like transformer blocks work equally well | 02 |
| 15 | Vanilla RNN state update? | `h_t = tanh(W_x x_t + W_h h_{t-1} + b)` | 03 |
| 16 | BPTT? | Backpropagation through the unrolled graph over all timesteps | 03 |
| 17 | LSTM's three gates? | Forget, input, output | 03 |
| 18 | LSTM cell recurrence? | `c_t = f_t .* c_{t-1} + i_t .* tanh(W_c [h_{t-1}, x_t] + b_c)` | 03 |
| 19 | Why LSTM helps gradients? | Additive path through time with a gate in `[0,1]`, no exponential product | 03 |
| 20 | GRU difference? | Merges input and forget gates, drops the cell state; ~25% fewer parameters | 03 |
| 21 | LSTM's limit? | It makes long-range dependencies learnable, not automatic | 03 |
| 22 | Seq2seq without attention? | Compresses the input into one fixed vector — a lossy bottleneck | 04 |
| 23 | Bahdanau attention? | Additive: `v' tanh(W [h_{i-1}, s_j])`, then softmax over `j` | 04 |
| 24 | Luong attention? | Multiplicative: `e_ij = s_i' W s_j` | 04 |
| 25 | Teacher forcing? | Train on ground-truth previous tokens; creates exposure bias at inference | 04 |
| 26 | Scheduled sampling? | Gradually replace ground truth with the model's own predictions to close the gap | 04 |
| 27 | Beam search length penalty? | Without one, beam search prefers short outputs; use `len^alpha`, `alpha ~ 0.6-1.0` | 04 |
| 28 | Scaled dot-product attention? | `softmax(Q K' / sqrt(d_k)) V` | 05 |
| 29 | Why `1/sqrt(d_k)`? | Dot product variance grows as `d_k`; scaling keeps the softmax off saturation | 05 |
| 30 | Causal mask? | Add `-inf` to positions `> i` before softmax | 05 |
| 31 | Transformer FFN shape? | `d -> 4d -> d`, applied per position; most parameters live here | 05 |
| 32 | Transformer block? | Pre-norm attention, residual, pre-norm FFN, residual | 05 |
| 33 | Self vs cross attention? | `Q=K=V` from one sequence versus `Q` from decoder, `K,V` from encoder | 06 |
| 34 | RoPE? | Rotates `Q` and `K` by position so scores encode relative distance | 06 |
| 35 | ALiBi? | Adds `-m * (i - j)` per head; parameter-free, extrapolates well | 06 |
| 36 | FlashAttention? | Tiled IO-aware exact attention with online softmax; no `n x n` materialization | 06 |
| 37 | MQA vs GQA? | One shared KV head versus a small number of KV groups | 06 |
| 38 | Sinusoidal PE formula? | `sin/cos(pos / 10000^(2i/d))` at geometrically spaced frequencies | 07 |
| 39 | Sinusoidal's key property? | Relative offsets are linear combinations, so it extrapolates beyond trained length | 07 |
| 40 | Learned absolute PE limit? | A lookup table; no extrapolation past the trained length | 07 |
| 41 | Relative position bias? | A learned bias indexed by `i - j`, added before the softmax | 07 |
| 42 | NoPE? | No positional signal at all; position is still implicitly available through the causal mask | 07 |
| 43 | LayerNorm in transformers? | Over hidden dims per position; independent of batch composition | 08 |
| 44 | RMSNorm? | LayerNorm without mean subtraction; one pass, same quality | 08 |
| 45 | Pre-norm vs post-norm? | Pre-norm keeps the residual path clean and trains at depth without warmup | 08 |
| 46 | Sandwich norm? | Normalize before and after each sublayer | 08 |
| 47 | Gradient checkpointing? | Recompute activations during backward to trade compute for memory | 08 |
| 48 | KV cache purpose? | Cache K and V so each decode step is `O(n)` instead of `O(n^2)` | 09 |
| 49 | KV cache bytes per token? | `2 * layers * heads * head_dim * bytes_per_element` | 09 |
| 50 | Sliding-window attention? | Attend only the last `w` tokens; bounded cache, long-range info lost | 09 |
| 51 | PagedAttention? | Fixed-size pages plus a free list and copy-on-write, eliminating fragmentation | 09 |
| 52 | Prefix caching? | Reuse the KV of a shared system prompt across requests | 09 |
| 53 | Continuous batching? | Admit new sequences as others finish, keeping the device saturated | 10 |
| 54 | Speculative decoding? | Draft `k` tokens cheaply, verify in one target pass; exact same distribution | 10 |
| 55 | GPTQ vs AWQ? | GPTQ is weight-only with second-order error compensation; AWQ is activation-aware | 10 |
| 56 | Why decode is bandwidth-bound? | Each step reads every weight but does little arithmetic; intensity is about 1 | 10 |
| 57 | Bandwidth vs FLOPs? | In decode, reducing bytes moved matters more than reducing FLOPs | 10 |
| 58 | Weight tying? | Share embedding and output projection weights; saves parameters, helps small models | 10 |
| 59 | Label smoothing effect on LLMs? | Softer targets; worse NLL, usually better generalization | 10 |
| 60 | Weight sharing? | Reuse filters across positions or timesteps to cut parameters | 10 |
