# Lab 11: Model Quantization & Deployment — Math Foundation

## 1. Memory Accounting

```
deployed_bytes(params, b, group, s_bits, z_bits)
    = params * b/8
    + (params / group) * (s_bits + z_bits) / 8
```

Worked example, 7B, INT4 with group 64, 16-bit scales, no zero points:

```
weights = 7e9 * 4/8           = 3.50 GB
scales  = 7e9/64 * 16/8       = 0.219 GB
total                          = 3.72 GB   -> 0.531 bytes/param
```

With double quantization (8-bit scales):

```
scales  = 7e9/64 * 8/8        = 0.109 GB
second  = 7e9/64/256 * 16/8   = 0.0005 GB
total                          = 3.61 GB   -> 0.515 bytes/param
```

Compare FP16: `7e9*2 = 14 GB`. Compression ratio `3.9x`, not `4x` — the scales are
the tax. This is why group size matters at 4 bits: `group=32` doubles the scale
memory and erodes the advantage.

## 2. Quantization Error

Uniform rounding error `e = x - x_hat` is `U(-s/2, s/2)`:

```
E[e]    = 0
E[e^2]  = s^2/12
MSE      = s^2/12
```

For symmetric quantization of a zero-mean Gaussian tensor with std `sigma`, the range
is set by the max over `n` elements. For `n = 4096` samples, the expected max is
about `3.7 * sigma`:

```
s ~ 2 * 3.7*sigma / (qmax - qmin) = 7.4*sigma/255   (INT8)
MSE ~ (7.4*sigma/255)^2 / 12 = 7.1e-5 * sigma^2
SNR = sigma^2/MSE ~ 14000 -> ~41 dB
```

The clip factor `3.7` is the real cost: if you use `absmax` from a single outlier
channel at `8*sigma`, `MSE` grows by `(8/3.7)^2 = 4.7x`. That is the entire argument
for per-channel scales.

## 3. Optimal Clipping

Clipping trades clipping error against resolution. For a Gaussian, the optimal
clipping threshold minimizing total squared error is approximately

```
c* ~ 2.5 to 3.0 * sigma   for 8 bits
c* ~ 2.0 to 2.5 * sigma   for 4 bits (more aggressive; more bins needed)
```

Lower bits need tighter clipping because resolution per bin is scarcer. Approximate
optimal MSE at `c*`:

```
MSE_opt ~ sigma^2 * 2^(-2b) * k_b,     k_8 ~ 0.0035,  k_4 ~ 0.02
```

Practical consequence: implement an absmax search over candidate clip ratios (1.0,
0.95, 0.9, ...) minimizing calibration MSE rather than always using 1.0. That alone
is often worth a nontrivial accuracy recovery for free.

## 4. NF4 vs Uniform Codebook

For a standard normal, uniform 4-bit (16 bins over `[-c, c]`):

```
s_unif = 2c/16
MSE_unif ~ 2 * sigma^2 * s_unif^2 / 12 = sigma^2 * (2c/16)^2 / 6
```

With `c = 3` and `sigma = 1`: `s = 0.375`, `MSE ~ 0.0234`.

For NF4 (16 levels at normal quantiles) the optimal Lloyd-Max quantizer for 16 levels
has

```
MSE_NF4 ~ 0.00054 * sigma^2     (16-level Lloyd-Max, Gaussian source)
```

Ratio: `0.0234 / 0.00054 = 43x` — larger than the "2-3x" often quoted, because that
quote compares against uniform quantization over the *same effective range* while
including clipping effects. Either way, the direction is unambiguous: non-uniform
codebooks are dramatically better on approximately-normal data. Report the
comparison you actually ran rather than a remembered ratio.

## 5. Error Propagation

Model layer outputs as `y_l = y_{l-1} + eps_l` with `E[eps_l] = 0`,
`Var[eps_l] = sigma_e^2`:

```
Var[y_L] = Var[y_0] + L * sigma_e^2
relative_error ~ sqrt(L) * (sigma_e / |y|)
```

With correlation `rho` between adjacent errors:

```
sum_{i,j} rho^{|i-j|} = L + 2 * sum_{k=1}^{L-1} (L-k) rho^k
                       -> L * (1+rho)/(1-rho)   for large L
```

So positively correlated errors grow *linearly*, not as `sqrt(L)`. Empirical
measured growth usually sits between the two, closer to `sqrt(L)`. This matters
practically: architectures with strong residual coupling behave better under
quantization than the naive random-walk model predicts.

## 6. Prefill vs Decode Arithmetic

Prefill (compute bound), `N` tokens:

```
FLOPs ~ 2 * P * N          (P = parameters)
time_compute = 2*P*N / FLOPS
time_mem     = 2*P / BW     (read every weight once)
```

Decode, `b` concurrent sequences, 1 step:

```
FLOPs ~ 2 * P * b
time_compute = 2*P*b / FLOPS
time_mem     = (2*P + b * cache_bytes) / BW
```

Ratio for `P = 7e9`, FLOPS = 1e14, BW = 2e12 B/s, fp16 (`2*P = 14 GB`):

```
prefill  N=512:  compute = 7e12/1e14 = 0.070 s ; mem = 7 ms   -> COMPUTE
decode   b=1:    compute = 14e9/1e14 = 0.14 ms ; mem = 7 ms  -> MEMORY (50x)
decode   b=64:   compute = 9 ms            ; mem = 7 ms + cache
```

At `b = 64`, decode becomes compute bound. This is exactly why **batching is the
primary throughput lever**: at `b=1` you waste `FLOPS` capacity waiting on bandwidth.

Batching threshold: `b* = FLOPS / BW` roughly (balance the two terms) — with the
numbers above, `b* ~ 50`. Bigger batches stop helping once compute dominates.

