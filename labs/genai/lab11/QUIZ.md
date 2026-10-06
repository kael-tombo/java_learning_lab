# Lab 11: Model Quantization & Deployment — Quiz

**Q1.** The main reason quantization speeds up LLM decode is...
- a) Fewer arithmetic operations per token
- b) Fewer bytes read per token, since decode is memory-bandwidth bound
- c) Better model accuracy allowing shorter outputs
- d) Smaller network latency

**Q2.** Bytes per parameter at INT8 is...
- a) 1
- b) 2
- c) 4
- d) 0.5

**Q3.** BF16 is preferred over FP16 for training because it has...
- a) More mantissa bits
- b) The same exponent range as FP32, avoiding overflow
- c) Fewer bits total
- d) Better int8 conversion

**Q4.** For a linear quantizer, the maximum per-element error is bounded by...
- a) `scale`
- b) `scale/2`
- c) `scale^2`
- d) `2*scale`

**Q5.** Symmetric quantization loses accuracy primarily when the tensor's values...
- a) Are near zero
- b) Have a range offset from zero
- c) Are integers
- d) Have outliers in specific channels

**Q6.** Per-channel quantization is nearly free for weights because it needs...
- a) One scale per input channel only
- b) One scale per output row, which is negligible relative to the matrix
- c) No scales at all
- d) One scale per element

**Q7.** NF4's advantage over uniform 4-bit comes from...
- a) Using more bits
- b) Placing levels at normal-distribution quantiles
- c) Using symmetric scaling
- d) Skipping the zero level

**Q8.** Double quantization in QLoRA compresses...
- a) The quantized weights a second time
- b) The per-block scale constants
- c) The optimizer state
- d) The activations

**Q9.** If per-layer relative error is `eps`, output error across `L` layers grows
roughly as...
- a) `L * eps`
- b) `sqrt(L) * eps`
- c) `log(L) * eps`
- d) `eps / L`

**Q10.** The square-root growth law is possible because...
- a) Layers are trained with quantization noise
- b) Errors are roughly independent and residual/normalization layers correct small
     perturbations
- c) Quantization is exact for large tensors
- d) Deeper models have smaller errors

**Q11.** Which tensors are usually NOT quantized because of sensitivity?
- a) MLP up/down
- b) Attention Q/K, LayerNorm, often the LM head
- c) Embeddings only
- d) All of them

**Q12.** Round-to-nearest quantization requires...
- a) A calibration set
- b) Only min/max statistics from the weights
- c) Gradient information
- d) A second model

**Q13.** GPTQ improves on RTN by...
- a) Using more bits
- b) Second-order error compensation using calibration statistics
- c) Using FP16 compute
- d) Training longer

**Q14.** SmoothQuant works by...
- a) Smoothing the loss landscape
- b) Migrating activation outliers into weights before quantizing
- c) Averaging adjacent layers
- d) Increasing group size

**Q15.** A fused dequant-matmul kernel is faster mainly because it...
- a) Uses more threads
- b) Avoids materializing dequantized weights, reducing memory traffic
- c) Skips the quantization step
- d) Uses lower precision outputs

**Q16.** A fused INT4 kernel can exceed the 2x compression ratio in speedup because...
- a) Arithmetic is free
- b) Bandwidth saved exceeds the arithmetic added
- c) The model is smaller
- d) Batch size increases

**Q17.** In ONNX, an opset version determines...
- a) The model size
- b) Operator semantics and which runtime supports it
- c) The number of layers
- d) The batch size

**Q18.** A dynamic axis in an ONNX graph means...
- a) The model is quantized
- b) A symbolic dimension the runtime must handle at varying sizes
- c) The weights are external
- d) The graph is unsupported

**Q19.** Runtime autotuning benchmarks candidate kernels, which means...
- a) Performance is identical across GPUs
- b) The same model file performs differently per device and needs warmup
- c) Warmup is free
- d) Kernels are chosen statically

**Q20.** Pre-fill is compute bound while decode is bandwidth bound, which motivates...
- a) Using the same hardware for both
- b) Disaggregated serving with separate prefill and decode pools
- c) Disabling prefill
- d) Larger batches only for prefill

**Q21.** Calibration data that does not match deployment traffic causes...
- a) No effect
- b) Wrong activation ranges and degraded accuracy
- c) Faster inference
- d) Smaller models

**Q22.** Quantization-aware training with a straight-through estimator exists because...
- a) It is faster than PTQ
- b) PTQ error cannot be corrected post-hoc in some models
- c) It needs no data
- d) It produces smaller files

**Q23.** KV cache quantization mainly reduces...
- a) Weight memory
- b) Memory per sequence during long-context decode
- c) Arithmetic
- d) Token count

**Q24.** Weight-only INT4 (FP16 activations) is preferred in practice because...
- a) INT4 matmul is fast on no hardware
- b) It retains nearly all quality while capturing most of the memory win
- c) It uses fewer kernels
- d) It requires no scales

---

## Answers

1. **b** — decode rereads all weights each token; halving bytes halves the wait.
2. **b** — 8 bits = 1 byte.
3. **b** — FP16's 5 exponent bits overflow on large magnitudes.
4. **b** — rounding to the nearest grid point.
5. **b** — a zero point is needed to shift the range.
6. **b** — `out_features` scales against `d_in * d_out` entries is negligible.
7. **b** — resolution concentrates where weight mass lives.
8. **b** — quantizing the fp16 scales to 8 bits.
9. **b** — independent perturbations accumulate as a random walk.
10. **b** — plus residual paths and normalization giving correction opportunities.
11. **b** — small, sensitive tensors are not worth the risk.
12. **b** — min/max from the weights themselves.
13. **b** — solves for rounded weights minimizing output error.
14. **b** — rescales activation channels so their maxima drop.
15. **b** — keeps weights in registers instead of writing fp16 copies.
16. **b** — bandwidth is the bottleneck, so saving it dominates added arithmetic.
17. **b** — runtimes cap at a supported opset.
18. **b** — symbolic `batch`/`sequence` dimensions.
19. **b** — tuning results are device-specific and cost warmup time.
20. **b** — different bottlenecks want different hardware and pools.
21. **b** — ranges come from observed activations.
22. **b** — the model must adapt to its own quantization error.
23. **b** — the cache grows with sequence length times layers times heads.
24. **b** — full INT4 compute needs specialized hardware.

## Score Guide

22-24: ready for Lab 12 (cost) and ai-engineering lab01/lab10.
16-21: redo Exercises 6, 9, 13.
0-15: reread THEORY sections 2-9.