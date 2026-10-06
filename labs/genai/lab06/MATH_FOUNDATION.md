# Lab 06: Fine-Tuning with LoRA/QLoRA — Math Foundation

## 1. Rank and Parameter Count

`W in R^{d_out x d_in}` full rank is `min(d_out, d_in)`. A rank-`r` update has
`A in R^{r x d_in}`, `B in R^{d_out x r}`:

```
P_lora = r*d_in + r*d_out = r (d_in + d_out)
P_full = d_in * d_out
ratio  = r (d_in + d_out) / (d_in d_out) = r/d_in + r/d_out
```

For `d_in = d_out = 4096`: `ratio = 2r/4096 = r/2048`.
`r=16` -> `0.0078` (0.78%). `r=64` -> `0.031` (3.1%).

Note `ratio` depends only on `r/d` — doubling `d` halves the relative cost.

## 2. Initialization Property

At step 0, `B = 0` so

```
W = W0 + s * B A = W0
```

`W` is *identical* to the pretrained weight, so the initial model function is
unchanged. Formally, the loss surface starts at the pretrained point:

```
L(W(0)) = L(W0)
```

Gradients:

```
dL/dB = s * delta A^T        (nonzero if delta != 0)
dL/dA = s * B^T delta        (= 0 because B = 0)
```

`delta = dL/dY` is the upstream gradient at that layer. So on the first step only
`B` moves; `A` becomes active from step 2. This is expected, not a bug.

## 3. Error of the Low-Rank Approximation

If the true update is `Delta W` with singular values `sigma_1 >= ... >= sigma_p`, a
rank-`r` approximation captures the Frobenius norm:

```
||Delta W - Delta W_r||_F^2 = sum_{i=r+1}^{p} sigma_i^2
energy_retained = 1 - (tail energy / total energy)
```

Truncated SVD is the optimal rank-`r` approximation (Eckart-Young). LoRA learns
`B A` by gradient descent rather than SVD, so it can be worse than SVD at the same
rank — the practical argument for choosing `r` generously.

## 4. Scaling and Effective Learning Rate

Update to `W` after one SGD step:

```
dW_1 = W(1) - W(0) = -eta * s * B A     (full FT:  -eta * Delta W)
```

The gradient magnitude w.r.t. `B` scales with `s = alpha/r`, so `alpha` is
effectively an LR multiplier. That is why LoRA tolerates `1e-4`..`3e-4` while full
FT often uses `1e-5`..`1e-6`: the trainable subspace is tiny, so a large step is
still a small relative move.

`rsLoRA` uses `s = alpha / sqrt(r)` so increasing `r` does not silently shrink the
step size.

## 5. Gradient of the LoRA Path (Derivation)

Forward: `Y = X W0^T + s * (X A^T) B^T`

```
dL/dB = s * dY^T (X A^T)          in R^{d_out x r}
dL/dA = s * (dY^T B) X            in R^{r x d_in}
```

Memory note: `X A^T` is `(batch*seq) x r`, so the saved activation for backprop is
`r/d_in` of the base input — small. This is why LoRA's activation memory is
dominated by the frozen base path.

## 6. Quantization

Affine symmetric, `b` bits:

```
qmin = -2^{b-1},  qmax = 2^{b-1} - 1
s    = (xmax - xmin) / (qmax - qmin)
q(x) = clamp(round(x / s), qmin, qmax)
x_hat = s * q(x)
```

Rounding error is uniform in `[-s/2, s/2]`, so `E[(x - x_hat)^2] = s^2/12`:

```
MSE = s^2 / 12
```

Asymmetric adds `z`:

```
s = (xmax - xmin)/(qmax - qmin)
z = round(qmin - xmin/s)
x_hat = s * (clamp(round(x/s) + z, qmin, qmax) - z)
```

Improvement when the distribution is offset: symmetric wastes levels on one side.
For ReLU-ish activations (all non-negative, mostly near zero), asymmetry matters a
lot; for zero-mean Gaussian weights it barely does — which is why weight-only
symmetric quantization is common.

