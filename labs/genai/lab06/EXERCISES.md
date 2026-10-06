# Lab 06: Fine-Tuning with LoRA/QLoRA — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Low-Rank Update Forward Pass (E)

Implement `double[] loraForward(double[] x, double[][] A, double[][] B, double scaling)`
computing `x' = x @ A^T @ B^T * scaling` for a single vector.

**Verify**: with `B = 0`, output is all zeros (so `W = W0` exactly).

---

## Exercise 2: Parameter Counting (E)

Given shapes and ranks, compute trainable vs total parameters and the ratio for
attention-only and attention+MLP targets on a 4096-dim, 32-layer model at r=4, 8, 16, 64.

**Expected**: r=16 gives roughly 0.5-1% of total params.

---

## Exercise 3: Initialization and First Step (M)

Implement `initLora(dIn, dOut, r, seed)` with Kaiming-uniform `A` and zero `B`.
Compute gradients of a small MSE loss w.r.t. `A` and `B` with a hand-rolled
backprop, and verify `dL/dA == 0` at step 0 while `dL/dB != 0`.

**Expected**: this asymmetry is the documented initialization property.

---

## Exercise 4: Merging Weights (M)

Implement `double[][] merge(double[][] W0, double[][] A, double[][] B, double scaling)`
and prove equivalence: `merge(W0, A, B, s)` applied as a linear layer equals
`W0` layer followed by the LoRA path with the same `s`.

**Verify**: max abs difference < 1e-12.

---

## Exercise 5: Weight Decay Exclusion (M)

Implement an AdamW step that applies decoupled weight decay to all params **except**
LoRA `B` (or `A`, your choice) and verify a few steps still reduce loss.

**Expected**: decaying `B` fights the zero-init and slows early learning.

---

## Exercise 6: Rank Sweep (M)

Train the mini model (Exercise 3) at r = 1, 2, 4, 8, 16 on the same data for the
same steps. Plot validation loss vs r.

**Expected**: improvement saturates quickly; r=1 often captures most of the gain.

---

## Exercise 7: Alpha Sweep (M)

With r fixed at 8, sweep alpha in `{1, 2, 8, 16, 32}` and report validation loss and
gradient norm.

**Expected**: effective LR scales with `alpha/r`; too large destabilizes.

---

## Exercise 8: Symmetric vs Asymmetric INT8 Quantization (M)

Implement both quantizers for a weight tensor. Report mean squared error and max
abs error, and reconstruct with dequantization.

**Expected**: asymmetric wins when the data range is offset from zero.

---

## Exercise 9: NF4 Codebook Construction (H)

Implement NF4 quantiles: build a standard normal CDF, invert it at levels
`[-1, -0.6961928009986877, -0.5250730514526367, -0.39491748809814453,
-0.28444138169288635, -0.18477343022823334, -0.09105003625154495, 0, ...]`-style
values derived from the inverse CDF, then assign each weight to the nearest level.
Report reconstruction error versus a uniform 4-bit quantizer.

**Expected**: NF4 has lower MSE for normally distributed weights.

---

## Exercise 10: Per-Block Scales and Double Quantization (H)

Implement blocksize-64 quantization: one scale per block. Then quantize the scale
tensor itself to 8 bits with a second-level scale. Compute total bytes/element for
both schemes.

**Verify**: 4-bit NF4 + double quant < 0.6 bytes/element.

---

## Exercise 11: Memory Budget Calculator (M)

Write `MemoryPlan.of(params, bits, trainableParams, gradCheckpointing, seqLen, batch)`
returning weights/grads/optimizer/activation bytes and whether it fits a given
device.

**Verify**: a 7B 4-bit QLoRA plan fits 24 GB and a 7B 16-bit LoRA plan does not fit 24 GB.

---

## Exercise 12: Prompt Masking for Chat Data (M)

Build a chat dataset with a loss mask that is 1 only on assistant tokens. Compute
loss over masked positions only.

**Verify**: changing a user token does not change the loss; changing an assistant
token does.

---

## Exercise 13: Adapter Registry and Hot-Swapping (M)

Implement `AdapterRegistry` storing named `A`,`B` pairs per target module, with
`activate(name)`, `save()`, `load()`. Serve two adapters alternately through one base
model and assert outputs differ.

**Verify**: no base weights are duplicated per adapter.

---

## Exercise 14: Base vs Adapter Quality Comparison (M)

Evaluate the base model and the merged adapter model on the held-out set. Report
exact-match and mean token accuracy.

**Expected**: adapter strictly better on the target format, comparable elsewhere.

---

## Stretch A: rsLoRA Scaling (H)

Implement `alpha / sqrt(r)` scaling and re-run the rank sweep from Exercise 6.
Compare against `alpha / r`.

**Expected**: rsLoRA decouples rank from effective LR, so larger r does not require
re-tuning alpha.

---

## Stretch B: DoRA-Style Magnitude Decomposition (H)

Implement DoRA: decompose the adapted weight into direction
`(W0 + BA)/||W0 + BA||` and a learned magnitude vector `m`, then apply
`m * direction` per output row. Train `m` alongside `A` and `B` and compare against
plain LoRA at matched trainable-parameter budgets.

---

## Stretch C: Pruning the Adapter (H)

After training, rank the LoRA update's singular values and prune to the smallest
rank that preserves >99% of the update's Frobenius energy.

**Verify**: report energy retained vs rank, and validation loss after pruning.