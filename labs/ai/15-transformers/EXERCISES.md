# 15-transformers — Exercises

**Prerequisites**: Read MATH_FOUNDATION.md, THEORY.md, and CODE_DEEP_DIVE.md first. Implement in Java.

---

## Exercise 1: Attention Scaling Experiment

**Goal**: Empirically verify why $\sqrt{d_k}$ scaling is necessary.

### Task 1.1: Implement Scaled Dot-Product Attention
```java
// src/main/java/com/ailab/transformer/Attention.java
public class Attention {
    public static double[][] scaledDotProductAttention(
            double[][] Q, double[][] K, double[][] V, double[][] mask) {
        // 1. scores = Q @ K^T / sqrt(dk)
        // 2. if mask != null: scores += mask
        // 3. attn = softmax(scores, axis=-1)
        // 4. return attn @ V
    }
}
```

### Task 1.2: Variance Analysis
Generate random $Q, K \in \mathbb{R}^{n \times d_k}$ with entries $\sim \mathcal{N}(0, 1)$.
- Compute empirical variance of $QK^T$ entries for $d_k \in \{16, 64, 256, 1024\}$
- Compare with theoretical $\text{Var} = d_k$
- Test softmax gradient magnitude with and without scaling

```java
public static void varianceExperiment() {
    for (int dk : new int[]{16, 64, 256, 1024}) {
        double[][] Q = randomMatrix(10, dk);
        double[][] K = randomMatrix(10, dk);
        double varUnscaled = variance(matmul(Q, transpose(K)));
        double varScaled = variance(scale(matmul(Q, transpose(K)), 1.0/Math.sqrt(dk)));
        System.out.printf("dk=%d: unscaled=%.2f, scaled=%.2f (theory=1.0)%n", dk, varUnscaled, varScaled);
    }
}
```

### Task 1.3: Gradient Saturation Test
For $d_k=1024$, compute $\frac{\partial \text{softmax}}{\partial \text{scores}}$ with and without scaling.
- Measure max gradient value
- Explain why unscaled leads to vanishing gradients

**Questions**:
1. What is the theoretical variance of $q^T k$ when $q_i, k_i \sim \mathcal{N}(0,1)$?
2. At what $d_k$ does unscaled softmax saturate (max prob > 0.99)?
3. Why does scaling fix this?

---

## Exercise 2: Multi-Head Attention Implementation

**Goal**: Build multi-head attention from scratch with proper dimension handling.

### Task 2.1: Projection Layers
```java
// src/main/java/com/ailab/transformer/MultiHeadAttention.java
public class MultiHeadAttention {
    private final int dModel, numHeads, dHead;
    private final LinearLayer Wq, Wk, Wv, Wo;
    
    public MultiHeadAttention(int dModel, int numHeads) {
        this.dModel = dModel;
        this.numHeads = numHeads;
        this.dHead = dModel / numHeads;
        
        // Projections: dModel -> dModel (will split into heads)
        Wq = new LinearLayer(dModel, dModel);
        Wk = new LinearLayer(dModel, dModel);
        Wv = new LinearLayer(dModel, dModel);
        Wo = new LinearLayer(dModel, dModel);  // Output projection
    }
}
```

### Task 2.2: Split Heads
```java
// Input: (batch, seq, dModel) -> Output: (batch, numHeads, seq, dHead)
private double[][][][] splitHeads(double[][][] x) {
    int batch = x.length;
    int seq = x[0].length;
    double[][][][] out = new double[batch][numHeads][seq][dHead];
    // TODO: Reshape
    return out;
}

// Inverse: (batch, numHeads, seq, dHead) -> (batch, seq, dModel)
private double[][][] combineHeads(double[][][][] x) { /* TODO */ }
```

### Task 2.3: Forward Pass
```java
public double[][][] forward(double[][][] x, double[][][] mask) {
    // 1. Project: Q = x @ Wq, K = x @ Wk, V = x @ Wv
    // 2. Split heads
    // 3. For each head: attn = scaledDotProductAttention(Q_h, K_h, V_h, mask)
    // 4. Combine heads
    // 5. Output projection: out @ Wo
}
```

### Task 2.4: Test on Synthetic Data
Create a "copy" task: input sequence of random vectors, target = same sequence.
- Use 1-layer transformer with MHA
- Train to copy input to output
- Verify attention learns identity mapping

---