## 7. NF4 Codebook

NF4 places bin edges at quantiles of the standard normal:

```
c_i = Phi^{-1}( (i + 0.5) / 16 ),  i = 0..15
```

For a normal distribution, the optimal (Lloyd-Max) quantizer is non-uniform and
matches these quantiles; uniform 4-bit spacing is much worse. Expected MSE
reduction vs uniform 4-bit on Gaussian weights is roughly 2-3x.

Assignment: `i* = argmin_i |x/s - c_i|`; dequantization `x_hat = s * c_{i*}`.

## 8. Bytes per Element with Double Quantization

```
weights          4 bits = 0.5 bytes
scales           1 per 64 elements, 16-bit -> 16/64/8 = 0.03125 bytes
zero points      1 per 64, 16-bit  -> 0.03125 bytes (asymmetric)
quantized scales 1 per 256 elements, 8-bit -> 8/256/8 = 0.0039 bytes
total (symmetric, dq) ~= 0.5 + 0.031 + 0.004 = 0.535 bytes/element
```

For 7B: `7e9 * 0.535 = 3.75 GB`.

## 9. Training Memory Formula

```
M = W(bits/8)
  + P_train * bpg                       (gradients)
  + P_train * bpo * S                   (Adam m, v: bpo=4, S=2)
  + activations                         (0 with grad checkpointing)
  + P_full * (bits/8) for non-adapter fp32 master copy, if used
```

Worked example, 7B QLoRA r=16 on all linear layers (~20M trainable):

```
M = 3.5 GB (4-bit weights) + 0.22 GB (scales)
  + 20e6*2 (bf16 grads)          = 0.04 GB
  + 20e6*8 (fp32 Adam m+v)       = 0.16 GB
  + activations w/ checkpointing ~ 1.5 GB
  total ~ 5.4 GB
```

Same model at bf16 base: `7e9*2 = 14 GB` weights -> total ~15.9 GB. The base bit
width is the whole story.

## 10. Effective Rank of the Learned Update

Measure the update's true rank via its singular value spectrum:

```
participation_ratio = (sum sigma_i)^2 / sum sigma_i^2
```

If this is ~5 for `r = 64`, you are paying for 64 parameters of capacity to express
5 effective directions — prune (Exercise 14 Stretch C). Normalize singular values
to a probability vector and look at cumulative energy; keep the smallest `r'` with
`>= 99%` energy.

## 11. Fisher-Weighted Loss Increase (the original LoRA objective)

The paper's surrogate objective shows the full-FT loss increase is bounded:

```
max ||Delta W||_F <= sqrt(sum_i ((1-lambda_i)/lambda_i) * grad_i^T Delta W^T grad_i)
```

Intuition: directions with small Fisher information (flat loss landscape) can move
far without hurting. LoRA constraining `Delta W` to rank `r` and norm `alpha/r`
directly limits that term — the "low-rank + small norm" constraint *is* the
regularizer. That is why LoRA reduces catastrophic forgetting relative to full FT.

## 12. Expected Output Change from an Adapter

First-order effect of adding `s*B*A` at one layer:

```
Delta_y = X (s B A)^T = s * (X A^T) B^T
||Delta_y|| <= s * ||X A^T||_2 * ||B||_2
```

so the *input* energy projected onto the adapter's `r` read directions sets the
scale of change. If `||X A^T||` is tiny for your data, the adapter will appear to
do nothing — a real diagnosis for "trained but no effect".

## Self-Check Questions

1. Compute the LoRA parameter ratio for `d_in=8192, d_out=8192, r=32`.
2. Prove `L(W(0)) = L(W0)` given `B = 0`.
3. Derive `MSE = s^2/12` for uniform rounding error.
4. Compute total bytes for 13B at 4-bit with double quantization.
5. Given `||X A^T|| = 0.001` and `s = 2`, what does the second-order estimate say
   about output change?