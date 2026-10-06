# Lab 01: Transformer Architecture Deep DIVE — Theory

## 1. Why Transformers?

Before 2017, sequence modeling was dominated by RNNs and LSTMs. They process tokens
one at a time, which makes them slow to train and prone to vanishing gradients over
long sequences. The Transformer (Vaswani et al., 2017) replaced recurrence entirely
with **attention**, enabling massive parallelization during training and much better
modeling of long-range dependencies.

## 2. High-Level Architecture

The original Transformer is an **encoder-decoder** model:

```
Input tokens ──► [Encoder × N] ──► memory ──► [Decoder × N] ──► Output tokens
```

- **Encoder**: builds a rich contextual representation of the input.
- **Decoder**: generates the output autoregressively, attending to its own past
  tokens (causally masked) and to the encoder memory (cross-attention).

Modern LLMs (GPT family) keep only the decoder; encoder-only models (BERT) keep
only the encoder.

## 3. Scaled Dot-Product Attention

The core operation. Given queries Q, keys K, values V:

```
Attention(Q, K, V) = softmax( Q·Kᵀ / √d_k ) · V
```

- **Q·Kᵀ** measures how much each query "matches" each key (raw affinity scores).
- **√d_k** scaling prevents dot products from growing large in magnitude (which
  would push softmax into regions with tiny gradients).
- **softmax** converts scores into a probability distribution over values.
- The weighted sum of V produces the output.

Intuition: each output token is a weighted blend of all input tokens, where the
weights are learned based on content similarity.

## 4. Multi-Head Attention

Instead of one attention operation, run `h` attention operations in parallel,
each with its own learned projection matrices W_q, W_k, W_v:

```
head_i = Attention(Q·W_q_i, K·W_k_i, V·W_v_i)
MultiHead(Q,K,V) = Concat(head_1, …, head_h) · W_o
```

Different heads can learn different relationships (syntax, position, semantics).
Typical configurations: d_model=512 with h=8 heads → d_k=64 per head.

## 5. Positional Encoding

Attention is permutation-invariant — it has no notion of order. Positional
encodings inject sequence position information:

```
PE(pos, 2i)   = sin( pos / 10000^(2i/d_model) )
PE(pos, 2i+1) = cos( pos / 10000^(2i/d_model) )
```

- Even dimensions use sine, odd dimensions use cosine.
- The geometric progression of wavelengths lets the model learn relative
  positions via linear transformations.
- Alternatives learned absolute embeddings (BERT), relative positions,
  and RoPE (modern LLMs — see Lab 13).

## 6. Feed-Forward Network (FFN)

Each sub-layer is followed by a position-wise FFN:

```
FFN(x) = max(0, x·W_1 + b_1)·W_2 + b_2
```

- Expands to a larger inner dimension (typically 4× d_model) then projects back.
- Applied independently to each position.
- Contains most of the model's parameters and "knowledge".

## 7. Residual Connections & Layer Normalization

Each sub-layer is wrapped with a residual connection and layer norm:

```
output = LayerNorm( x + Sublayer(x) )
```

- **Residual connections** let gradients flow directly through the network,
  enabling training of very deep models.
- **Layer normalization** stabilizes activations (zero mean, unit variance
  across the feature dimension).
- Pre-norm vs post-norm: modern LLMs (GPT-3+) use pre-norm for stability.

## 8. Encoder Layer

```
x ──► Multi-Head Self-Attention ──► Add & Norm ──► FFN ──► Add & Norm ──► out
```

- Self-attention: Q, K, V all come from the same input (bidirectional context).
- Two sub-layers per encoder block.

## 9. Decoder Layer

```
x ──► Masked Self-Attention ──► Add & Norm
  ──► Cross-Attention (Q from decoder, K/V from encoder) ──► Add & Norm
  ──► FFN ──► Add & Norm ──► out
```

- **Masked self-attention**: causal mask prevents attending to future tokens.
- **Cross-attention**: connects decoder to encoder memory.
- Three sub-layers per decoder block.

## 10. Causal Masking

A lower-triangular mask of `-∞` is added to attention scores before softmax:

```
scores = [[ 0, -inf, -inf],
          [ s,   0, -inf],
          [ s,   s,   0 ]]
```

After softmax, future positions get zero weight. This is what makes autoregressive
generation possible.

## 11. Training Objective

- **Encoder-decoder models**: cross-entropy between predicted and target tokens.
- **Decoder-only models**: next-token prediction (causal language modeling).
- Teacher forcing: feed the ground-truth prefix during training.

## 12. Complexity Analysis

| Operation | Time | Space |
|-----------|------|-------|
| Self-attention | O(n²·d) | O(n²) |
| FFN | O(n·d²) | O(n·d) |

The n² term in attention is the bottleneck for long sequences — motivating
sparse attention, sliding windows, and other efficient variants (Lab 13).

## 13. Key Takeaways

1. Attention replaces recurrence → parallel training, long-range dependencies.
2. Multi-head attention captures diverse relationships.
3. Positional encodings restore order information.
4. Residuals + layer norm enable deep stacking.
5. Causal masking enables autoregressive generation.
6. The n² attention cost is the central scaling challenge.
