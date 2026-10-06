# Lab 11: Model Quantization & Deployment — Theory

## 1. Why Quantize

Model weights are `float32` by default. Inference memory and bandwidth are dominated
by weight reads, so halving the bytes per weight roughly halves decode latency.

```
float32:  4 bytes/param     fp16/bf16: 2 bytes     int8: 1 byte    int4: 0.5 byte
7B model: 28 GB              14 GB                 7 GB          3.5 GB
```

Second-order effects that matter more than people expect: bandwidth-bound decode gets
faster, cache pressure drops so more requests fit per device, and energy per token
falls. Quantization also reduces the compute spent moving data, which is why the
speedup is often larger than the compression ratio on decode.

## 2. Floating Point Formats

| Format | Bits | Exponent | Mantissa | Range | Notes |
|--------|------|----------|----------|-------|-------|
| FP32 | 32 | 8 | 23 | ~1e38 | Reference |
| TF32 | 19 (8/10 storage) | 8 | 10 | ~1e38 | Tensor-core matmul, lossy mantissa |
| BF16 | 16 | 8 | 7 | ~3e38 | Same range as FP32, low precision |
| FP16 | 16 | 5 | 10 | ~65504 | More mantissa, narrow range — overflow risk |
| FP8 E4M3 | 8 | 4 | 3 | ~448 | Used for activations |
| FP8 E5M2 | 8 | 5 | 2 | ~57344 | Used for gradients |
| INT8 | 8 | — | — | range-dependent | Symmetric or asymmetric |
| INT4 (NF4) | 4 | — | — | 16 levels | Non-uniform codebook |

**Why BF16 over FP16 for training**: same exponent width means the same dynamic
range, so no overflow, at half the mantissa precision. Why **FP16 for inference**:
10 mantissa bits give better precision and hardware support is universal; inference
does not need BF16's range because weights are already normalized.

## 3. Quantization Schemes

### Linear / affine

Given range `[xmin, xmax]` mapped to `[qmin, qmax]`:

```
s    = (xmax - xmin) / (qmax - qmin)
z    = round(qmin - xmin / s)            (asymmetric only)
q(x) = clamp(round(x/s) + z, qmin, qmax)
x_hat = s * (q(x) - z)
```

- **Symmetric** (`z = 0`): centered on zero. Good for zero-mean weights.
- **Asymmetric**: uses a zero point. Better when the range is offset (ReLU
  activations, all-positive tensors).

Error bound per element: `|x - x_hat| <= s/2`, so `MSE <= s^2/12`.

### Per-tensor vs per-channel vs per-block

| Granularity | Scales | Memory overhead | Accuracy |
|-----------|--------|-----------------|----------|
| Per-tensor | 1 | negligible | Worst — one outlier poisons everything |
| Per-channel (per output row) | out_features | tiny | Much better for weights |
| Per-group / per-block | groups | small | Best; NF4 uses block 64 |

Weight distributions have outliers in specific channels. Per-channel scaling is
essentially free for weights (one scale per output row) and recovers most of the loss.
Group size trades memory for accuracy; 64 is a common default for 4-bit.

## 4. Non-Uniform Codebooks (NF4)

NF4 places 16 levels at quantiles of a standard normal:

```
c_i = Phi^{-1}((i + 0.5) / 16),  i = 0..15
```

Weights are approximately normal, so non-uniform bins concentrate resolution where
the mass is. NF4 typically has 2-3x lower MSE than uniform 4-bit at the same bit
width. Double quantization additionally compresses the scale tensor itself, removing
an fp16 tensor that otherwise costs real memory.

## 5. Quantization Error Propagation

Quantizing a single linear layer perturbs the output by roughly the layer's relative
error. Across `L` sequential layers with independent relative error `eps`:

```
relative output error ~ sqrt(L) * eps      (random-walk model)
                       ~ L * eps           (worst case)
```

The square-root law is why 4-bit works at all for large models: error grows slowly
with depth, and residual connections plus normalization give the network opportunities
to correct small perturbations. Practically, **quantize more aggressively where it
matters less**: early layers and the LM head are more sensitive.

## 6. Which Tensors to Quantize

