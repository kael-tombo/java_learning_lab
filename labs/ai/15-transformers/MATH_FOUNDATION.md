# 15-transformers — Math Foundation

## 1. Scaled Dot-Product Attention

### Core Formula
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

Where:
- $Q \in \mathbb{R}^{n_q \times d_k}$: Query matrix
- $K \in \mathbb{R}^{n_k \times d_k}$: Key matrix  
- $V \in \mathbb{R}^{n_k \times d_v}$: Value matrix
- $d_k$: Key dimension (typically $d_{model}/h$)
- $\sqrt{d_k}$: Scaling factor

### Why Scaling?
Without scaling, for large $d_k$, the dot products $QK^T$ grow large in magnitude, pushing softmax into saturation (gradients $\to 0$).
$$\text{Var}(q_i^T k_j) = d_k \cdot \text{Var}(q) \cdot \text{Var}(k)$$
If $q, k \sim \mathcal{N}(0, 1)$, then $\text{Var}(q^T k) = d_k$. Scaling by $\frac{1}{\sqrt{d_k}}$ keeps variance $\approx 1$.

---

## 2. Multi-Head Attention

### Parallel Attention Heads
Split $Q, K, V$ into $h$ heads:
$$Q_i = Q W_i^Q, \quad K_i = K W_i^K, \quad V_i = V W_i^V$$
where $W_i^Q \in \mathbb{R}^{d_{model} \times d_k}$, $W_i^K \in \mathbb{R}^{d_{model} \times d_k}$, $W_i^V \in \mathbb{R}^{d_{model} \times d_v}$

Typically $d_k = d_v = d_{model}/h$.

### Head Computation
$$\text{head}_i = \text{Attention}(Q_i, K_i, V_i)$$

### Concatenation & Output Projection
$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, ..., \text{head}_h) W^O$$
where $W^O \in \mathbb{R}^{h d_v \times d_{model}}$

---

## 3. Positional Encoding

### Sinusoidal Positional Encoding (Original Transformer)
$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$
$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

**Properties**:
- Deterministic, no learnable parameters
- Allows extrapolation to longer sequences
- $PE_{pos+k}$ can be expressed as linear function of $PE_{pos}$ (enables relative attention)

### Learnable Positional Embeddings
$$PE \in \mathbb{R}^{L_{max} \times d_{model}}$$
Learned jointly with model. Used in BERT, GPT.

### Rotary Positional Embeddings (RoPE)
Rotate query/key vectors by position-dependent angles:
$$q_m' = q_m e^{i m \theta_{pos}}, \quad k_m' = k_m e^{i m \theta_{pos}}$$
where $\theta_{pos} = pos \cdot \theta_m$, $\theta_m = 10000^{-2m/d}$

Enables relative position encoding naturally in attention.

---

## 4. Transformer Block Architecture

### Encoder Block
```
Input (x)
  ↓
LayerNorm
  ↓
Multi-Head Self-Attention
  ↓
Dropout + Residual: x + Attention(LayerNorm(x))
  ↓
LayerNorm
  ↓
Feed-Forward Network (FFN)
  ↓
Dropout + Residual: x + FFN(LayerNorm(x))
  ↓
Output
```

### Decoder Block
```
Input (x)
  ↓
LayerNorm
  ↓
Masked Multi-Head Self-Attention (causal)
  ↓
Dropout + Residual
  ↓
LayerNorm
  ↓
Cross-Attention (Q from decoder, K,V from encoder)
  ↓
Dropout + Residual
  ↓
LayerNorm
  ↓
FFN
  ↓
Dropout + Residual
  ↓
Output
```

---

## 5. Feed-Forward Network (FFN)

### Standard (Original Transformer)
$$\text{FFN}(x) = \text{ReLU}(x W_1 + b_1) W_2 + b_2$$
- $W_1 \in \mathbb{R}^{d_{model} \times d_{ff}}$, $W_2 \in \mathbb{R}^{d_{ff} \times d_{model}}$
- Typically $d_{ff} = 4 \times d_{model}$

