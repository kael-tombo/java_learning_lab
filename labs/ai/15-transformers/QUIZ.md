# 15-transformers — Quiz

**Instructions**: Answer all 10 questions. Each question has one correct answer unless marked "Select all that apply." Check your answers at the end.

---

### Question 1: Scaled Dot-Product Attention Scaling
Why is the attention score divided by $\sqrt{d_k}$?
- A) To make the output dimension match $d_k$
- B) To prevent softmax saturation for large $d_k$ by keeping variance of dot products $\approx 1$
- C) To normalize the query and key vectors to unit length
- D) To ensure the attention weights sum to 1

### Question 2: Multi-Head Attention Dimensions
For a transformer with $d_{model}=512$ and $h=8$ heads, what are the dimensions of each head's query, key, and value projections?
- A) $d_k = d_v = 512$
- B) $d_k = d_v = 64$
- C) $d_k = 64, d_v = 512$
- D) $d_k = 512, d_v = 64$

### Question 3: Positional Encoding Properties
Which statement about sinusoidal positional encoding is **false**?
- A) It allows extrapolation to sequence lengths longer than seen during training
- B) It has no learnable parameters
- C) $PE_{pos+k}$ can be represented as a linear function of $PE_{pos}$
- D) It outperforms learnable positional embeddings on all tasks

### Question 4: Pre-LN vs Post-LN
What is the key advantage of Pre-LN (LayerNorm before residual) over Post-LN?
- A) Pre-LN has fewer parameters
- B) Pre-LN provides better gradient flow in deep networks, allowing larger learning rates
- C) Post-LN is not compatible with residual connections
- D) Pre-LN eliminates the need for warmup

### Question 5: Causal Masking
In decoder self-attention, the causal mask $M$ has $M_{ij} = -\infty$ for $i < j$. What does this achieve?
- A) Position $i$ attends only to positions $j \le i$ (no future tokens)
- B) Position $i$ attends only to positions $j \ge i$ (no past tokens)
- C) All positions attend equally to all positions
- D) The first token attends to all, others attend only to previous

### Question 6: Cross-Attention in Decoder
In encoder-decoder attention, what are $Q, K, V$?
- A) $Q$ from encoder, $K,V$ from decoder
- B) $Q$ from decoder, $K,V$ from encoder
- C) All from encoder
- D) All from decoder

### Question 7: FFN Variants
What is the key difference between standard FFN and SwiGLU?
- A) SwiGLU uses GELU instead of ReLU
- B) SwiGLU has a gating mechanism: $(Swish(xW_1) \odot xW_3)W_2$ vs $ReLU(xW_1)W_2$
- C) SwiGLU removes the second linear layer
- D) SwiGLU uses layer norm inside the FFN

### Question 8: Attention Complexity
What is the time and memory complexity of standard self-attention for sequence length $n$ and model dimension $d$?
- A) Time: $O(n d)$, Memory: $O(n d)$
- B) Time: $O(n^2 d)$, Memory: $O(n^2)$
- C) Time: $O(n d^2)$, Memory: $O(n d)$
- D) Time: $O(n^3)$, Memory: $O(n^2)$

### Question 9: RoPE (Rotary Positional Embeddings)
How does RoPE encode position?
- A) Adds learnable positional embeddings to token embeddings
- B) Rotates query and key vectors by position-dependent angles in complex plane
- C) Concatenates positional encoding to query/key vectors
- D) Uses sinusoidal functions added to attention scores

### Question 10: Flash Attention
What is the main innovation of Flash Attention?
- A) Approximates attention with linear complexity
- B) Uses sparse attention patterns
- C) IO-aware algorithm that fuses softmax and matmul without materializing $QK^T$ matrix
- D) Replaces softmax with a linear kernel

---

## Answer Key

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **B** | Without scaling, $\text{Var}(QK^T) \propto d_k$, pushing softmax into saturation where gradients vanish. Scaling by $1/\sqrt{d_k}$ keeps variance $\approx 1$. |
| 2 | **B** | $d_k = d_v = d_{model}/h = 512/8 = 64$. Each head gets $1/h$ of the model dimension. |
| 3 | **D** | Sinusoidal PE does NOT universally outperform learnable PE. Learnable PE (BERT, GPT) often works better; sinusoidal enables extrapolation. |
| 4 | **B** | Pre-LN: gradient flows through identity path $\frac{\partial L}{\partial x} \approx \frac{\partial L}{\partial y}$ when $F$ is small. More stable, allows larger LR, no warmup needed in some cases. |
| 5 | **A** | $-\infty$ mask becomes 0 after softmax. Position $i$ only attends to $j \le i$ (current and past). |
| 6 | **B** | Decoder generates queries (what to look for), encoder provides keys/values (what's available to attend to). |
| 7 | **B** | SwiGLU uses gated linear unit: element-wise product of Swish-activated and linear projections, then final projection. |
| 8 | **B** | $QK^T$ is $n \times n$, computed in $O(n^2 d)$. Softmax over $n \times n$. Memory $O(n^2)$ for attention matrix. |
| 9 | **B** | RoPE applies rotation $e^{i m \theta_{pos}}$ to query/key in complex space, encoding relative position in dot product. |
| 10 | **C** | Flash Attention is EXACT attention (not approximate) but avoids writing/reading $QK^T$ to/from HBM by fusing operations in SRAM. |

---

## Scoring

- **9-10 correct**: Excellent — Strong transformer fundamentals
- **7-8 correct**: Good — Review attention mechanics and architectures
- **5-6 correct**: Fair — Re-read MATH_FOUNDATION.md sections on attention and architecture
- **<5 correct**: Needs work — Implement attention from scratch in CODE_DEEP_DIVE

---

## Follow-Up Exercises

For each question you missed, do the corresponding exercise in **EXERCISES.md**:
- Q1 → Exercise 1 (Attention Scaling Experiment)
- Q2 → Exercise 2 (Multi-Head Dimension Verification)
- Q3 → Exercise 3 (Positional Encoding Comparison)
- Q4 → Exercise 4 (Pre-LN vs Post-LN Training)
- Q5 → Exercise 5 (Causal Mask Implementation)
- Q6 → Exercise 6 (Encoder-Decoder Attention)
- Q7 → Exercise 7 (FFN Variants)
- Q8 → Exercise 8 (Complexity Analysis)
- Q9 → Exercise 9 (RoPE Implementation)
- Q10 → Exercise 10 (Flash Attention Concepts)