## Exercise 3: Positional Encoding Comparison

**Goal**: Compare sinusoidal, learnable, and RoPE positional encodings.

### Task 3.1: Sinusoidal PE
```java
public class SinusoidalPositionalEncoding {
    public double[][] encode(int seqLen, int dModel) {
        double[][] pe = new double[seqLen][dModel];
        for (int pos = 0; pos < seqLen; pos++) {
            for (int i = 0; i < dModel; i += 2) {
                double angle = pos / Math.pow(10000.0, (double)i / dModel);
                pe[pos][i] = Math.sin(angle);
                if (i + 1 < dModel) pe[pos][i+1] = Math.cos(angle);
            }
        }
        return pe;
    }
}
```

### Task 3.2: Learnable PE
```java
public class LearnablePositionalEncoding {
    private double[][] pe;  // (maxLen, dModel) - learned parameters
    
    public double[][] forward(int seqLen) {
        return Arrays.copyOfRange(pe, 0, seqLen);
    }
}
```

### Task 3.3: RoPE (Rotary Positional Embeddings)
```java
public class RoPE {
    // Rotate pairs of dimensions by position-dependent angles
    public double[][] apply(double[][] x, int startPos) {
        // x: (seq, dModel) - assume dModel even
        // For each pair (2i, 2i+1): rotate by pos * theta_i
        // theta_i = 10000^(-2i/dModel)
    }
}
```

### Task 3.4: Extrapolation Test
Train a small transformer on sequences of length 128. Test on length 256.
- Compare accuracy drop for each PE type
- Sinusoidal and RoPE should extrapolate better than learnable

**Questions**:
1. Why does sinusoidal PE allow extrapolation?
2. How does RoPE encode relative position in the attention score?
3. What happens to learnable PE at positions > maxLen?

---

## Exercise 4: Pre-LN vs Post-LN Training Stability

**Goal**: Compare training dynamics of Pre-LN and Post-LN transformers.

### Task 4.1: Implement Both Variants
```java
// Pre-LN Encoder Block
public class PreLNEncoderBlock {
    public double[][][] forward(double[][][] x) {
        // x + MHA(LN(x))
        // x + FFN(LN(x))
    }
}

// Post-LN Encoder Block
public class PostLNEncoderBlock {
    public double[][][] forward(double[][][] x) {
        // LN(x + MHA(x))
        // LN(x + FFN(x))
    }
}
```

### Task 4.2: Deep Transformer Training
Build 12-layer and 24-layer transformers with each variant.
- Use same initialization, LR, data
- Track: training loss, gradient norms per layer, max attention weight

```java
public static void compareVariants() {
    for (String variant : new String[]{"PreLN", "PostLN"}) {
        for (int depth : new int[]{6, 12, 24}) {
            Transformer model = createModel(variant, depth);
            train(model);
            // Log gradient norms at each layer
        }
    }
}
```

### Task 4.3: Learning Rate Sweep
For 24-layer models, test LR $\in \{10^{-4}, 3\times10^{-4}, 10^{-3}, 3\times10^{-3}\}$.
- Which variant tolerates higher LR?
- Plot final loss vs LR

**Questions**:
1. Why does Post-LN suffer from gradient vanishing in deep networks?
2. How does Pre-LN create a "gradient highway"?
3. What is DeepNorm and when is it needed?

---

## Exercise 5: Causal Masking Implementation

**Goal**: Implement correct causal masking for autoregressive generation.

### Task 5.1: Causal Mask Generation
```java
public class CausalMask {
    // Returns (seq, seq) mask with -inf for j > i
    public static double[][] generate(int seqLen) {
        double[][] mask = new double[seqLen][seqLen];
        for (int i = 0; i < seqLen; i++) {
            for (int j = 0; j < seqLen; j++) {
                mask[i][j] = (j > i) ? Double.NEGATIVE_INFINITY : 0.0;
            }
        }
        return mask;
    }
}
```

### Task 5.2: Autoregressive Generation Loop
```java
public class AutoregressiveGenerator {
    private TransformerDecoder model;
    
    public int[] generate(int[] prompt, int maxNewTokens) {
        List<Integer> generated = new ArrayList<>(Arrays.asList(prompt));
        
        for (int step = 0; step < maxNewTokens; step++) {
            // 1. Prepare input: all tokens so far
            // 2. Create causal mask for current length
            // 3. Forward pass through decoder
            // 4. Get logits for last position
            // 5. Sample next token (argmax or temperature sampling)
            // 6. Append to generated
        }
        return generated.stream().mapToInt(i -> i).toArray();
    }
}
```

