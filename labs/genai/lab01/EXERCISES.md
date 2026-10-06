# Lab 01: Transformer Architecture — Exercises

## Exercise 1: Matrix Multiplication Warm-Up (Easy)

Implement a `matmul(double[][] A, double[][] B)` method in Java. Verify with a
known 2×2 example. Add a `transpose` helper.

**Hint**: Triple loop: `C[i][j] = Σ A[i][k] * B[k][j]`.

**Expected**: Correct result for a hand-computed test case.

---

## Exercise 2: Scaled Dot-Product Attention (Core)

Implement `attention(double[][] Q, double[][] K, double[][] V)`:

1. Compute scores = Q·Kᵀ.
2. Scale by 1/√d_k.
3. Apply softmax row-wise.
4. Multiply by V.

**Hint**: Write a `softmax(double[] row)` helper that subtracts the max for
numerical stability.

**Expected**: Output matrix where each row is a convex combination of V rows.

---

## Exercise 3: Multi-Head Attention (Core)

Implement `multiHeadAttention` with configurable head count `h`:

1. Project Q, K, V into h subspaces using learned weight matrices.
2. Run attention per head.
3. Concatenate and apply output projection W_o.

**Hint**: Use `d_model % h == 0`. Store heads in a 3D array `[h][n][d_k]`.

**Expected**: Output shape [n][d_model]; different heads produce different outputs.

---

## Exercise 4: Sinusoidal Positional Encoding (Easy)

Implement `positionalEncoding(int maxLen, int dModel)`:

```java
PE[pos][2i]   = sin(pos / 10000^(2i/dModel));
PE[pos][2i+1] = cos(pos / 10000^(2i/dModel));
```

**Expected**: A [maxLen][dModel] matrix; verify PE[0] has zeros in even columns
and ones in odd columns.

---

## Exercise 5: Encoder Layer (Core)

Assemble a full encoder layer:

```
x → SelfAttention → Dropout → Add&Norm → FFN → Dropout → Add&Norm
```

Implement `LayerNorm` with learnable gain and bias.

**Expected**: Output shape matches input shape; residual stream preserves information.

---

## Exercise 6: Causal Mask (Core)

Implement `applyCausalMask(double[][] scores)` that sets the upper triangle
(strictly above diagonal) to `-∞` (use `Double.NEGATIVE_INFINITY` or -1e9).

**Hint**: Loop `for i, for j > i: scores[i][j] = -1e9`.

**Expected**: After softmax, upper triangle weights are exactly 0.

---

## Exercise 7: Decoder Layer with Cross-Attention (Advanced)

Build a decoder layer with three sub-layers:

1. Masked self-attention (causal).
2. Cross-attention: Q from decoder state, K/V from encoder output.
3. FFN.

**Expected**: Decoder output attends to all encoder positions but only past decoder positions.

---

## Exercise 8: Full Transformer Assembly (Advanced)

Combine everything into a `Transformer` class:

- Token embedding + positional encoding.
- Stack of N encoder layers.
- Stack of N decoder layers.
- Final linear + softmax for token prediction.

**Expected**: Forward pass produces a probability distribution over the vocabulary.

---

## Exercise 9: Gradient Flow Analysis (Advanced)

Add a `backward` pass (or use a simple autograd) to compute ∂L/∂W for one
attention weight matrix. Verify gradients are non-zero and finite.

**Hint**: Use finite differences for gradient checking:
`∂f/∂w ≈ (f(w+ε) - f(w-ε)) / 2ε`.

**Expected**: Analytical and numerical gradients match within tolerance.

---

## Exercise 10: Complexity Profiling (Easy)

Instrument your attention implementation to count floating-point operations
for sequence lengths n = 128, 256, 512, 1024. Plot FLOPs vs n.

**Expected**: FLOPs grow quadratically with n — confirming O(n²) complexity.