### Gated Variants (Modern LLMs)
**SwiGLU** (used in LLaMA, PaLM):
$$\text{SwiGLU}(x) = (\text{Swish}(x W_1) \odot x W_3) W_2$$
$$\text{Swish}(x) = x \cdot \sigma(x)$$

**GeGLU**:
$$\text{GeGLU}(x) = (\text{GELU}(x W_1) \odot x W_3) W_2$$

---

## 6. Layer Normalization

### Formula
$$\text{LayerNorm}(x) = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} \odot \gamma + \beta$$
- $\mu = \frac{1}{d}\sum_i x_i$, $\sigma^2 = \frac{1}{d}\sum_i (x_i - \mu)^2$
- $\gamma, \beta \in \mathbb{R}^d$: Learnable scale and shift
- Normalized over feature dimension (not batch)

### Difference from BatchNorm
| Aspect | LayerNorm | BatchNorm |
|--------|-----------|-----------|
| Normalization dim | Feature (last) | Batch (first) |
| Sequence length | Works for any | Fixed |
| Training/inference | Same | Different stats |
| RNN/Transformer | Preferred | Rarely used |

---

## 7. Residual Connections & Gradient Flow

### Residual Block
$$y = x + F(\text{LayerNorm}(x))$$
or (Post-LN): $y = \text{LayerNorm}(x + F(x))$

### Gradient Flow Analysis
$$\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} \left(I + \frac{\partial F}{\partial x}\right)$$

If $F$ is small (near initialization), $\frac{\partial L}{\partial x} \approx \frac{\partial L}{\partial y}$ — **gradient highway**.

### Pre-LN vs Post-LN
- **Pre-LN** (Modern): $\text{LayerNorm} \to \text{Attention/FFN} \to \text{Residual}$ — Stable, allows larger LR
- **Post-LN** (Original): $\text{Attention/FFN} \to \text{Residual} \to \text{LayerNorm}$ — Original paper, harder to train deep

---

## 8. Causal Masking (Decoder Self-Attention)

### Mask Matrix
$$M_{ij} = \begin{cases} 0 & \text{if } i \ge j \\ -\infty & \text{if } i < j \end{cases}$$

### Application
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T + M}{\sqrt{d_k}}\right)V$$

Ensures position $i$ only attends to positions $\le i$ (no future peeking).

---

## 9. Cross-Attention (Encoder-Decoder)

### Setup
- $Q$ from decoder (current target position)
- $K, V$ from encoder output (full source sequence)
$$\text{CrossAttn}(Q_{dec}, K_{enc}, V_{enc})$$

### Purpose
Allows each decoder position to attend to all encoder positions — the "alignment" mechanism.

---

## 10. Attention Complexity & Optimizations

### Complexity
| Operation | Time | Memory |
|-----------|------|--------|
| $QK^T$ | $O(n^2 d)$ | $O(n^2)$ |
| Softmax | $O(n^2)$ | $O(n^2)$ |
| $AV$ | $O(n^2 d)$ | $O(n d)$ |

**Quadratic in sequence length $n$** — bottleneck for long sequences.

### Optimizations
| Method | Idea | Complexity |
|--------|------|------------|
| **Sparse Attention** | Local + global tokens (Longformer, BigBird) | $O(n \sqrt{n})$ or $O(n)$ |
| **Linear Attention** | Kernel trick: $\text{softmax}(QK^T)V \approx \phi(Q)(\phi(K)^T V)$ | $O(n d^2)$ |
| **Flash Attention** | IO-aware, fuses softmax + matmul, no materialized $QK^T$ | $O(n^2 d)$ but 2-4x faster |
| **Sliding Window** | Only attend to local window | $O(n w d)$ |
| **KV Cache** | Cache K,V for autoregressive generation | $O(n d)$ per step |

---

## 11. Initialization

### Transformer-Specific
- **Xavier/Glorot** for most weights
- **Zero initialization** for output projection $W^O$ and FFN second layer — makes residual branch near-identity at init
- **Small initialization** for attention output ($\sim 0.02$)

