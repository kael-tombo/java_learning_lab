# Lab 11: Model Quantization & Deployment — Mini Project

## Project: Quantize and Deploy a Small Language Model with a Measured Latency Model

Implement the quantization stack and a serving scheduler in pure Java 21, then
produce a measured cost/latency model that justifies every configuration choice.

## Goal

A quantized model that is measurably faster per token than the fp32/fp16 baseline,
with an accuracy report per tensor type, a throughput model validated against
measurements, and a documented decision on what to ship.

## Requirements

### Phase 1: Numeric Formats
- [ ] fp32 <-> fp16 conversion handling normals, subnormals, Inf, NaN.
- [ ] Unit test over magnitudes `1e-8` to `1e8`; report max relative error.
- [ ] Format spec table generated from the code (bits/exp/mantissa).

### Phase 2: Quantizers
- [ ] Symmetric int8/int4: per-tensor, per-channel, per-group.
- [ ] Asymmetric int8 with zero points.
- [ ] NF4 codebook with per-block scales and optional double quantization.
- [ ] Accuracy report (MSE, max abs error, SNR in dB) per configuration.
- [ ] Round-trip tests: `dequant(quant(x))` within `scale/2`.

### Phase 3: Sensitivity Analysis
- [ ] Quantize each tensor group alone: attention Q/K, attention V/O, MLP,
      LayerNorm, embeddings, LM head.
- [ ] End-to-end loss impact per group.
- [ ] Produce a sensitivity table and a "what we quantize" decision.

### Phase 4: Better Quantization
- [ ] Optimal clip search over ratios 1.0 .. 0.7 on calibration data.
- [ ] GPTQ-style per-channel round-direction selection using an inverse-Hessian
      diagonal from calibration activations.
- [ ] SmoothQuant activation-outlier migration with an alpha sweep.
- [ ] Compare: RTN, clip-search, GPTQ, SmoothQuant+clip, all at 4 bits.

### Phase 5: Kernels
- [ ] `NaiveDequantMatmul` (dequantize to a float array, then multiply).
- [ ] `FusedMatmul` (unpack inside the accumulation loop).
- [ ] Microbenchmark both; report bytes touched and measured speedup.
- [ ] Explain why the fused version wins even in single-threaded Java.

### Phase 6: Graph Handling
- [ ] ONNX-like graph model (nodes, opset, typed IO) with JSON parse.
- [ ] Inspection: unsupported ops, dynamic axes, fusion candidates, dead nodes.
- [ ] Graph passes: constant folding, Conv+BN fusion, dead-node elimination.

### Phase 7: Serving Model
- [ ] `MemoryPlan` for the model across bit widths and group sizes.
- [ ] `ThroughputModel`: prefill time, decode time per token, batch sweep.
- [ ] KV cache accounting for the sequence lengths of interest.
- [ ] Queueing model: utilization vs mean wait; compute the stability threshold.
- [ ] Cost per 1k tokens per configuration.

### Phase 8: Scheduler
- [ ] A simple batching scheduler with a prefill/decode priority policy.
- [ ] Batch size selection accounting for cache memory pressure.
- [ ] Measure achieved throughput against the model's prediction.

### Phase 9: Calibration Sensitivity
- [ ] Calibrate on distribution A, evaluate on distribution B.
- [ ] Quantify the accuracy gap; re-calibrate on B; compare.
- [ ] Document the failure mode and the mitigation (drift alerting).

## Directory Layout

```
lab11/
  src/com/genai/lab11/{fp,quant,graph,kernel,deploy}/
  calib/dist_a.txt, dist_b.txt
  out/accuracy.csv
  out/throughput.csv
  out/sensitivity.csv
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — FP16 conversion passes all magnitude cases.
2. **M2** — four quantizer variants with accuracy reports.
3. **M3** — sensitivity table produced; decision recorded.
4. **M4** — clip search beats absmax measurably.
5. **M5** — GPTQ and SmoothQuant each improve over RTN at 4 bits.
6. **M6** — fused kernel measured faster than naive; traffic explained.
7. **M7** — graph inspection flags unsupported ops and dead nodes.
8. **M8** — throughput model within 20% of measured scheduler throughput.
9. **M9** — calibration mismatch quantified; drift mitigation documented.

## Acceptance Criteria

- [ ] Round-trip error within `scale/2` for all quantizers.
- [ ] NF4 MSE < uniform INT4 MSE at the same bit width.
- [ ] Clip search improves SNR over plain absmax by a stated margin.
- [ ] GPTQ improves over RTN at identical bits.
- [ ] Fused kernel touches at least 4x fewer bytes than naive.
- [ ] Sensitivity table identifies the tensors that must stay in fp16.
- [ ] Throughput model predicts measured throughput within 20%.
- [ ] Calibration distribution mismatch produces a measurable accuracy drop.

## Stretch Goals

- [ ] INT4 KV cache; measure accuracy at 1k / 4k / 16k context.
- [ ] Group-size frontier plot (32/64/128/256) with a marked knee.
- [ ] Quantization-aware training with a straight-through estimator.
- [ ] Weight-only INT4 vs full INT4 comparison.
- [ ] Split prefill/decode simulation with KV transfer cost.
- [ ] Autotuning harness measuring warmup cost.
- [ ] Mixture-of-experts routing cost model with quantized experts.
- [ ] Energy per token estimate from byte counts and device TDP.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| FP16 conversion wrong for subnormals | Implicit bit not restored |
| All-zero block decodes to garbage | `scale == 0` not guarded |
| Asymmetric worse than symmetric on ReLU data | Zero point computed from the wrong range |
| NF4 no better than uniform | Same codebook, or scale applied twice |
| Accuracy drop only in production | Calibration distribution mismatch |
| Fused kernel slower than naive | Too few inner iterations to amortize; or not actually fused |
| Throughput model wrong | Ignoring cache reads at long context |
| Dead nodes in the graph | Export bug (detached branch), not just unoptimized |
| OOM at high batch | Cache not accounted for in the batch cap |

## Definition of Done

`REPORT.md` contains: format table, accuracy tables for all quantizer
configurations, the sensitivity table, the clip-search and GPTQ/SmoothQuant
comparison, the kernel microbenchmark with a traffic explanation, the memory plan
table, the throughput model vs measurements, the utilization/queueing analysis, the
calibration mismatch experiment, and a "what we ship and why" section with the
accuracy/cost trade explicitly stated.