# 15-transformers — Flashcards

## Core Attention

| Concept | Formula / Key Point |
|---------|---------------------|
| **Scaled Dot-Product Attention** | $\text{Attention}(Q,K,V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}})V$ |
| **Why $\sqrt{d_k}$?** | $\text{Var}(q^T k) = d_k$ if $q,k \sim \mathcal{N}(0,1)$. Scaling keeps variance $\approx 1$, prevents softmax saturation. |
| **Multi-Head Attention** | Split $Q,K,V$ into $h$ heads, compute attention in parallel, concat, project: $\text{Concat}(\text{head}_i)W^O$ |
| **Head Dimensions** | $d_k = d_v = d_{model}/h$. Total params same as single head with full dimension. |

---

## Positional Encoding

| Type | Formula / Description | Pros | Cons |
|------|----------------------|------|------|
| **Sinusoidal** | $PE_{pos,2i}=\sin(pos/10000^{2i/d})$, $PE_{pos,2i+1}=\cos(\dots)$ | Extrapolates to longer seq, no params | Fixed, may not be optimal |
| **Learnable** | $PE \in \mathbb{R}^{L_{max} \times d_{model}}$ learned | Flexible, often better performance | Fixed max length, no extrapolation |
| **RoPE (Rotary)** | Rotate $q,k$ by $e^{i m \theta_{pos}}$ in complex plane | Encodes relative position naturally, extrapolates | Slightly more complex |

**Key Property**: Sinusoidal $PE_{pos+k}$ = linear function of $PE_{pos}$ → enables relative attention.

---

## Transformer Block Architecture

### Encoder Block (Pre-LN — Modern Standard)
```
x → LayerNorm → MHA → Dropout → + → x
                    ↓
                LayerNorm → FFN → Dropout → +
```

### Decoder Block
```
x → LayerNorm → Masked MHA → Dropout → + → x
                    ↓
                LayerNorm → Cross-Attn → Dropout → +
                    ↓
                LayerNorm → FFN → Dropout → +
```

### Residual Connection Variants
| Variant | Order | Stability |
|---------|-------|-----------|
| **Post-LN** (Original) | $x \to \text{SubLayer} \to + \to \text{LN}$ | Harder to train deep |
| **Pre-LN** (Modern) | $x \to \text{LN} \to \text{SubLayer} \to +$ | Stable, larger LR, no warmup needed |
| **DeepNorm** | Scaled residual: $\alpha x + F(\text{LN}(x))$, $\alpha=2L^{1/4}$ | Very deep (100+) |

---

## Feed-Forward Network (FFN)

| Variant | Formula | Used In |
|---------|---------|---------|
| **Standard** | $\text{ReLU}(xW_1+b_1)W_2+b_2$ | Original Transformer, BERT |
| **GELU** | $\text{GELU}(xW_1)W_2$ | GPT-2, BERT-large |
| **SwiGLU** | $(\text{Swish}(xW_1) \odot xW_3)W_2$ | LLaMA, PaLM, Mistral |
| **GeGLU** | $(\text{GELU}(xW_1) \odot xW_3)W_2$ | Some modern LLMs |

**Typical**: $d_{ff} = 4 \times d_{model}$ (standard), $d_{ff} = 8/3 \times d_{model}$ (SwiGLU for same params).

---

## Normalization

| Aspect | LayerNorm | BatchNorm |
|--------|-----------|-----------|
| **Norm Dimension** | Feature (last dim) | Batch (first dim) |
| **Sequence Length** | Any | Fixed |
| **Train/Inference** | Same | Different (running stats) |
| **RNN/Transformer** | ✅ Preferred | ❌ Rarely used |

**Formula**: $y = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} \odot \gamma + \beta$

---

## Attention Masking

| Mask Type | Matrix $M_{ij}$ | Purpose |
|-----------|-----------------|---------|
| **Causal (Decoder)** | $0$ if $i \ge j$, $-\infty$ if $i < j$ | No future peeking |
| **Padding** | $0$ for real tokens, $-\infty$ for padding | Ignore padding |
| **Combined** | $M_{causal} + M_{padding}$ | Both |

**Application**: $\text{softmax}(\frac{QK^T + M}{\sqrt{d_k}})V$

---

## Cross-Attention (Encoder-Decoder)

| Component | Source |
|-----------|--------|
| **Q (Query)** | Decoder (current target position) |
| **K, V (Key, Value)** | Encoder output (full source sequence) |