## 7. Quantization Speedup Bound

If time is `max(compute, memory)`, and quantization reduces bytes by `r` while adding
arithmetic overhead `f`:

```
before: max(C, M)
after:  max(C*f, M/r)
speedup = max(C,M) / max(C*f, M/r)
```

If memory bound (`M >> C`): `speedup ~ r / (1 + small)`, so up to `r` (e.g. 4x at
INT4, or 8x vs INT32). If compute bound: `speedup ~ 1/f`, often *less than 1* — int4
unpacking can make it slower. This is why a fused kernel matters: it keeps `f` near 1.

## 8. Throughput Model

```
tokens_per_second = b * FLOPS / (2 * P)          when compute bound
                  = BW / (2*P)                     when memory bound
requests_per_sec  = tokens_per_second / avg_output_tokens
```

For a 7B fp16 model at `BW = 2e12`: `tokens/s = 2e12/14e9 = 143` at `b=1`. To hit
2,000 tokens/s you need `b >= 14` at minimum, and realistically `b ~ 40-60` to be
compute bound. Concretely: **plan capacity in terms of required batch size, not
tokens per request.**

## 9. Batch vs Latency

Decode is memory bound at low batch, so adding sequences is nearly free in latency:

```
latency_per_token(b) ~ max(2*P*b/FLOPS, (2*P + b*C)/BW)
```

From `b=1` to `b=32`, the memory term grows only by `32*C/BW` while compute stays
below memory for a long way. Result: per-token latency is nearly flat from 1 to ~32,
then rises linearly. Queueing is where latency explodes: if arrival rate exceeds
service rate, queue length grows without bound (M/M/1 behavior).

## 10. Queueing and Overload

Little's Law: `L = lambda * W` (average items in system = arrival rate * average
time in system).

```
stability requires rho = lambda / mu < 1
```

If `mu` is the service rate in requests/s and requests arrive at `lambda`, the system
is stable only when `rho < 1`. Operating at `rho = 0.9` gives mean wait
`W = 1/(mu - lambda) = 10/mu` — a 10x the service time. That is why latency-based
autoscaling needs headroom: **target `rho <= 0.6`** so tail latency stays acceptable.

## 11. Cost Model Per Token

```
cost_per_token = (hourly_gpu_cost * gpu_seconds_per_token) / 1e6
gpu_seconds_per_token = time_mem_bound                          (b=1)
                     = time_compute_bound / b                    (b large)
```

With `b = 32`, cost per token is up to `32x` lower than `b = 1` for the same
hardware. This is the single largest lever in LLM serving economics, ahead of
quantization.

## 12. KV Cache Memory (long context)

```
cache_bytes = 2 * layers * n_kv_heads * head_dim * seq_len * batch * bytes_per_elem
```

For 32 layers, 32 heads, 128 dim, `seq = 32k`, `batch = 8`, fp16:

```
= 2 * 32 * 4096 * 32768 * 8 * 2 = 137 GB      > H100 80GB
```

GQA (8 KV heads) cuts this to `34 GB`; INT8 cache to `17 GB`; sliding window
(`W = 4096`) to `4.3 GB`. Long context is fundamentally a **cache capacity** problem,
and the levers are architectural (GQA, sliding window, quantization), not clever
engineering.

## 13. Calibration Sample Efficiency

The clip threshold estimate from `n` samples has standard error

```
SE(absmax) ~ sigma / sqrt(n) * f(n)
```

With `n = 128` samples per channel, the absmax estimate is already stable for
8-bit; for 4-bit the tighter optimum means `n = 512` is often worth it. Calibration
cost is one forward pass per sample per quantized tensor group — negligible. The
failure mode is not too few samples; it is **the wrong distribution**.

## Worked Numbers

7B model, H100 at $3/hour, `BW = 3.3e12 B/s`, `FLOPS = 1e15` (fp16 with sparsity off).

- `b=1`: memory term `14e9/3.3e12 = 4.2 ms`; compute `14e9/1e15 = 0.014 ms`.
  Compute is negligible -> `4.2 ms/token`, `238 tok/s`.
- `b=32`: memory `4.2 ms + 32*cache`; cache at seq 2048 = `2*32*4096*2048*2 = 1.07 GB`,
  so `32*1.07e9/3.3e12 = 10.4 ms`; compute `0.45 ms`. Still memory bound: `14.6 ms/token`,
  but now `32*1000/14.6 = 2,192 tok/s`.
- `b=64`: compute `0.9 ms`, memory `25 ms`. Memory bound. `2,560 tok/s`.
- `b*` balance `= FLOPS/BW = 303`. Reaching compute bound needs batch ~300 — with
  2k-token sequences that is 600k tokens of KV cache. Memory bound is real.
- INT4 weights: memory term at `b=1` drops to `1.05 ms` -> `950 tok/s`. 4x.
- Cost at `b=32`, 2,192 tok/s: `3/2192 = $0.00137` per 1k tokens.
- Same model at `b=1`: `3/238 = $0.0126` per 1k tokens. **9.2x more expensive.**
- INT4 + `b=32`: `3/(32*950) = $0.000099` per 1k tokens.

Takeaway: batching gives ~9x, quantization gives ~4x. Do batching first; quantization
is a close second and often enables batching you could not otherwise afford.

## Self-Check Questions

1. Compute deployed bytes for 13B at INT4 with group 32 and 16-bit scales.
2. Derive why `absmax` from one outlier channel at `8*sigma` inflates MSE by `4.7x`.
3. Compute the optimal clip ratio implication for 4-bit vs 8-bit.
4. Derive `b* = FLOPS/BW` and evaluate it for the numbers above.
5. Explain why per-channel scaling is nearly free for a `d_out x d_in` matrix.