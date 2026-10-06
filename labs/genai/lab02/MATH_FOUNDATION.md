# Lab 02: GPT Architecture — Math Foundation

## 1. Attention with a Causal Mask

For query row i and key column j:

```
S_ij = (Q K^T)_ij / sqrt(d_k) + M_ij
M_ij = 0            if j <= i
M_ij = -infinity    if j > i
Attention(Q,K,V)_i = softmax_row(S_i) · V
```

Because `exp(-inf) = 0`, masked columns contribute exactly nothing. Do **not**
compute `weights * mask` after softmax: `0 * (-inf)` yields NaN.

## 2. Softmax Stability

```
softmax(z)_i = exp(z_i - z_max) / sum_j exp(z_j - z_max)
```

`z -> z - z_max*1` leaves the result unchanged because the factor `exp(-z_max)`
cancels between numerator and denominator, while every exponential argument is
now <= 0 so `exp` cannot overflow.

## 3. Language Model Loss

```
L(theta) = - (1/T) * sum_{t=1..T} log P_theta(x_t | x_<t)
P_theta(x_t | x_<t) = softmax(W_lm · h_t + b)[x_t]
```

With padding mask `m_t in {0,1}`:

```
L = -sum_t m_t log P(x_t | x_<t) / sum_t m_t
```

## 4. Cross-Entropy as Dot Product of Logits

```
-log p_y = -z_y + log sum_k exp(z_k)
```

This identity is why implementations shift by `z_max` and why the loss never needs
the full probability vector. It is also numerically awkward in `float` — use
`double` or the log-sum-exp trick.

## 5. Temperature Scaling

```
p_i(T) = exp(z_i / T) / sum_k exp(z_k / T)
```

Derivative of log-prob wrt temperature: `d/dT log p_i = -(z_i - E[z]) / T^2`.
So T < 1 amplifies the gap to the argmax; T -> 0 gives argmax.

## 6. Top-p Selection

Sort probabilities `p_(1) >= ... >= p_(V)`. Let `m = min{k : sum_{j<=k} p_(j) >= p}`.
Keep the first `m` logits, set the rest to `-inf`, renormalize.

Expected mass loss from truncation is bounded by `(1 - p)` in the worst case and
typically far less; empirically `p` in `[0.9, 0.98]` is a common operating band.

## 7. Perplexity

```
PPL = exp(L) = exp( -(1/T) sum_t log P(x_t | x_<t) )
```

Property: `PPL = exp(NLL per token)`. Only comparable across runs that share the
tokenizer, since tokenization changes `T`.

## 8. KV Cache Memory

```
bytes = batch * 2 (K and V) * layers * n_kv_heads * head_dim * seq_len * sizeof(elem)
```

Example: batch 8, 32 layers, 8 KV heads, 128 dim, 4096 tokens, fp16 (2 bytes):

```
8 * 2 * 32 * 8 * 128 * 4096 * 2 = 17.18 GB
```

GQA with 8 KV heads instead of 32 query heads gives a 4x reduction.

## 9. Per-Token Decode Cost Model

Decode reads every weight once and the whole KV cache each step:

```
cost_per_token ~ W_bytes / mem_bandwidth + cache_bytes / mem_bandwidth
```

which is why decode is memory-bandwidth bound and why batching (which amortizes
`W_bytes` across requests) is the single biggest throughput lever.

## 10. Prefill Cost Model

Prefill is compute bound:

```
FLOPs ~ 2 * params * tokens    (plus 2 * seq^2 * d_model * layers for attention)
```

So prefill latency is roughly linear in prompt length.

## 11. Scaling Law

Chinchilla-style form:

```
L(N, D) = E^(1/alpha) * N^(-alpha/beta) * D^(-1/beta) + E
```

Approximate exponents: `alpha ≈ 0.76`, `beta ≈ 1.0` in one parameterization; the
practical content is: for fixed `E = 6ND`, optimal `N ∝ E^0.5` and `D ∝ E^0.5`,
i.e. parameters and tokens should grow together.

## 12. Layer Parameter Counts (per layer, d = d_model, f = expansion)

```
Attention:  W_q, W_k, W_v, W_o      -> 4 d^2      (MHA)
            + W_q, W_kv, W_o (GQA) -> 2 d^2 + 2 d^2 * (g / h)
FFN (GELU): 2 f d                    with f = 4d  -> 8 d^2
FFN (SwiGLU): 3 * (8/3 d) * d         -> 8 d^2
Embeddings:  V d                       (tied to W_lm when weight tying is on)
```

At `d >= 1024` the FFN is roughly half of all non-embedding parameters, which is
why MLP-focused pruning and quantization pay off.

## 13. GQA/MQA Cache Ratio

```
MHA: n_kv_heads = n_q_heads        cache ratio 1.0
GQA with group g: n_kv = h / g     cache ratio 1/g
MQA: n_kv = 1                      cache ratio 1/h
```

## 14. Speculative Decoding Acceptance

Draft proposes `z_1..z_k`. Target verifies with one forward pass; token `z_i` is
accepted with probability

```
min(1, p_target(z_i) / p_draft(z_i))
```

so expected accepted tokens per pass is `1 + sum_{i} p_ratio_i`; speedup is
bounded by how well the draft matches the target.

## Worked Numbers

Prompt 500 tokens, generate 200, 32 layers, d_model 4096, 32 heads x 128 dim, fp16.

- KV cache per sequence: `2 * 32 * 4096 * 700 * 2 bytes = 367 MB`.
- At batch 16: `5.9 GB` just for cache — this is why GQA and cache eviction are
  production requirements, not optimizations.

## Self-Check Questions

1. Why does `0 * -inf` produce NaN, and which order avoids it?
2. Derive the KV cache byte count for the numbers above.
3. If logits are `[2.0, 2.0, 2.0]` what is top-p=0.95 behavior?
4. Show that `d/dT log p_i` has the sign you predicted.