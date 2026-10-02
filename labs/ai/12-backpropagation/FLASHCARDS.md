# 12-backpropagation — Flashcards

## Core Concepts

| Term | Definition |
|------|------------|
| **Backpropagation** | Algorithm to compute $\frac{\partial L}{\partial \theta}$ for all parameters $\theta$ using chain rule |
| **Forward Pass** | Input $\to$ hidden layers $\to$ output $\to$ loss computation |
| **Backward Pass** | Loss $\to$ output layer $\to$ hidden layers $\to$ input layer; computes gradients |
| **Computational Graph** | DAG where nodes = operations (matmul, add, activation), edges = tensors |
| **Automatic Differentiation (Autograd)** | Automatic construction of backward pass from computational graph |
| **Credit Assignment** | Problem of determining which weights contributed to output error |

---

## Chain Rule Fundamentals

### Single Variable Chain Rule
$$\frac{dz}{dx} = \frac{dz}{dy} \cdot \frac{dy}{dx}$$

### Multivariable Chain Rule
If $z = f(y_1, y_2, ..., y_n)$ and each $y_i = g_i(x)$:
$$\frac{dz}{dx} = \sum_{i=1}^n \frac{\partial z}{\partial y_i} \frac{dy_i}{dx}$$

### Vector Chain Rule (Neural Networks)
For layer $l$: $\mathbf{z}^{[l]} = \mathbf{W}^{[l]}\mathbf{a}^{[l-1]} + \mathbf{b}^{[l]}$, $\mathbf{a}^{[l]} = \sigma(\mathbf{z}^{[l]})$

$$\frac{\partial L}{\partial \mathbf{W}^{[l]}} = \underbrace{\frac{\partial L}{\partial \mathbf{z}^{[l]}}}_{\boldsymbol{\delta}^{[l]}} \cdot (\mathbf{a}^{[l-1]})^T$$

$$\frac{\partial L}{\partial \mathbf{b}^{[l]}} = \boldsymbol{\delta}^{[l]}$$

$$\boldsymbol{\delta}^{[l-1]} = (\mathbf{W}^{[l]})^T \boldsymbol{\delta}^{[l]} \odot \sigma'(\mathbf{z}^{[l-1]})$$

---

## Activation Functions & Derivatives

| Activation | Formula | Derivative | Range | Notes |
|------------|---------|------------|-------|-------|
| **Sigmoid** | $\sigma(z) = \frac{1}{1+e^{-z}}$ | $\sigma(z)(1-\sigma(z))$ | (0, 1) | Max grad 0.25; vanishes |
| **Tanh** | $\tanh(z)$ | $1 - \tanh^2(z)$ | (-1, 1) | Max grad 1; zero-centered |
| **ReLU** | $\max(0, z)$ | $\mathbb{1}_{z>0}$ | [0, ∞) | No vanishing for $z>0$ |
| **Leaky ReLU** | $z$ if $z>0$ else $\alpha z$ | 1 if $z>0$ else $\alpha$ | (-∞, ∞) | Fixes dying ReLU |
| **GELU** | $0.5z(1+\tanh[\sqrt{2/\pi}(z+0.0447z^3)])$ | Complex | (-∞, ∞) | Used in transformers |
| **Softmax** | $\frac{e^{z_i}}{\sum_j e^{z_j}}$ | Jacobian: $S_{ij} = s_i(\delta_{ij} - s_j)$ | (0, 1), sums to 1 | Output layer for classification |

---

## Loss Functions & Gradients

| Loss | Formula | $\frac{\partial L}{\partial \mathbf{z}}$ (with Softmax/Sigmoid) |
|------|---------|---------------------------------------------------------------|
| **MSE** | $\frac{1}{2}\|\mathbf{y} - \hat{\mathbf{y}}\|^2$ | $(\hat{\mathbf{y}} - \mathbf{y}) \odot \sigma'(\mathbf{z})$ |
| **Binary Cross Entropy** | $-[y\log\hat{y} + (1-y)\log(1-\hat{y})]$ | $\hat{y} - y$ (with sigmoid) |
| **Categorical Cross Entropy** | $-\sum_i y_i \log \hat{y}_i$ | $\hat{\mathbf{y}} - \mathbf{y}$ (with softmax) |

**Key Insight**: With canonical pairing (sigmoid+BCE, softmax+CE), gradient simplifies to $\hat{y} - y$ — no explicit derivative of activation needed!

---

## Backpropagation Algorithm (Step by Step)

### 1. Forward Pass (Cache Everything)
```python
for each layer l:
    Z[l] = W[l] @ A[l-1] + b[l]
    A[l] = activation(Z[l])
Loss = loss_fn(A[L], Y)
```

### 2. Backward Pass
```python
# Output layer
dZ[L] = A[L] - Y  # For softmax+CE or sigmoid+BCE
dW[L] = dZ[L] @ A[L-1].T / m
db[L] = np.mean(dZ[L], axis=1, keepdims=True)

# Hidden layers (l = L-1 down to 1)
for l in reversed(range(1, L)):
    dZ[l] = (W[l+1].T @ dZ[l+1]) * activation_derivative(Z[l])
    dW[l] = dZ[l] @ A[l-1].T / m
    db[l] = np.mean(dZ[l], axis=1, keepdims=True)
```

### 3. Update Parameters
```python
W[l] -= learning_rate * dW[l]
b[l] -= learning_rate * db[l]
```

---

## Matrix Dimensions Cheatsheet

