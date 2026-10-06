# Lab 06: Fine-Tuning with LoRA/QLoRA — Theory

## 1. Why Not Full Fine-Tuning

Full fine-tuning updates every weight. For a 7B model at bf16 that means:

```
trainable = 7e9 params
optimizer state (Adam m, v) = 2 * 7e9 * 4 bytes  = 56 GB
gradients                   = 7e9 * 2 bytes       = 14 GB
weights                     = 7e9 * 2 bytes       = 14 GB
total                       ~ 84 GB  + activations
```

One consumer GPU cannot hold that. Fine-tuning is also risky: catastrophic
forgetting, and most task knowledge lives in a few directions, not all of them.

## 2. The Low-Rank Hypothesis

LoRA's starting observation: the weight **update** for adaptation has low intrinsic
rank. If `W0` is frozen and the trained update is `Delta W`, then instead of
learning `Delta W in R^{d_out x d_in}` (rank up to `min(d_out,d_in)`), learn:

```
W = W0 + (alpha / r) * B A ,     A in R^{r x d_in},  B in R^{d_out x r}
```

`r << min(d_out, d_in)` (typical `r = 4..64`). Parameter count for the update:

```
LoRA params = r * (d_in + d_out)
vs full     = d_in * d_out
reduction   = r * (d_in + d_out) / (d_in * d_out)   -> ~0.1-1% for typical dims
```

For a 4096x4096 projection with r=16: 131,072 vs 16,777,216 params = **0.78%**.

## 3. Initialization Matters

- `A ~ N(0, sigma^2)` (Kaiming uniform, small), random.
- `B = 0`.

Then `BA = 0` at step 0, so `W = W0` exactly: the adapted model *starts* as the
pretrained model. This is a correctness property, not a convenience — without it the
model begins randomly perturbed.

Gradients: `dL/dB = delta * A^T * (alpha/r)` is nonzero at init, while
`dL/dA = B^T * delta * (alpha/r)` is **zero** (because `B = 0`). So A stays put on
step 1 and B starts moving; training proceeds from there. This asymmetry trips up
people who expect both matrices to change immediately.

## 4. Scaling: alpha / r

```
W = W0 + scaling * B A ,   scaling = alpha / r
```

`alpha` sets the effective learning rate on the update. Common: `alpha = r` giving
`scaling = 1`, or `alpha = 2r` (scaling 2). With `rsLoRA`, the scaling becomes
`alpha / sqrt(r)`, which decouples the learning rate from the rank — useful when
sweeping `r`.

## 5. Target Modules

LoRA is not applied to every matrix. Standard targets: the attention projections
`q_proj`, `k_proj`, `v_proj`, `o_proj` and the MLP `gate_proj`, `up_proj`,
`down_proj`. Embeddings and the LM head are normally left frozen (or handled by
separate methods). Attaching to all linear layers is the safest default if unsure.

## 6. Merging Weights

After training, the adapters fold into the base weights:

```
W_merged = W0 + scaling * B A
```

Merging costs one matmul per target module and produces a standalone checkpoint —
no adapter loading at inference. Why keep adapters separate? Cheap weight swapping
(multi-tenant serving), instant rollback, and no base-weight duplication.

## 7. QLoRA: 4-bit Base Weights

QLoRA adds three ideas:

1. **NF4** — a 4-bit NormalFloat data type whose bin edges are the quantiles of a
   standard normal distribution, so values cluster where the distribution is dense.
2. **Double quantization** — quantize the per-block absmax scale constants too,
   removing a fp16 scale tensor that would otherwise cost real memory.
3. **Paged optimizers** — memory spikes during gradient checkpointing cause
   fragmentation; page-wise allocation defers optimizer state to unified memory.

Rough memory for a 4-bit 7B model:

```
weights      7e9 * 0.5 bytes          = 3.5 GB
scales       (blocksize=64) ~ 7e9/64 * 2 bytes = 0.22 GB
LoRA params  (r=16 on all linears) ~ 20M * (2 grad + 8 optim) bytes = 0.2 GB
activations  small (grad checkpointing) = ~1-2 GB
total                                     ~ 6 GB
```

That is the whole point: a 7B model trains on a single 24 GB card.

## 8. Quantization Math

Affine (symmetric) quantization to `b` bits:

```
q(x) = clamp(round(x / s), qmin, qmax),   s = (xmax - xmin) / (qmax - qmin)
x_hat = s * q(x)
```

Per-block scaling (NF4 uses blocksize 64) keeps error low because each block fits
its own range. Error analysis:

```
||x - x_hat|| <= s/2  per element   (rounding is the dominant term)
relative error ~ s / std(x)
```

Asymmetric quantization adds a zero-point `z` and uses
`s = (xmax - xmin)/(qmax - qmin)` with `q = round(x/s) + z` — better when the data
range is offset from zero.

## 9. Memory Math for a Fine-Tune

```
total = W(bits/8) + grads(trainable * bpg) + optim(trainable * bytesPerState * states)
      + activations(grad checkpointing) + base overhead
```

Peak-memory levers, in order of impact:
1. Base weight bits (16 -> 4): ~7x reduction.
2. LoRA rank `r` (linear in trainable params).
3. Gradient checkpointing (trades compute for activation memory).
4. Sequence length and batch size.

## 10. Data and Hyperparameters

- **Dataset size**: rank-stabilized data — a few hundred to a few thousand
  high-quality examples usually beats a large noisy set.
- **LoRA target modules**: attention-only underfits for style/format tasks; include
  MLP for those.
- **Learning rate**: LoRA tolerates ~10x higher LR than full fine-tuning
  (1e-4 to 3e-4 typical). AdamW with weight decay on non-LoRA params only.
- **Epochs**: 1-3. More epochs on a small set memorizes fast.
- **Masking**: mask the prompt tokens out of the loss when training chat models —
  otherwise you are training the model to reproduce user turns.
- **Eval**: hold out 5-10%; compare against the base model, not against zero.

## 11. Practical Failure Modes

| Symptom | Cause |
|---------|-------|
| Loss starts higher than base model | Bad init (`B != 0`), or LR far too high |
| Adapter has no effect at inference | Not merged, or `scaling` mismatch |
| Output is a verbatim copy of inputs | Loss not masked on prompt tokens |
| Degrades general ability | Overfitting small set, or missing KL regularization |
| `B` gradient is zero and never recovers | Custom optimizer or weight decay on `B` |
| Memory blows up at eval | `use_cache` off / checkpoint not loaded correctly |

## 12. Choosing a Method

| Method | Params trained | Memory | Use when |
|--------|----------------|--------|----------|
| Full FT | all | very high | You have the hardware and need broad change |
| LoRA | ~0.1-1% | moderate | Default choice for most adaptation |
| QLoRA | ~0.1-1% | low | Single GPU, larger models |
| Prefix/prompt tuning | ~0.01% | tiny | Very narrow tasks, many tenants |
| DoRA | ~0.1-1% | moderate | Margin-based tuning quality (Lab 06 stretch) |
| Adapter/prompt caching | 0 (inference) | free | Many tenants, no training budget |

Rule of thumb: **LoRA first**. Move to full FT only when you have evidence that
adapter capacity is the binding constraint.

## Key Equations

```
W = W0 + (alpha/r) * B A
LoRA params  = r (d_in + d_out)
scale to 4-bit:  s = (xmax - xmin)/(qmax - qmin)
train memory = W(bits/8) + P_train*(bpg + bpo*S) + activations
```