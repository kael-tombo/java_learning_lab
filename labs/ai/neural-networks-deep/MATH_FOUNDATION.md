# neural-networks-deep — Math Foundation

## 1. Perceptron Convergence

Objective: `f(w) = min_i y_i (w'x_i)` subject to `w` on the unit ball (the
subgradient of the hinge loss). Update `w <- w + alpha y_i x_i`. If separable, the
update count satisfies

```
updates <= O( (R / gamma)^2 ),   R = max_i ||x_i||,   gamma = min_i y_i (w*'x_i)
```

Proof sketch: each update increases `w'w*'` by at least `alpha*gamma` and increases
`||w||^2` by at most `alpha^2 R^2` (else the sample would have been correctly
classified). Bounding `||w||^2 <= 4R^2` gives `alpha gamma m <= 8R^2`.

Consequence: convergence is **finite but not fast**, and it is sensitive to the margin
`gamma`. A larger-margin problem converges in far fewer updates. This is the first
appearance of the margin idea that SVMs formalize.

## 2. Backpropagation as the Chain Rule

For `L` layers, the loss derivative with respect to `W_1` naively requires differentiating
through every path: `O(L^2)` work. Backprop reuses intermediates:

```
delta_L = dL/dz_L
delta_l = (W_{l+1})' delta_{l+1} .* phi'(z_l)
dL/dW_l = delta_l h_{l-1}'
```

Total cost `O(sum_l d_l * d_{l-1})`, i.e. one forward and one backward per layer. The
gradient is exact; the speedup is purely from reuse.

## 3. Vanishing and Exploding Gradients

Along one path, the Jacobian is a product:

```
dL/dh_0  contains  prod_{l=1..L}  W_l diag(phi'(z_l))
```

- If `||W_l|| < 1` and `|phi'| < 1`, the product decays exponentially in `L`.
- Sigmoid: `max |phi'| = 1/4`. For a 10-layer net with unit-norm weights,
  `0.25^10 ≈ 9.5e-7`.
- Tanh: `max |phi'| = 1`, so decay comes only from the weights — much better, which is why
  tanh replaced sigmoid in the 1990s.
- ReLU: `phi' = 1` on the positive half, so there is **no** multiplicative decay at all.
  The problem becomes dead units rather than vanishing gradients.

**Effective Jacobian with residuals**: for `y = x + F(x)`, `dy/dx = I + J_F`. Eigenvalues
sit near 1 when `||J_F||` is small, so the gradient path does not decay. This is the entire
argument for skip connections.

## 4. Activation Derivatives

```
sigmoid:   phi(z) = 1/(1+e^-z);       phi'(z) = phi(z)(1-phi(z)) <= 1/4
tanh:      phi'(z) = 1 - tanh^2(z)   <= 1
ReLU:      phi'(z) = 1[z > 0]
Leaky:     phi'(z) = 1 if z>0 else a
ELU:       phi'(z) = 1 if z>0 else alpha e^z
GELU:      phi(z) = z Phi(z);        phi'(z) = Phi(z) + z phi_N(z)
Swish:     phi(z) = z sigma(bz);     phi'(z) = sigma(bz) + bz sigma(bz)(1-sigma(bz))
```

`Phi` and `phi_N` are the standard normal CDF and PDF. Note sigmoid's derivative is
maximal only near `z = 0` — the saturated region is where the gradient vanishes, and it is
also where most units end up.

## 5. Cross-Entropy Against Logits

With logits `z` and softmax `p = softmax(z)`, cross-entropy `L = -sum_k y_k log p_k`:

```
dL/dz_j = p_j - y_j
```

Derivation: `dL/dp_j = -y_j/p_j` and `dp_j/dz_k = p_j(delta_jk - p_k)`, so
`dL/dz_j = -y_j(1-p_j) + p_j sum_k y_k = p_j - y_j` when `sum_k y_k = 1`.

This is why one must **not** compute softmax and then log separately in floating point: the
`p_j -> 0` branch produces `inf`. Use the fused form
`L = logsumexp(z) - z_target`, with `logsumexp` shifted by the max.

## 6. Loss Gradients

```
MSE:      dL/dz = 2 (z - y) / n
MAE:      dL/dz = sign(z - y) / n              (subgradient)
Huber(d): dL/dz = z - y    if |z-y| <= d, else d * sign(z - y)
BCE:      dL/dz = (sigma(z) - y) / n           (= p - y)
Focal:    dL/dz = -alpha_t (1-p_t)^gamma * (dL/dz of CE)
```

For classification, cross-entropy's `p - y` shrinks the gradient exactly when the model is
already right (large `|p - y|` is small when `p ~ y`). MAE's constant gradient is why
training converges slowly at the end — the step does not shrink with error size.