### Depth Scaling
For deep transformers ($L > 24$), scale initialization by $1/\sqrt{L}$ or use **DeepNorm**:
$$\text{DeepNorm: } \alpha = 2L^{1/4}, \quad \text{Residual weight} = \alpha$$

---

## 12. Training Dynamics

### Learning Rate Schedule
- **Warmup**: Linear increase from 0 to peak over first 1-5% steps
- **Cosine decay**: Gradual decrease to minimum
- **Constant with warmup**: Popular for LLMs

### Gradient Clipping
Clip gradient norm at 1.0 (standard for transformers).

### Weight Decay
- **AdamW**: Decoupled weight decay (0.01-0.1)
- Apply to all params except biases, LayerNorm scales/shifts, positional embeddings

---

## 13. Key Formulas Reference

| Component | Formula |
|-----------|---------|
| Scaled Dot-Product Attention | $\text{softmax}(\frac{QK^T}{\sqrt{d_k}})V$ |
| Multi-Head Attention | $\text{Concat}(\text{head}_i)W^O$ |
| Sinusoidal PE | $\sin(pos/10000^{2i/d}), \cos(pos/10000^{2i/d})$ |
| RoPE | $q_m' = q_m e^{i m \theta_{pos}}$ |
| LayerNorm | $\frac{x-\mu}{\sqrt{\sigma^2+\epsilon}}\odot\gamma+\beta$ |
| FFN (Standard) | $\text{ReLU}(xW_1+b_1)W_2+b_2$ |
| SwiGLU | $(\text{Swish}(xW_1)\odot xW_3)W_2$ |
| Residual (Pre-LN) | $x + F(\text{LN}(x))$ |
| Causal Mask | $M_{ij} = 0$ if $i\ge j$, else $-\infty$ |
| Cross-Attention | $\text{Attn}(Q_{dec}, K_{enc}, V_{enc})$ |

---

## 14. Java Implementation Reference

```java
// Scaled Dot-Product Attention
public class Attention {
    public static double[][] attention(double[][] Q, double[][] K, double[][] V, double[][] mask) {
        int n = Q.length;
        int dk = Q[0].length;
        
        // 1. QK^T / sqrt(dk)
        double[][] scores = matmul(Q, transpose(K));
        scaleInPlace(scores, 1.0 / Math.sqrt(dk));
        
        // 2. Add mask (if provided)
        if (mask != null) addInPlace(scores, mask);
        
        // 3. Softmax
        double[][] attn = softmaxRows(scores);
        
        // 4. AV
        return matmul(attn, V);
    }
}

// Multi-Head Attention
public class MultiHeadAttention {
    private LinearLayer Wq, Wk, Wv, Wo;
    private int numHeads;
    private int dModel, dHead;
    
    public double[][] forward(double[][] x, double[][] mask) {
        // Project
        double[][] Q = Wq.forward(x);
        double[][] K = Wk.forward(x);
        double[][] V = Wv.forward(x);
        
        // Split heads: (n, d_model) -> (h, n, d_head)
        // Process each head
        // Concat and project
        return Wo.forward(concat(heads));
    }
}
```

---

## 15. Further Reading

1. **Vaswani et al.** - "Attention Is All You Need" (NeurIPS 2017)
2. **Devlin et al.** - "BERT: Pre-training of Deep Bidirectional Transformers" (NAACL 2019)
3. **Radford et al.** - "Language Models are Unsupervised Multitask Learners" (GPT-2, 2019)
4. **Su et al.** - "RoFormer: Enhanced Transformer with Rotary Position Embedding" (2021)
5. **Dao et al.** - "FlashAttention: Fast and Memory-Efficient Exact Attention" (2022)
6. **Shazeer** - "GLU Variants Improve Transformer" (2020) — SwiGLU, GeGLU
7. **Xiong et al.** - "On Layer Normalization in the Transformer Architecture" (2020) — Pre-LN vs Post-LN