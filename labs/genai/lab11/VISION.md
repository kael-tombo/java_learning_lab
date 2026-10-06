# Lab 11: Model Quantization & Deployment — Vision

## Where the Time Goes

```
DECODE, batch = 1                       PREFILL, 512 tokens
--------------------                    --------------------
  read 14 GB of weights                   512 parallel token passes
  BW = 3.3 TB/s  ->  4.2 ms               FLOPs = 2 * 7e9 * 512 = 7.2e12
  compute = 14 GFLOP                     FLOPs = 1e15  ->  7.2 ms
  compute time = 0.014 ms                 read weights once = 4.2 ms
                                           memory time = 4.2 ms
  => MEMORY BOUND by 300x                 => COMPUTE BOUND

  238 tok/s at b=1                        prefill of 512 tokens = 7.2 ms

as batch grows:
  b      compute      memory(+cache)   tokens/s   bound
  ------------------------------------------------------------
  1      0.014 ms     4.2 ms           238        memory
  8      0.11 ms      ~6 ms            1333       memory
  32     0.45 ms      ~15 ms           2133       memory
  64     0.90 ms      ~25 ms           2560       memory
  128    1.8 ms       ~45 ms            2844       memory
  256    3.6 ms       ~85 ms            3012       memory
  ------------------------------------------------------------
  b* for compute bound ~ FLOPS/BW/2 ~ 150
  => you will essentially never leave the memory-bound regime on one device
```

## Memory Composition

```
7B model, INT4 with group 64, 16-bit scales

  weights   7e9 * 4/8        = 3.500 GB   ====================================
  scales    7e9/64 * 2       = 0.219 GB   ===
                                        |
                                        v
  total                             3.719 GB   (0.531 bytes/param)

  with double quantization (8-bit scales):
  scales    7e9/64 * 1        = 0.109 GB
  second    7e9/64/256 * 2    = 0.0005 GB
  total                             3.610 GB   (0.515 bytes/param)

  vs FP16   7e9 * 2          = 14.000 GB

  compression 3.77x  (not 4x -- the scales are the tax)
  group 32 instead: scales double to 0.438 GB -> total 3.94 GB -> 3.55x
  => at 4 bits, group size matters a lot
```

## Quantization Granularity

```
weight matrix 4x4, one large value at (0,0) = 40, rest ~ N(0,1)

PER-TENSOR scale:  absmax = 40  ->  s = 40/7 = 5.71
  row 1: [7, 0, 1, -2] -> codes [1, 0, 0, 0]  -> recon [5.7, 0, 0, 0]
  MSE   ~ 1.0  (typical values crushed to zero)

PER-CHANNEL scale (one per row):
  row 0: absmax 40 -> still bad
  rows 1-3: absmax 2 -> s = 0.29 -> codes accurate
  MSE   ~ 0.08  (only the outlier row suffers)

PER-GROUP (group 4):
  every row self-contained -> MSE ~ 0.005

  cost: 1 scale per group
  per-channel for a d_out x d_in matrix = d_out scales vs d_out*d_in weights
  => overhead = 1/d_in  (~0.02% at d_in=4096) -- essentially FREE

  => always per-channel for weights. there is no reason not to.
```

## Codebook Comparison

```
weight distribution: N(0,1)

UNIFORM 4-bit over [-3, 3]  (16 equal bins, s = 0.375)
  bins: -3.00 -2.63 -2.25 -1.88 -1.50 -1.13 -0.75 -0.38 0  0.38 ...
        |__| |__| |__| ...
  most values near 0 land in the same bin -> coarse resolution where it matters
  MSE ~ 0.023

NF4 (quantiles of N(0,1)):
  -1.000 -0.696 -0.525 -0.395 -0.284 -0.185 -0.091 0.000
   0.080  0.161  0.246  0.338  0.441  0.563  0.723  1.000
        |_| |_|  |__|  |___| |____|
  fine near 0 (where mass is), coarse in the tails
  MSE ~ 0.0005

  16 levels either way. the difference is entirely WHERE they are placed.
```

## Optimal Clip Ratio

```
weight distribution: N(0,1), INT4

absmax from calibration n=4096  ->  ~3.7 sigma
MSE(3.7)  ~ 0.020

sweep the clip ratio:
  ratio   clip     MSE
  1.00    3.7σ     0.0200     <- plain absmax
  0.90    3.33σ    0.0155
  0.80    2.96σ    0.0102     <- optimum for 4-bit
  0.70    2.59σ    0.0180     <- too tight: clipping error dominates
  0.60    2.22σ    0.0340

INT8 optimum is looser (~0.95-1.0 of absmax) because more bins means
resolution is not the bottleneck.
=> SEARCH the clip ratio on calibration data. it is free at inference
   time and recovers real accuracy. absmax is a lazy default.
```

## Error Propagation

```
per-layer relative error eps, L layers

independent errors:      relative_error(L) ~ sqrt(L) * eps
                        sqrt(1)=1   sqrt(4)=2   sqrt(9)=3   sqrt(36)=6

correlated errors (rho):  ~ L * (1+rho)/(1-rho)
                        worst case:  L

measured (typical LLM):   between, closer to sqrt(L)

WHY QUANTIZATION WORKS AT ALL:
  - error grows slowly with depth (sqrt(L), not L)
  - residual connections give the network a correction path
  - normalization layers renormalize accumulated drift
  - training already has some tolerance to small perturbations

WHY SOME LAYERS BREAK FIRST:
  attention Q/K -> softmax amplifies error (exp of perturbed logits)
  LM head       -> directly sets the output distribution
  early layers   -> errors compound into every later layer
  => quantize the big tolerant tensors; keep the small sensitive ones in fp16
```

