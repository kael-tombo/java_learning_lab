# neural-networks-deep — Theory

Track-level theory for the ten neural network modules: from the perceptron to model
compression. Each section states the mechanism, why it exists, and the failure it causes.

## 1. The Perceptron

```
y = step(w'x + b),  step(z) = 1 if z > 0 else 0
```

The perceptron convergence theorem: if the data is linearly separable and
`alpha > 0`, the algorithm converges in finitely many steps to *some* separating
hyperplane. The bound is `O((R/gamma)^2)` updates, where `R` bounds `||x||` and `gamma` is
the margin.

- **Limit**: XOR is not separable, so the perceptron cycles forever. This is the historical
  motivation for hidden layers, and it is why "just add more perceptrons" was the answer.
- Practical read: the theorem says nothing about speed or generalization. A large margin
  solution (SVM) generalizes better than a perceptron that happens to converge.
- The pocket algorithm (keep the best-weight-so-far on non-separable data) is the practical
  variant.

## 2. MLP and Backpropagation

A multilayer perceptron composes affine maps with elementwise nonlinearities:

```
h_l = phi(W_l h_{l-1} + b_l)
```

Backpropagation is the chain rule applied efficiently: the forward pass caches
intermediates, the backward pass reuses them, giving `O(L)` forward and backward cost for
`L` layers instead of `O(L^2)` from independent per-layer derivatives.

```
delta_l = (W_{l+1})' delta_{l+1} .* phi'(z_l)
grad W_l = delta_l h_{l-1}'
```

- **Vanishing gradient**: `prod_l W_l diag(phi'_l)`. With `|W| < 1` and `|phi'| < 1`, the
  product decays exponentially in depth. Sigmoid's `phi'` peaks at 1/4, so a 10-layer
  sigmoid net has a gradient scaled by ~1e-6 at the bottom.
- **Exploding gradient**: the mirror case; produces NaNs rather than slow learning, and
  is easier to spot and to clip.
- Fixes: ReLU (`phi' = 1` for positive inputs), residual connections, careful
  initialization, normalization.

## 3. Activation Functions

| Function | Formula | Note |
|----------|---------|------|
| Sigmoid | `1/(1+e^-x)` | Saturating, not zero-centred, `max phi' = 0.25` |
| Tanh | `(e^x-e^-x)/(e^x+e^-x)` | Zero-centred but still saturating |
| ReLU | `max(0,x)` | Non-saturating, cheap, dies at negative inputs |
| Leaky ReLU | `max(a x, x)` | `a=0.01`; fixes the dying-ReLU problem partly |
| ELU | `x` if `x>0` else `alpha(e^x-1)` | Negative mean, better convergence |
| SELU | scaled ELU | Self-normalizing with the right init |
| Swish | `x * sigmoid(beta x)` | Smooth, slightly better than ReLU |
| GELU | `x * Phi(x)` | The transformer default; smooth, gate-like |

- Choosing: ReLU-family for CNNs, GELU for transformers, sigmoid only on output layers
  for binary probability.
- Sigmoid's non-zero mean shifts gradients and slows convergence — a subtle but real tax.
- A dead ReLU (always negative input) gets zero gradient forever. Leaky variants and
  careful init reduce, not eliminate, this.

## 4. Loss Functions

- **MSE**: sensitive to outliers, penalizes small errors quadratically. Right for
  regression where errors are Gaussian.
- **MAE**: linear penalty, robust, but non-differentiable at 0 and constant-gradient
  (learns poorly at convergence).
- **Huber**: quadratic below a threshold, linear above. The standard compromise.
- **Cross-entropy**: for classification. The gradient against the logits is `p - y`,
  which is why training is stable.
- **Focal loss**: `(1-p_t)^gamma * CE`. Down-weights easy examples by `gamma`. For heavy
  class imbalance and dense detection.
- **Contrastive / triplet**: pull same-class pairs together, push different-class pairs
  apart, with a margin. The backbone of metric learning and retrieval.
- **Label smoothing**: `y = (1-eps) y + eps/K`. Prevents overconfident logits.

## 5. Regularization

- **L2 (weight decay)**: `+ lambda ||W||^2`. Shrinks uniformly; equivalent to a Gaussian
  prior. AdamW applies it **decoupled**, which is not the same as adding to the loss.
- **L1**: sparsity, for feature selection rather than performance.
- **Dropout**: inverted dropout scales activations by `1/(1-p)` during training so no
  scaling is needed at inference. Trains an implicit ensemble of subnetworks.
- **Batch normalization**: normalize per-channel over the batch, then affine. Makes
  gradients better conditioned and permits higher learning rates.
- **Early stopping**: stop when validation loss stops improving, with patience. Cheapest
  regularization available.
- Failure mode: **regularization without a validation set is just noise**. Every
  technique here needs a held-out signal, and the model selection must not touch test.

## 6. Weight Initialization

```
Xavier/Glorot: Var(W) = 2 / (fan_in + fan_out)
He (ReLU):     Var(W) = 2 / fan_in      (= Xavier for tanh's phi' variance)
LeCun:         Var(W) = 1 / fan_in
```