Enables decoder to "look at" relevant encoder positions for each generated token.

---

## Complexity & Optimizations

| Method | Time | Memory | Notes |
|--------|------|--------|-------|
| **Standard** | $O(n^2 d)$ | $O(n^2)$ | Quadratic bottleneck |
| **Sparse (Longformer)** | $O(n \sqrt{n})$ or $O(n)$ | $O(n \sqrt{n})$ | Local + global attention |
| **Linear Attention** | $O(n d^2)$ | $O(n d)$ | Kernel approximation |
| **Flash Attention** | $O(n^2 d)$ | $O(n d)$ | **Exact**, IO-aware, 2-4x speedup |
| **Sliding Window** | $O(n w d)$ | $O(n w)$ | Window size $w \ll n$ |
| **KV Cache** | $O(n d)$ per step | $O(n d)$ | Autoregressive generation |

---

## Initialization Best Practices

| Component | Initialization |
|-----------|----------------|
| **Most weights** | Xavier/Glorot uniform |
| **Output projections** ($W^O$, FFN $W_2$) | **Zero** (near-identity residual at init) |
| **Attention output** | Small ($\sim 0.02$) |
| **Deep transformers** ($L > 24$) | Scale by $1/\sqrt{L}$ or use DeepNorm |

---

## Training Recipes

| Component | Standard Practice |
|-----------|-------------------|
| **Optimizer** | AdamW ($\beta_1=0.9, \beta_2=0.95\text{ or }0.999$) |
| **LR Schedule** | Warmup (1-5% steps) → Cosine decay |
| **Peak LR** | $10^{-4}$ to $10^{-3}$ (small models), $10^{-5}$ to $10^{-4}$ (LLMs) |
| **Weight Decay** | 0.01-0.1 (decoupled, no decay on bias/LN/pos) |
| **Gradient Clipping** | 1.0 (global norm) |
| **Batch Size** | Large (1024-4M tokens) |
| **Mixed Precision** | BF16/FP16 compute, FP32 master weights |

---

## Modern Architecture Variants

| Variant | Key Changes | Examples |
|---------|-------------|----------|
| **GPT (Decoder-only)** | Causal masking, no cross-attn | GPT-1/2/3/4 |
| **BERT (Encoder-only)** | Bidirectional, MLM pretraining | BERT, RoBERTa |
| **T5 (Encoder-Decoder)** | Standard architecture, span corruption | T5, FLAN-T5 |
| **LLaMA** | Pre-LN, SwiGLU, RoPE, RMSNorm | LLaMA 1/2/3 |
| **Mistral** | Sliding window attention, grouped-query | Mistral 7B, Mixtral |

---

## Interview Quick Reference

**Q**: "Why does attention scale with $\sqrt{d_k}$?"
**A**: Dot product variance grows with $d_k$. Without scaling, softmax saturates, gradients vanish.

**Q**: "What's the difference between Pre-LN and Post-LN?"
**A**: Pre-LN applies LayerNorm before sublayer: $x + F(\text{LN}(x))$. Gradient flows through identity. Post-LN: $\text{LN}(x + F(x))$. Pre-LN more stable for deep nets.

**Q**: "How does RoPE work?"
**A**: Rotates query/key vectors by position-dependent angles in complex plane. $q_m' = q_m e^{i m \theta_{pos}}$. Dot product $q^T k$ becomes function of relative position.

**Q**: "What is Flash Attention?"
**A**: Exact attention algorithm that fuses softmax + matmul in SRAM, avoiding $O(n^2)$ HBM reads/writes of $QK^T$ matrix. 2-4x faster, less memory.

**Q**: "Why SwiGLU over ReLU FFN?"
**A**: Gating mechanism $(Swish(xW_1) \odot xW_3)W_2$ allows dynamic feature selection. Better performance per parameter.

**Q**: "How does KV cache work?"
**A**: In autoregressive generation, cache $K,V$ for all previous tokens. Each new step only computes $Q$ for new token, attends to cached $K,V$. Reduces $O(n^2)$ to $O(n)$ per step.

**Q**: "What's the difference between encoder and decoder attention?"
**A**: Encoder: full self-attention (bidirectional). Decoder: causal self-attention + cross-attention to encoder.

**Q**: "Why zero-initialize output projections?"
**A**: Makes residual branch output near-zero at init, so $x + F(x) \approx x$. Easier optimization, especially deep networks.