## 7. Variance-Preserving Initialization

Require each layer to preserve activation variance across `L` layers:

```
forward:  Var(a_l) = fan_in * Var(W) * Var(a_{l-1}) = Var(a_{l-1})
          =>  Var(W) = 1 / fan_in
backward: same requirement on the gradient path
          =>  Var(W) = 1 / fan_out
```

Satisfying both: `Var(W) = 2/(fan_in + fan_out)` — Xavier/Glorot.

ReLU zeroes half the units, so forward variance is halved per layer. Compensate:
`Var(W) = 2/fan_in` — He/Kaiming.

Check the arithmetic: with He init on a ReLU net, `Var(a_l) = fan_in * (2/fan_in) *
0.5 * Var(a_{l-1}) = Var(a_{l-1})`. Constant. With Xavier it halves per layer, which is why
deep ReLU nets trained with Xavier fail where He succeeds.

## 8. Adaptive Optimizers

```
AdaGrad:  g2 += g^2;                  w -= eta * g / (sqrt(g2) + eps)
RMSProp:  g2 = rho g2 + (1-rho) g^2;  w -= eta * g / (sqrt(g2) + eps)
Adam:     m = b1 m + (1-b1) g
          v = b2 v + (1-b2) g^2
          w -= eta * (m/(1-b1^t)) / (sqrt(v/(1-b2^t)) + eps)
```

`E[g^2]_t = E[g^2] * (1 - b2^t)` for constant-gradient squared expectation, so
`v/(1-b2^t)` is the unbiased estimate. Without it, at `t = 1` the update is
`eta * (1-b1) g / (sqrt((1-b2) g^2) + eps) ~ eta * 0.1 g / (0.1 |g|) = eta`, i.e. the
first step has magnitude `eta` regardless of gradient scale. With `eps = 1e-8` and
`|g| = 1e-6`, the first step is ~`eta` — enormous relative to the weights.

**AdamW** applies `w <- w - eta * lambda * w` directly, not through the `sqrt(v_hat)`
denominator. Under Adam, L2-in-loss becomes
`eta * lambda * w / sqrt(v_hat)`, which is *not* proportional to `w` and therefore not
weight decay.

## 9. Normalization Mathematics

**BatchNorm** for a channel over `n*H*W` values:

```
mu    = mean(x),   sigma^2 = var(x) (biased, /n)
x_hat = (x - mu) / sqrt(sigma^2 + eps)
y     = gamma x_hat + beta
```

Inference uses running estimates. The backward pass must include the dependency of
`mu` and `sigma^2` on `x`:

```
dx_hat = gamma * dx
dx = (1/std) * [ dx_hat - mean(dx_hat) - x_hat * mean(dx_hat * x_hat) ]
```

The last two terms are the cross-sample covariance contribution. Omitting them — the most
common hand-implementation error — still trains, but with wrong gradients.

**LayerNorm** over features `d`:

```
mu = (1/d) sum_j x_j,  sigma^2 = (1/d) sum_j (x_j - mu)^2
```

Independent of other samples in the batch. That independence is the property transformers
need, since sequence lengths and batch composition vary.

**RMSNorm**: `y = x / sqrt((1/d) sum_j x_j^2 + eps) * gamma`. One pass instead of two, no
mean subtraction — measurably faster in the transformer FFN/attention inner loops.

## 10. Residual Jacobian

For a residual block `y = x + F(x)`, `dy/dx = I + J_F`. For `L` stacked blocks,
`dy/dx = prod (I + J_F^l)`. If `||J_F|| < 1`, each factor's eigenvalues lie within a
disk centered at 1, so the product's singular values stay bounded away from both 0 and
infinity. Gradient flow is preserved to any depth — the precise statement of why
50-layer networks are trainable.

## 11. Weight Decay and Effective Learning Rate

Under SGD with L2, `w <- w - eta (g + 2 lambda w) = (1 - 2 eta lambda) w - eta g`.
Multiplicative shrinkage per step is `1 - 2 eta lambda`; over `T` steps:
`(1 - 2 eta lambda)^T ≈ e^{-2 eta lambda T}`. The decay timescale is
`1/(2 eta lambda)`, so **halving the learning rate doubles the effective decay time**.
That is why `weight_decay` values tuned at one learning rate do not transfer.

Under AdamW, shrinkage is `w <- (1 - eta lambda) w - eta * adam`, timescale `1/(eta lambda)`.

## 12. Quantization Error

Round a weight `w` to a grid of step `s`: `w_q = s * round(w/s)`, error `e = w - w_q`
uniform on `[-s/2, s/2]`.

```
E[e^2] = s^2 / 12
```