### Task 5.3: Verify No Future Peeking
- Train on a sequence where next token depends on future (impossible with causal mask)
- Verify model cannot cheat
- Compare with non-causal attention (should overfit/cheat)

---

## Exercise 6: Encoder-Decoder Cross-Attention

**Goal**: Build a sequence-to-sequence model with cross-attention.

### Task 6.1: Encoder
```java
public class TransformerEncoder {
    private List<EncoderBlock> layers;
    
    public double[][][] forward(double[][][] src, double[][][] srcMask) {
        double[][][] x = src;
        for (EncoderBlock layer : layers) {
            x = layer.forward(x, srcMask);
        }
        return x;  // (batch, srcSeq, dModel)
    }
}
```

### Task 6.2: Decoder with Cross-Attention
```java
public class DecoderBlock {
    private MultiHeadAttention selfAttn;
    private MultiHeadAttention crossAttn;  // Q from decoder, K,V from encoder
    private FFN ffn;
    
    public double[][][] forward(double[][][] tgt, double[][][] memory, 
                                 double[][][] tgtMask, double[][][] memoryMask) {
        // 1. Self-attention with causal mask
        // 2. Cross-attention: Q=tgt, K=memory, V=memory
        // 3. FFN
        // All with residuals and layer norms
    }
}
```

### Task 6.3: Seq2Seq Task — Sequence Reversal
- Input: random sequence of integers [1..10]
- Target: reversed sequence
- Train encoder-decoder to reverse sequences

**Questions**:
1. Why does cross-attention use encoder output for K,V?
2. What would happen if decoder self-attention weren't causal?
3. How does cross-attention enable "alignment" in translation?

---

## Exercise 7: FFN Variants (SwiGLU, GeGLU)

**Goal**: Implement and compare modern gated FFN variants.

### Task 7.1: Implement SwiGLU
```java
public class SwiGLU {
    private LinearLayer W1, W2, W3;  // W1, W3 for gate; W2 for output
    
    public double[][] forward(double[][] x) {
        // Swish(x @ W1) * (x @ W3) @ W2
        // Swish(x) = x * sigmoid(x)
    }
}
```

### Task 7.2: Implement GeGLU
```java
public class GeGLU {
    // GELU(x @ W1) * (x @ W3) @ W2
}
```

### Task 7.3: Parameter Count Matching
Standard FFN: $d_{model} \times 4d_{model} + 4d_{model} \times d_{model} = 8 d_{model}^2$

SwiGLU with $d_{ff} = \frac{8}{3}d_{model}$:
- $W_1, W_3: d_{model} \times \frac{8}{3}d_{model}$ each
- $W_2: \frac{8}{3}d_{model} \times d_{model}$
- Total: $3 \times \frac{8}{3}d_{model}^2 = 8 d_{model}^2$ ✓

### Task 7.4: Compare on Language Modeling
Train small transformer (4 layers) on character-level language modeling.
- Compare: ReLU, GELU, SwiGLU, GeGLU
- Metrics: perplexity, training speed, memory

---

## Exercise 8: Attention Complexity Analysis

**Goal**: Profile attention complexity and test optimizations.

### Task 8.1: Time/Memory Profiling
```java
public class AttentionProfiler {
    public static void profile(int n, int d) {
        double[][] Q = randomMatrix(n, d);
        double[][] K = randomMatrix(n, d);
        double[][] V = randomMatrix(n, d);
        
        long start = System.nanoTime();
        double[][] out = Attention.scaledDotProductAttention(Q, K, V, null);
        long elapsed = System.nanoTime() - start;
        
        // Measure memory (approximate via allocated arrays)
        System.out.printf("n=%d, d=%d: time=%.2f ms%n", n, d, elapsed/1e6);
    }
}
```

Run for $n \in \{128, 256, 512, 1024, 2048\}$, $d=512$.
- Plot time vs $n$ (should be quadratic)
- Plot memory vs $n$

### Task 8.2: Sliding Window Attention
```java
public class SlidingWindowAttention {
    // Only attend to window_size neighbors on each side
    public static double[][][] forward(double[][][] Q, double[][][] K, double[][][] V, int window) {
        // For each position i, only attend to j in [i-window, i+window]
        // Implement by masking attention scores
    }
}
```

