# Lab 02: GPT Architecture — Theory

## 1. From Transformer to GPT

Lab 01 built the full encoder-decoder Transformer. GPT keeps only the **decoder**
stack and drops the encoder entirely. That single decision defines the modern LLM:
- Unidirectional (causal) context — every token attends only to its left.
- One unified objective: **next-token prediction**.
- Scale behaviour: more layers, more heads, more data (the "scaling laws" story).

## 2. Causal Masking

Self-attention is symmetric; GPT needs it asymmetric. Before the softmax, set
future positions to negative infinity:

```
scores[i][j] = Q[i]·K[j]/sqrt(d_k) + M[i][j],  M[i][j] = 0 if j<=i else -inf
```

Then row-softmax ignores masked entries exactly (exp(-inf) = 0). In Java use
`Double.NEGATIVE_INFINITY` and add the mask, never multiply by zero (0 * inf = NaN).

## 3. The Language Modelling Objective

For a token sequence x1..xT, the model maximizes:

```
L = -sum_{t=1..T} log P(x_t | x_1 ... x_{t-1})
P(x_t | x_<t) = softmax(h_t) · E[x_t]
```

With teacher forcing the whole loss is computed in a single forward pass: inputs
are `x[0..T-1]`, targets are `x[1..T]`. Padding positions are masked out of the
mean so that variable-length batches stay comparable.

## 4. Decoder Block Anatomy

Per layer (pre-norm modern variant):
1. RMSNorm / LayerNorm
2. Causal self-attention (GQA in larger models)
3. Residual add
4. RMSNorm / LayerNorm
5. MLP: `up(gate) * down` (SwiGLU) or `w2 * act(w1 x + b1)`
6. Residual add

Position-wise FFN expands `d_model -> 4*d_model` (GPT-2) or
`-> 8*d_model/3` gated (LLaMA-style) — the parameter budget is dominated here,
not by attention, for models at/above ~1B params.

## 5. Tokenization (BPE)

Byte-Pair Encoding is a greedy bottom-up merge procedure:
1. Start from the 256 byte tokens (never out-of-vocabulary).
2. Repeatedly merge the most frequent adjacent symbol pair.
3. Stop at `vocabSize`.

Properties that matter operationally:
- Vocabulary size trades embedding params vs sequence length (short vocab =
  more embedding memory + slower prefill).
- Leading-space handling ("Ġ") changes token boundaries materially.
- Java implementation: keep the merges list, apply greedily per priority level.

## 6. Autoregressive Generation

Sampling loop per step t:
1. forward(x[0..t-1]) -> logits
2. apply temperature / top-k / top-p filtering
3. sample token
4. append, repeat until EOS or max tokens

The **KV cache** stores K and V for positions 0..t-1 so step t only computes the
new token's queries — O(n) instead of O(n²) per sequence. Cost: 2 * layers *
n_kv_heads * head_dim * batch * bytes. This is why batch size is the first thing
serving engineers tune down.

## 7. Temperature, Top-K, Top-P

- Temperature: `logits / T`. T→0 greedy, T→1 sampling, T>1 flattens.
- Top-k: keep k highest-probability tokens.
- Top-p (nucleus): keep smallest set whose cumulative mass ≥ p. Adaptive to the
  entropy of each position; usually better than top-k.

## 8. Pretraining vs Instruction Tuning

Base models are next-token predictors. Instruction-tuned models are fine-tuned on
(demonstration, response) pairs so the model answers instructions instead of
continuing text. Chat/instruct checkpoints add a chat template and a special
`<|im_end|>`-style stop token — the template is part of the model contract.

## 9. Scaling Laws

Loss follows a power law in parameters, data, and compute:

```
L(N, D) = (E / (N^alpha_alpha / D^beta))^1/alpha
```

Roughly `alpha ≈ 0.076` (data exponent on N) and `beta ≈ 0.095` in Chinchilla
terms. Practical takeaway: for a fixed compute budget, models are now
over-parameterized relative to data — so retrieval, synthetic data and
fine-tuning matter more than adding parameters.

## 10. Java Implementation Notes

- Use `double[][]` for logits, `float[][]`-style arrays (or int8 with per-row
  scales) for the cache — document which.
- Softmax must subtract the row max for numerical stability.
- Guard the cache with a ring buffer when `maxContext` is finite.
- Deterministic sampling: seed `java.util.Random` and log the seed with results.

## Key Equations

```
Attention(Q,K,V) = softmax(QK^T/sqrt(d_k) + M) V
h_t = TransformerBlock(x_t with causal mask)
P(x_t | x_<t) = softmax(h_t W_vocab) · E[x_t]
Loss = -mean_t log P(x_t | x_<t)
```

## Common Pitfalls

1. Forgetting the causal mask during training (labels leak).
2. Not offsetting inputs vs targets by one position.
3. Recomputing the whole prefix each step (no KV cache) — 100x slower.
4. Dividing the sum of per-token losses by `T` on padded data.
5. `logits / T` overflow when T is very small and logits are large.