For symmetric per-tensor INT8, `s = max|w| / 127`. With weights ~ `N(0, 1/max(fan_in))`,
`s ~ 4/max(fan_in)/127`, so per-weight error variance `~ s^2/12`, and the accumulated
error over `fan_in` summed inputs has variance `fan_in * s^2/12`. Larger networks need
**per-channel** scales for this reason — a single outlier channel destroys a per-tensor
scale for every other channel.

## 13. Distillation Objective

Hard-label training minimizes `CE(y, p_s)`. Distillation adds the teacher's soft
distribution:

```
L = (1 - lambda) CE(y, p_s) + lambda T^2 * KL( softmax(z_t/T) || softmax(z_s/T) )
```

The `T^2` factor is not cosmetic: softmax entropies scale as `1/T`, so without it the
gradient magnitude shrinks as `T` grows. `T = 2` to `4` is typical.

Information argument: at `T -> 0` the softmax collapses to the argmax and the teacher's
"dark knowledge" — the relative probabilities among the wrong classes — is lost. Those
ratios carry most of the transferable signal.

## Worked Numbers

- **Vanishing gradient**: sigmoid net, 10 layers, `||W_l||_F = 1`, `phi' = 0.25` per layer.
  Gradient scale `~ 0.25^10 = 9.5e-7`. With tanh (`phi' ~ 0.8` typical) it is `0.8^10 =
  0.107` — 100,000x better. With ReLU and healthy init (half the units positive,
  `phi' = 1`), the decay is 1.0 — none.
- **Residual**: 20 blocks with `||J_F|| = 0.1`. Product of `(I + J_F)` has singular values
  between roughly `(1-0.1)^20 = 0.12` and `(1.1)^20 = 6.7`. Compare plain 20 layers at
  `0.25^20 = 9.1e-13`.
- **Xavier vs He** on a 64-unit ReLU layer: Xavier `Var(W) = 2/128 = 0.0156`, so output
  variance `= 64 * 0.0156 * 0.5 = 0.5` — halving per layer. He `Var(W) = 2/64 = 0.03125`,
  output variance `= 64 * 0.03125 * 0.5 = 1.0` — preserved. Over 20 layers Xavier leaves
  `0.5^20 = 1e-6`.
- **Adam first step**: `b1 = 0.9`, `b2 = 0.999`, `eta = 0.001`, `g = 0.01`.
  `m1 = 0.001`, `v1 = 1e-7`, `m_hat = 0.01`, `v_hat = 1e-4`, step `= 0.001 * 0.01/0.01 =
  0.001`. Without bias correction: `0.001 * 0.001/sqrt(1e-7) = 0.001 * 0.316 = 3.16e-4` —
  actually smaller here, but with `g = 1e-6` and `eps = 1e-8` the uncorrected step is
  `0.001 * 1e-7/1e-5 = 1e-5`, i.e. 10x the weight scale. The pathology appears when the
  gradient magnitude is comparable to or below `eps`.
- **INT8 quantization** on a 256-unit layer, weights `~ N(0, 1/256)`, `sigma = 0.0625`.
  Per-tensor `s = 4*0.0625/127 = 0.00197`, error variance `s^2/12 = 3.2e-7`.
  Summing 256 inputs: error variance `256 * 3.2e-7 = 8.2e-5`, std `0.0091` against a
  signal std of `sqrt(256)*0.0625 = 1.0` — a 0.9% relative error. With one outlier channel
  at `|w| = 10`, `s = 0.0315`, error std `0.0091`, and the relative error becomes 0.9% for
  *every* channel — 10x worse. Per-channel scales eliminate this.
- **Weight decay timescale**: SGD, `eta = 0.1`, `lambda = 1e-4`, 1000 steps per epoch.
  Decay time `1/(2*0.1*1e-4) = 50,000` steps = 50 epochs. At `eta = 0.05` it becomes 100
  epochs. The same `lambda` is half as strong at half the learning rate.

## Self-Check Questions

1. Derive the perceptron update bound `O((R/gamma)^2)`.
2. Compute the gradient scale for a 15-layer sigmoid net given `phi' = 0.2`.
3. Derive `dL/dz = p - y` for softmax cross-entropy.
4. Show that He init preserves activation variance under ReLU and Xavier does not.
5. Compute Adam's first-step magnitude with and without bias correction for `g = 1e-6`.
6. Write the BatchNorm backward pass including the covariance terms.
7. Derive the effective decay timescale for L2 under SGD and under AdamW.
8. Compute the relative output error from symmetric INT8 quantization for a 1024-unit
   layer with `weights ~ N(0, 1/1024)`, per-tensor versus per-channel scales.
9. Explain why `T^2` appears in the distillation loss.
10. Compute the eigenvalue bounds of a 30-block residual stack with `||J_F|| = 0.15`.