### Task 8.3: Compare Speed
- Standard attention: $O(n^2)$
- Sliding window: $O(n \cdot w)$ where $w \ll n$
- Measure crossover point

---

## Exercise 9: RoPE Implementation

**Goal**: Implement Rotary Positional Embeddings correctly.

### Task 9.1: Complex Number Rotation
```java
public class RoPE {
    // For each head, split dimensions into pairs
    // Pair (2i, 2i+1) treated as complex number: a + bi
    // Rotate by angle = pos * theta_i
    // theta_i = 10000^(-2i/d_head)
    
    public static void applyRoPEInPlace(double[][][] q, double[][][] k, int startPos) {
        // q, k: (batch, numHeads, seq, dHead)
        // dHead must be even
    }
}
```

### Task 9.2: Verify Relative Position Property
RoPE makes attention score depend only on relative position:
$$\langle q_i, k_j \rangle_{RoPE} = \langle q_i, k_j \rangle \cos(\theta(i-j)) + \dots$$

Test: Compute attention scores for positions $(0,1), (10,11), (100,101)$ — should be identical.

### Task 9.3: Compare with Absolute PE
Train on sequences up to 512, test on 1024.
- RoPE should maintain performance
- Absolute PE (sinusoidal/learnable) may degrade

---

## Exercise 10: KV Cache for Autoregressive Generation

**Goal**: Implement efficient KV caching to avoid recomputing attention for past tokens.

### Task 10.1: KV Cache Data Structure
```java
public class KVCache {
    // For each layer: cache K and V
    // Shape: (batch, numHeads, seqLen, dHead)
    private List<double[][][][]> keyCache;
    private List<double[][][][]> valueCache;
    
    public void update(int layerIdx, double[][][] newK, double[][][] newV) {
        // Concatenate along seq dimension
    }
    
    public double[][][][] getKey(int layerIdx) { /* return cached K */ }
    public double[][][][] getValue(int layerIdx) { /* return cached V */ }
}
```

### Task 10.2: Cached Attention Forward
```java
public class CachedMultiHeadAttention extends MultiHeadAttention {
    private KVCache cache;
    
    public double[][][] forward(double[][][] x, KVCache cache, boolean useCache) {
        // 1. Compute Q, K, V for current x (usually just last token)
        // 2. If useCache: append K,V to cache, use full cached K,V for attention
        // 3. If !useCache: normal attention (training)
    }
}
```

### Task 10.3: Benchmark Generation Speed
Compare generation time for 100 tokens:
- Without KV cache: recompute all attention each step
- With KV cache: only compute for new token

**Expected**: Without cache $O(n^2)$ per step, with cache $O(n)$ per step.

---

## Starter Project Structure

```
15-transformers/
├── src/
│   ├── main/
│   │   └── java/com/ailab/transformer/
│   │       ├── Attention.java
│   │       ├── MultiHeadAttention.java
│   │       ├── SinusoidalPositionalEncoding.java
│   │       ├── LearnablePositionalEncoding.java
│   │       ├── RoPE.java
│   │       ├── PreLNEncoderBlock.java
│   │       ├── PostLNEncoderBlock.java
│   │       ├── DecoderBlock.java
│   │       ├── TransformerEncoder.java
│   │       ├── TransformerDecoder.java
│   │       ├── FFN.java
│   │       ├── SwiGLU.java
│   │       ├── GeGLU.java
│   │       ├── CausalMask.java
│   │       ├── AutoregressiveGenerator.java
│   │       ├── KVCache.java
│   │       └── AttentionProfiler.java
│   └── test/
│       └── java/com/ailab/transformer/
│           └── TransformerTest.java
```

---

## Deliverables

For each exercise, submit:
1. **Working Java code** in `src/main/java/...`
2. **Plots** (save as PNG in `results/`)
3. **Written answers** to questions in `EXERCISE_ANSWERS.md`
4. **Benchmark results** for Exercises 1, 4, 8, 10

---

## Grading Rubric

| Component | Points |
|-----------|--------|
| Correctness (passes tests) | 35 |
| Code quality & vectorization | 20 |
| Plot quality & labels | 15 |
| Written explanations | 15 |
| Bonus (Exercise 10) | 15 |
| **Total** | **100** |