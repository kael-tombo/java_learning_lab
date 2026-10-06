# Lab 01: Transformer Architecture — Math Foundation

## 1. Linear Algebra Prerequisites

### Matrix Multiplication
For A ∈ ℝ^(m×k) and B ∈ ℝ^(k×n):
```
C[i][j] = Σ_{p=0}^{k-1} A[i][p] · B[p][j]
```
Cost: O(m·k·n) FLOPs.

### Matrix Transpose
```
(Aᵀ)[i][j] = A[j][i]
```
Useful for computing Q·Kᵀ efficiently.

### Dot Product & Cosine Similarity
```
a·b = Σ a_i b_i
cos(a,b) = (a·b) / (‖a‖ ‖b‖)
```
Attention scores are unnormalized dot products (not cosine similarity).

## 2. The Softmax Function

```
softmax(z_i) = exp(z_i) / Σ_j exp(z_j)
```

**Numerical stability**: subtract max before exponentiating:
```
softmax(z_i) = exp(z_i - max(z)) / Σ_j exp(z_j - max(z))
```

Properties:
- Output is a probability distribution (all positive, sum to 1).
- Monotonic: larger input → larger output.
- Temperature τ: softmax(z/τ) — lower τ → sharper distribution.

## 3. Attention Score Derivation

Given Q, K, V ∈ ℝ^(n×d):

```
S = Q·Kᵀ          ∈ ℝ^(n×n)   raw affinity scores
S' = S / √d_k     ∈ ℝ^(n×n)   scaled scores
A = softmax(S')   ∈ ℝ^(n×n)   attention weights
O = A·V           ∈ ℝ^(n×d)   output
```

**Why √d_k?** If Q and K components are independent with mean 0 and variance 1,
then each dot product has variance d_k. Dividing by √d_k normalizes variance to 1.

## 4. Multi-Head Attention Dimensions

```
d_model = 512, h = 8 heads
d_k = d_v = d_model / h = 64

W_q, W_k, W_v ∈ ℝ^(d_model × d_k)   per head
W_o ∈ ℝ^(h·d_v × d_model) = ℝ^(512 × 512)
```

Total parameters for one MHA layer: 4 · d_model² = 4 · 512² ≈ 1M.

## 5. Positional Encoding Derivation

```
PE(pos, 2i)   = sin( pos / 10000^(2i/d) )
PE(pos, 2i+1) = cos( pos / 10000^(2i/d) )
```

**Key property**: PE(pos+k) can be represented as a linear function of PE(pos):
```
PE(pos+k, 2i)   = sin(ω_i·(pos+k)) = sin(ω_i·pos)cos(ω_i·k) + cos(ω_i·pos)sin(ω_i·k)
```
This lets the model learn relative positions via linear attention transformations.

## 6. Layer Normalization

```
μ = (1/d) Σ x_i
σ² = (1/d) Σ (x_i - μ)²
x̂_i = (x_i - μ) / √(σ² + ε)
y_i = γ_i · x̂_i + β_i
```

- γ (gain) and β (bias) are learnable parameters.
- ε = 1e-5 prevents division by zero.
- Normalizes across the feature dimension (not batch dimension).

## 7. Feed-Forward Network

```
FFN(x) = W_2 · activation(W_1 · x + b_1) + b_2
```

- W_1 ∈ ℝ^(d_model × d_ff), W_2 ∈ ℝ^(d_ff × d_model)
- d_ff = 4 · d_model (typical)
- Activation: ReLU, GELU, or SwiGLU (modern).

## 8. Complexity Analysis

| Operation | FLOPs | Memory |
|-----------|-------|--------|
| Q·Kᵀ | O(n²·d) | O(n²) |
| softmax | O(n²) | O(n²) |
| A·V | O(n²·d) | O(n·d) |
| FFN | O(n·d·d_ff) | O(n·d) |
| Total per layer | O(n²·d + n·d²) | O(n²) |

For n >> d, attention dominates. For d >> n, FFN dominates.

## 9. Gradient Flow

Residual connections create "gradient highways":
```
∂L/∂x = ∂L/∂y · (1 + ∂Sublayer/∂x)
```

The `1 +` term ensures gradients can flow directly, mitigating vanishing
gradients in deep networks.

## 10. Worked Example: Single-Head Attention

```
Q = [[1, 0], [0, 1]]    (2 tokens, d=2)
K = [[1, 0], [0, 1]]
V = [[1, 2], [3, 4]]

S = Q·Kᵀ = [[1, 0], [0, 1]]
S' = S/√2 = [[0.707, 0], [0, 0.707]]
A = softmax(S') = [[0.668, 0.332], [0.332, 0.668]]
O = A·V = [[1.664, 2.664], [2.336, 3.336]]
```

Each output token is a weighted blend of both value vectors.