The derivation: to keep the variance of activations constant across layers, each layer
must preserve forward variance (`Var(W) * fan_in = 1`) **and** backward variance
(`Var(W) * fan_out = 1`). Satisfying both gives Xavier. ReLU halves the forward variance
(units are zeroed), so He doubles the gain.

- Zero init: symmetric neurons stay identical forever. The single most damaging bug.
- Orthogonal init: for recurrent networks, where the product of weights must not grow or
  decay exponentially over timesteps.

## 7. Optimizers

```
SGD:        w -= eta * g
Momentum:   v = mu v + g;        w -= eta v
Nesterov:   look ahead, then correct
AdaGrad:    accum += g^2;        w -= eta * g / (sqrt(accum) + eps)
RMSProp:    accum = rho*accum + (1-rho) g^2;  w -= eta g / (sqrt(accum)+eps)
Adam:       m, v with bias correction; w -= eta * m_hat / (sqrt(v_hat)+eps)
AdamW:      Adam plus decoupled decay
```

- The `eps` inside the denominator is a **bias-correction surrogate**: at step 1, `v_hat`
  is tiny, so without it the first update is enormous. Adam's `m_hat`, `v_hat` are the real
  fix; `eps` is numerical insurance.
- AdamW's decay is decoupled precisely because L2-in-loss becomes, under Adam's adaptive
  scaling, something other than weight decay.
- Generalization gap: adaptive methods often fit the training set better and generalize
  slightly worse on some tasks. It is empirical, not a law.
- Learning-rate schedule: warmup for transformers (avoids the early large-gradient
  shock), cosine decay afterwards.

## 8. Normalization Layers

| Layer | Normalizes over | Depends on batch size | Typical use |
|-------|----------------|----------------------|-------------|
| BatchNorm | batch and spatial, per channel | Yes | CNNs, large batches |
| LayerNorm | features within a sample | No | Transformers, RNNs, small batches |
| InstanceNorm | spatial per sample per channel | No | Style transfer, small batches |
| GroupNorm | channel groups per sample | No | Diffusion, small CNN batches |
| RMSNorm | features, no mean subtraction | No | Large LLMs, cheaper than LN |

- BatchNorm's train/eval discrepancy (running statistics vs batch statistics) is the
  classic bug: forgetting `.eval()` gives silently wrong inference.
- LayerNorm is invariant to batch composition, which is why transformers use it — variable
  sequence lengths and batch sizes must not change the activation scale.
- **Pre-norm vs post-norm**: pre-norm (`x + f(LN(x))`) trains far more stably at depth
  because the residual path is clean; post-norm requires careful warmup. Nearly all modern
  transformers use pre-norm, often with a final norm.

## 9. Advanced Architectures

- **Residual connections**: `y = F(x) + x`. Gradients flow through the identity path
  unchanged, which is what makes 50+ layers trainable. Effective gradient becomes
  `(I + J_F)`, so the Jacobian is closer to identity than to a vanishing product.
- **DenseNet**: every layer sees every prior feature; gradients and features are reused.
- **Inception**: parallel branches at multiple scales, concatenated.
- **SENet**: channel attention — a squeeze-and-excitation block that reweights channels
  from a global descriptor. Cheap and reliably additive.
- **ConvNeXt**: convolutions structured like transformers; evidence that the transformer
  block is not intrinsically necessary, only useful.
- Residual depth > width > more heads, generally, for a fixed compute budget.

## 10. Model Compression

| Method | What it does | Cost |
|--------|--------------|------|
| Pruning (unstructured) | Zero small weights | Sparse storage, dense compute unless sparse-aware |
| Pruning (structured) | Remove channels/heads/blocks | Retrain required |
| Quantization INT8/FP16 | Lower-precision weights and activations | Small accuracy loss, 2-4x memory and bandwidth |
| Knowledge distillation | Small student mimics a large teacher | Needs teacher logits, cheap student |
| Weight sharing | Reuse filters across positions | Only for like-for-like parameters |

- **Post-training vs quantization-aware training**: PTQ on a large model can be
  catastrophic without calibration data; QAT recovers most of the loss at the cost of
  training complexity. Always evaluate on real activation ranges.
- Distillation transfers a teacher's *dark knowledge* — the relative probabilities over
  wrong answers, which carry the most information. Hard-label training discards that.
- Compression is a trade, always measured on the task metric and never on model size
  alone. A 4x smaller model at 5 points worse accuracy is not a win.

## Cross-Cutting Judgement

1. **Debug in order**: shapes and data flow, then gradients (norm per layer, any zeros or
   NaNs), then the learning curve, then hyperparameters. Most "the model is not learning"
   reports are a shape or gradient-norm bug.
2. **Initialization and normalization are not optional.** They determine whether training
   is stable at all; learning rate is third.
3. **Measure before regularizing.** If the training loss is high, the problem is capacity
   or optimization, not overfitting.
4. **The residual/normalized/pre-norm combination is why deep transformers train.** Each
   element solves a specific gradient-path problem; removing one hurts more than expected.