| Variable | Shape | Description |
|----------|-------|-------------|
| $\mathbf{X}$ | $(n_{in}, m)$ | Input (m samples) |
| $\mathbf{W}^{[l]}$ | $(n_l, n_{l-1})$ | Weights layer l |
| $\mathbf{b}^{[l]}$ | $(n_l, 1)$ | Bias layer l |
| $\mathbf{Z}^{[l]}$ | $(n_l, m)$ | Pre-activation |
| $\mathbf{A}^{[l]}$ | $(n_l, m)$ | Post-activation |
| $\boldsymbol{\delta}^{[l]}$ | $(n_l, m)$ | Upstream gradient $\frac{\partial L}{\partial \mathbf{Z}^{[l]}}$ |
| $\frac{\partial L}{\partial \mathbf{W}^{[l]}}$ | $(n_l, n_{l-1})$ | Weight gradient |
| $\frac{\partial L}{\partial \mathbf{b}^{[l]}}$ | $(n_l, 1)$ | Bias gradient |

---

## Vanishing / Exploding Gradients

### Vanishing Gradients
**Cause**: Repeated multiplication by small derivatives ($\sigma' \le 0.25$, $\tanh' \le 1$)
$$\frac{\partial L}{\partial \mathbf{W}^{[1]}} \propto \prod_{l=2}^L \sigma'(\mathbf{z}^{[l]}) \to 0$$

**Solutions**:
1. **ReLU / Leaky ReLU / GELU** — derivative = 1 for positive inputs
2. **Residual Connections** — $\mathbf{x}_{l+1} = \mathbf{x}_l + F(\mathbf{x}_l)$; gradient flows through identity
3. **Batch Normalization** — keeps activations in non-saturating regime
4. **Better Initialization** — He/Xavier initialization
5. **Gradient Clipping** — for exploding gradients

### Exploding Gradients
**Cause**: Repeated multiplication by large weights ($\|W\| > 1$)
**Fix**: Gradient clipping (clip norm to max 1.0 or 5.0)

---

## Weight Initialization

| Method | Formula | Best For |
|--------|---------|----------|
| **Xavier/Glorot** | $W \sim \mathcal{U}[-\sqrt{6/(n_{in}+n_{out})}, \sqrt{6/(n_{in}+n_{out})}]$ | Tanh, Sigmoid |
| **He Initialization** | $W \sim \mathcal{N}(0, \sqrt{2/n_{in}})$ | ReLU, Leaky ReLU |
| **LeCun Normal** | $W \sim \mathcal{N}(0, \sqrt{1/n_{in}})$ | SELU |

---

## Gradient Checking (Numerical Verification)

```python
def gradient_check(f, x, analytic_grad, eps=1e-7):
    """
    f: function returning scalar loss
    x: parameter vector
    analytic_grad: gradient from backprop
    """
    numeric_grad = np.zeros_like(x)
    for i in range(len(x)):
        x_plus = x.copy(); x_plus[i] += eps
        x_minus = x.copy(); x_minus[i] -= eps
        numeric_grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
    
    # Relative error
    diff = np.linalg.norm(numeric_grad - analytic_grad) / \
           (np.linalg.norm(numeric_grad) + np.linalg.norm(analytic_grad))
    
    return diff < 1e-7  # Should be ~1e-9 for correct backprop
```

**Tips**:
- Use central difference $(f(x+\epsilon) - f(x-\epsilon))/2\epsilon$ for $O(\epsilon^2)$ accuracy
- Check only a random subset of parameters (too slow for all)
- Disable dropout, batch norm during checking
- Use $\epsilon = 10^{-7}$ for float32, $10^{-10}$ for float64

---

## Common Bugs & Debugging

| Bug | Symptom | Fix |
|-----|---------|-----|
| **Wrong matrix transpose** | Shape mismatch in `dW = dZ @ A.T` | Verify: `dW.shape == W.shape` |
| **Missing bias gradient** | Bias never updates | `db = np.mean(dZ, axis=1, keepdims=True)` |
| **Activation derivative wrong** | Gradients don't match numeric | Use `dSigmoid = A * (1 - A)` not `Z * (1 - Z)` |
| **Forget to divide by batch size** | Gradients too large | `dW = dZ @ A.T / m` |
| **In-place modification of cache** | Forward pass corrupted | Copy arrays before modifying |
| **Index off-by-one in loop** | Layer gradients wrong | Print shapes at each layer |

---

## Interview Quick Reference

**Q**: "Derive the backprop equations for a 2-layer network."
**A**: 
1. $L \to \hat{y} \to z^{[2]} \to W^{[2]}$: $\delta^{[2]} = \hat{y}-y$, $dW^{[2]} = \delta^{[2]} a^{[1]T}$
2. $z^{[2]} \to a^{[1]} \to z^{[1]} \to W^{[1]}$: $\delta^{[1]} = (W^{[2]T} \delta^{[2]}) \odot \sigma'(z^{[1]})$, $dW^{[1]} = \delta^{[1]} x^T$

**Q**: "Why does ReLU solve vanishing gradients?"
**A**: $\text{ReLU}'(z) = 1$ for $z>0$. No multiplication by $<1$ values in positive regime.

**Q**: "What's the gradient of softmax cross-entropy?"
**A**: $\frac{\partial L}{\partial z_i} = \hat{y}_i - y_i$. Beautifully simple!

**Q**: "How does batch norm affect backprop?"
**A**: Adds extra paths in computational graph. Gradient flows through normalization statistics (mean, var). Acts as regularizer.

**Q**: "Explain gradient checking."
**A**: Compare analytic gradient $\frac{\partial L}{\partial w}$ with numeric $\frac{L(w+\epsilon)-L(w-\epsilon)}{2\epsilon}$. Relative error should be $< 10^{-7}$.

**Q**: "What causes exploding gradients in RNNs?"
**A**: Repeated multiplication by same weight matrix $W$ over many time steps. If $\rho(W) > 1$, gradients explode exponentially.