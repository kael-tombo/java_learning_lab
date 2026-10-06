# Lab 11: Model Quantization & Deployment — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: FP32 to FP16 Round-Trip (E)

Implement fp32 -> fp16 (with overflow saturation) -> fp32 and measure max relative
error on a set of magnitudes from `1e-8` to `1e8`.

**Expected**: catastrophic relative error above ~65504 (inf) and near `1e-5` (denormal
region relative to mantissa).

---

## Exercise 2: Symmetric INT8 Quantizer (E)

Per-tensor symmetric: compute `absmax`, `scale`, quantize with clamping, dequantize.
Report MSE and max abs error.

**Verify**: `dequant(quant(x))` reconstructs within `scale/2`.

---

## Exercise 3: Asymmetric INT8 Quantizer (M)

Add a zero point. Compare MSE against symmetric on a tensor with a skewed range
(e.g. all-positive activations).

**Expected**: asymmetric wins clearly on offset data, roughly ties on zero-mean data.

---

## Exercise 4: Per-Channel Quantization (M)

Quantize each output row of a weight matrix independently. Compare MSE to per-tensor.

**Expected**: a large improvement, at negligible overhead (one scale per row).

---

## Exercise 5: Per-Group Quantization Sweep (M)

Sweep group size 32, 64, 128, 256. Report MSE and bytes/element.

**Expected**: monotone tradeoff; 64 is a common knee.

---

## Exercise 6: Outlier Sensitivity (M)

Construct a weight matrix with one large outlier channel. Show per-tensor MSE explodes
while per-channel MSE barely moves.

**Verify**: this is the empirical justification for per-channel scales.

---

## Exercise 7: NF4 Codebook and Error (H)

Build the NF4 codebook from normal quantiles, implement encode/decode with per-block
scales, and compare MSE against uniform INT4 at the same bit width.

**Expected**: NF4 MSE roughly 2-3x lower.

---

## Exercise 8: Double Quantization (H)

Quantize the scale tensor to 8 bits with a second-level scale. Compute bytes/element
before and after.

**Expected**: 4-bit NF4 total ~0.535 bytes/element.

---

## Exercise 9: Error Propagation Across Layers (M)

Quantize weights layer by layer in a small model and measure output relative error vs
`sqrt(L)` and `L` models.

**Expected**: closer to `sqrt(L)`.

---

## Exercise 10: Sensitivity Map by Tensor Type (H)

Quantize each tensor group (attention Q/K, attention V/O, MLP, LayerNorm, LM head,
embeddings) individually and measure end-to-end loss impact.

**Expected**: Q/K and LM head most sensitive; MLP least.

---

## Exercise 11: GPTQ-Style Error Compensation (H)

Implement per-input-channel second-order correction: using a calibration set, solve a
small least-squares problem per output channel to choose rounded weights minimizing
output error.

**Expected**: lower MSE than round-to-nearest at identical bit width.

---

## Exercise 12: SmoothQuant Migration (H)

Compute per-channel activation maxima, then migrate a fraction `alpha` of activation
outliers into the weights (`W' = W * S^-1`, `X' = X * S`) and quantize both.

**Verify**: activation max shrinks by `1/(1-alpha)` factor while weights grow slightly;
net activation quantization error drops.

---

## Exercise 13: Fused Dequant-Matmul Microbenchmark (M)

Compare (a) naive dequantize-then-matmul against (b) dequantize fused into the matmul
loop, measuring bytes touched. Report the theoretical and measured speedup.

**Expected**: fused touches 4x fewer bytes at INT4.

---

## Exercise 14: ONNX Graph Inspection (M)

Parse a small ONNX-like protobuf (or a JSON stand-in) graph: list nodes, opset
version, input/output shapes, identify dynamic axes, detect unsupported operators.

**Verify**: correctly flags at least one unsupported op and one dynamic axis.

---

## Exercise 15: Bytes/Param Accounting for Real Models (E)

Compute total deployment bytes for 7B/13B/70B at FP16, INT8, INT4-NF4, INT4+GPTQ
(INT8 scale), including embedding and LM head handling.

---

## Exercise 16: Prefill vs Decode Kernel Profile (M)

Instrument a synthetic model: measure time per token in prefill and decode, and
attribute to weight reads vs cache reads.

**Expected**: decode dominated by weight reads; at long context cache reads catch up.

---

## Exercise 17: Autotuning Warmup Cost (H)

Benchmark N kernel variants per layer shape; report total autotune time and the
resulting per-shape best. Show the value of caching tuning results.

---

## Exercise 18: Split Prefill/Decode Analysis (M)

Model prefill and decode throughput separately and compute the utilization loss from
mixing them in one engine at different batch sizes.

---

## Stretch A: Quantization-Aware Training (H)

Add fake-quant with a straight-through estimator to a small training loop and compare
against PTQ on the same data.

---

## Stretch B: KV Cache Quantization (H)

Quantize the KV cache to INT8/FP8 per-head with per-head scales. Measure accuracy
impact at long context and memory saved.

**Expected**: small accuracy loss up to ~4k tokens; growing at very long context.

---

## Stretch C: INT4 Weight-Only Kernels vs Full INT4 (H)

Compare 4-bit weights with FP16 activations (weight-only, the common practical choice)
against fully INT4 compute.

**Expected**: weight-only retains nearly all quality with most of the memory win.

---

## Stretch D: INT4 Group Size vs Accuracy Frontier (M)

Plot accuracy against bits/param for group sizes 32-256. Mark the knee for your
model.

---

## Stretch E: Quantization Robustness Under Distribution Shift (H)

Quantize on calibration data from distribution A, then evaluate on distribution B.
Measure the accuracy gap against calibration from B.

**Expected**: mismatch costs accuracy — a common and underappreciated bug.