| Tensor | Quantize? | Why |
|--------|-----------|-----|
| Linear layer weights | Yes | Large, uniform-ish |
| Attention Q/K | Usually not (or FP8) | Very sensitive; softmax amplifies error |
| Attention V / output proj | Yes | Larger, more tolerant |
| MLP up/gate/down | Yes | Majority of parameters |
| LayerNorm weights | No | Tiny, and normalization is sensitive |
| Embeddings | Optional | Row-wise scales help; can be kept FP16 |
| LM head | Often kept higher precision | Directly determines logits |
| KV cache | Yes (FP8/INT8) | Large memory consumer during decode |

A useful rule: quantize the ~90% of parameters that live in MLP and attention output
projections, and leave the small, sensitive tensors alone.

## 7. Post-Training Quantization

```
Round-to-nearest (RTN):  s and z from min/max, then round. No data needed.
GPTQ:                    per-input-channel second-order error compensation.
AWQ:                    per-channel scaling by activation magnitude.
SmoothQuant:             migrate activation outliers into weights before quantizing.
Calibration:             run N samples to collect activation ranges (for asymmetric).
```

RTN is instant and the baseline. GPTQ and AWQ are a small one-time cost and
recover most of the gap. Calibration data must match the deployment distribution or
the ranges are wrong.

## 8. Quantization-Aware Training

QAT simulates quantization during training (fake-quant with straight-through
estimator) so the model adapts to its own quantization error. Best accuracy, highest
cost. Use when PTQ accuracy loss is unacceptable in a critical path.

## 9. Inference Kernels and Why They Matter

Naive Java dequant-then-compute reads and converts every weight on every token —
memory bandwidth is spent on int reads plus fp converts. Real kernels **fuse
dequantization into the matmul**, keeping weights in registers.

```
naive:  read int4 -> convert fp16 -> store -> matmul     (extra traffic)
fused:  read int4 -> dequant in register -> matmul        (single pass)

=> a theoretically 2x compression can give ~3x latency improvement
   because the bandwidth saved exceeds the arithmetic added
```

This is why a Java implementation can look correct and still be slower than fp16.

## 10. ONNX and Runtime Graphs

An ONNX model is a protobuf graph of operators with typed inputs and outputs. What
matters for deployment:

- **Opset version**: determines operator semantics; runtimes support up to an opset.
- **Dynamic axes**: symbolic dimensions (`batch`, `sequence`) require the runtime to
  handle varying shapes; `torch.export` helps produce fewer dynamic branches.
- **Graph optimizations**: constant folding, fusion (Conv+BN, MatMul+Add),
  dead-node elimination, layout transformation.
- **External data**: weights stored separately for models over the protobuf size limit.

Runtime backends (ONNX Runtime, TensorRT, OpenVINO) run several passes: graph
optimization -> constant folding -> kernel selection -> layout -> precision
assignment -> autotuning.

## 11. Deployment Shapes

| Shape | When | Notes |
|-------|------|-------|
| In-process library | Small models, low QPS, edge | No isolation; simplest |
| Dedicated server (GPU) | Most production LLM serving | vLLM/TGI/TensorRT-LLM style |
| Serverless | Spiky traffic | Cold start kills LLM serving; pre-warmed pools |
| Multi-tenant | Many adapters | One base, N adapters (Lab 06) |
| Split prefill/decode | Prefill and decode have different bottlenecks | Disaggregated serving |

Pre-fill is compute bound; decode is memory-bandwidth bound. They want different
hardware and different optimizations, which is the motivation for disaggregation.

## 12. Autotuning

Runtime autotuning benchmarks candidate kernels per layer shape and picks the fastest
on the actual device. Consequences:

- The same model file gives different performance on different GPUs.
- Warmup time before serving (measure it, or your p99 includes it).
- Tuning results should be cached and shipped with the deployment, not recomputed in
  production.

## 13. Quantization Selection Guide

```
need max quality, have the hardware      -> FP16/BF16
need memory reduction, quality tolerant  -> INT8 per-channel weights (PTQ)
need large model on limited device       -> INT4/INT8 (QLoRA-style, or AWQ/GPTQ)
need batch serving throughput            -> INT8/FP8 + fused kernels + continuous batching
training                                -> BF16 master weights, FP32 optimizer
```

## Key Equations

```
s = (xmax - xmin)/(qmax - qmin);  x_hat = s*(clamp(round(x/s)+z) - z)
MSE <= s^2/12
bytes/param = bits/8 + (bits_scale * (1/group) + bits_zp * (1/group))/8
deployed_bytes = params * (bits/8 + overhead_per_param)
relative error across L layers ~ sqrt(L) * eps
```