## Tensor Selection

```
7B model, parameter distribution (approximate)

  MLP gate/up/down      6.0e9  86%  -> QUANTIZE (uniform-ish, tolerant)
  attention q,k,v,o     1.0e9  14%  -> q,k: fp16 or fp8
                                          v,o: quantize
  embeddings            0.2e9   3%  -> fp16 (row-wise scales if quantized)
  LM head               0.2e9   3%  -> fp16 (tied to embeddings anyway)
  layer norms           0.02e9 <1%  -> NEVER quantize

  rule: quantize ~86% of params with near-zero risk
  the remaining 14% costs almost nothing to keep in fp16

  KV cache              varies  -> int8/fp8 for long context (Lab 12/13)
```

## Fused vs Naive Kernels

```
NAIVE: dequantize then matmul
  read  int4 weights          3.5 GB
  convert to fp16            write 14 GB   <-- extra traffic!
  read  fp16 weights          14 GB
  matmul
  total memory traffic      ~ 31.5 GB

FUSED: dequantize inside the matmul loop
  read  int4 weights          3.5 GB
  unpack into registers      0
  matmul
  total memory traffic        3.5 GB

  traffic ratio ~ 9x
  => 4x compression can yield ~9x speedup
  => the arithmetic added by unpacking is free while you are bandwidth-bound

  in Java this is measurable: NaiveDequantMatmul vs FusedMatmul
  and it is exactly why a "correct" Java port can still lose to fp16
```

## Calibration Mismatch

```
calibration set A (training-domain text):  activation max per channel ~ N(0,1), max 3.2
deployment traffic B (user documents):    activation max per channel, max 8.5

quantize with scales from A:
  deployment activations at 8.5 sigma
  code range capped at 7  ->  8.5 maps to 7, reconstructed as 7 * s
  relative error on the largest activations: ~18%

symptom:  perplexity fine on your eval set, bad in production
          "the model is weird sometimes" with no obvious cause

fix:      calibrate on deployment-representative traffic, re-calibrate when the
          traffic distribution shifts, alert on input drift (Lab 09)

=> the calibration bug is far more common than the bit-width bug.
```

## Throughput and Cost

```
7B, H100 @ $3/hour, fp16, seq 2048

  b      tokens/s    $ per 1k tokens
  1          238        0.0126
  8         1333        0.00225
  32        2133        0.00141
  64        2560        0.00117
  ----------------------------------------------------------------
  b=1 -> b=32:  9.0x cheaper
  fp16 -> int4 at b=32: ~4x cheaper
  combined: ~35x cheaper

  lesson: BATCHING FIRST, quantization second
  (quantization is what lets you afford the memory for batching)

capacity planning in terms of required batch size:
  KV cache for 32 concurrent x 2048 ctx = 32 * 1.07 GB = 34 GB
  that is half the device. batching competes with cache for the same memory.
  => there is a batching optimum, not "as much as possible"
```

## Queueing Reality

```
service rate mu (requests/s), arrival rate lambda

  stability requires  lambda < mu   (rho = lambda/mu < 1)

  rho    mean wait W
  0.5    2/mu
  0.8    5/mu
  0.9    10/mu
  0.99   100/mu
  1.0+   UNSTABLE, queue grows without bound

Little's Law: L = lambda * W
  at rho=0.9 with mu=10/s: W = 1/(10-9) = 1s, L = 9*1 = 9 requests queued

=> target rho <= 0.6 for acceptable tail latency
=> autoscaling on p95 latency needs headroom, not exact saturation
=> an LLM server that "handles peak load" at rho=0.99 does not handle peak load
```

## Prefill/Decode Disaggregation

```
  single pool (mixed):
    prefill request (512 tokens) blocks decode for 7 ms
    long prefill bursts destroy tail latency for everyone
    big cache allocation from prefill evicts decode sessions

  disaggregated:
    +--------------------+        +--------------------+
    | PREFILL POOL       |        | DECODE POOL        |
    | compute optimized  | -----> | bandwidth optimized|
    | TP high, 8 GPU     |  KV    | TP low, 1-2 GPU    |
    | handles bursts     |  cache | handles many seqs   |
    +--------------------+ transfer+--------------------+
                        |
              KV transfer cost is real:
              1.07 GB per 2048-token sequence at fp16
              ~= 0.3 ms at 3.3 TB/s (NVLink), much worse over a network

  => use disaggregation when prefill bursts are frequent and long.
     otherwise one pool with a prefill/decode priority scheduler is simpler
     and avoids the transfer cost entirely.
```

## Self-Check

- [ ] Per-channel scales on all weight matrices.
- [ ] Clip ratio searched, not hardcoded to absmax.
- [ ] Sensitive tensors (Q/K, LayerNorm, LM head) left in fp16.
- [ ] Fused dequant-matmul, not dequantize-then-multiply.
- [ ] Calibration data matches deployment traffic.
- [ ] Memory plan computed before choosing batch size.
- [ ] Utilization targeted below saturation for tail latency.