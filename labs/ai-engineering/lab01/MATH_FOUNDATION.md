# Lab 01: LLM Serving Infrastructure — Math Foundation

## 1. Prefill Time

For `P` parameters and `n` prompt tokens, forward-pass FLOPs are approximately:

```
FLOPs ~ 2 * P * n
```

plus attention, which for `n` tokens and `d` hidden size is `~ 4 * n^2 * d` per layer
(summed over layers: `~ 4 * n^2 * d_model`).

```
t_prefill = max( 2*P*n / FLOPS ,  2*P / BW + 4*n^2*d / FLOPS )
```

Worked example (7B, `d = 4096`, 300 TFLOP/s, 3 TB/s):

- `n = 500`: `2*7e9*500/3e14 = 23 ms`; attention `4*500^2*4096/3e14 = 13.7 ms`
  (per layer this should be summed; for 32 layers it is `~ 0.44 s`, so the FFN term
  dominates at this length).
- `n = 4096`: attention grows 67x; prefill becomes seconds.

**Conclusion: prefill is compute bound and roughly linear in `n` until the quadratic
attention term dominates at `n ~ d_model`.**

## 2. Decode Time Per Step

One decode step for batch `b`:

```
FLOPs     ~ 2 * P * b
bytes     = 2*P*bytes_per_param   (weights, read once per step)
         + b * kv_bytes_per_token (cache, read once per step per sequence)
t_step = max( 2*P*b / FLOPS , (2*P*bytes + b*kv_bytes_per_token) / BW )
```

Worked example (7B, fp16, `kv_bytes_per_token = 2*32*8*128*2 = 131 KB`, 3 TB/s):

```
b=1:   compute 2*7e9/3e14        = 0.047 ms
       memory (14e9 + 1*131e3)/3e12 = 4.7 ms     -> MEMORY bound (100x)
b=64:  compute 2*7e9*64/3e14     = 3.0 ms
       memory (14e9 + 64*131e3)/3e12 = 4.7 ms     -> still memory bound
b=256: compute 2*7e9*256/3e14    = 11.9 ms
       memory (14e9 + 256*131e3)/3e12 = 4.8 ms    -> COMPUTE bound
```

**Crossover batch size**: memory ≈ compute when

```
2*P*b/FLOPS = 2*P*bytes/BW   =>   b = bytes * FLOPS / BW
```

With `bytes = 2`, `FLOPS/BW = 100`: `b* = 200`. So for a 7B model on a modern GPU,
batching below ~200 sequences leaves you memory bound — which is exactly why batching is
the dominant throughput lever.

## 3. Throughput

```
tokens_per_second = b / t_step
```

At the numbers above: `b=1` -> 214 tok/s; `b=64` -> 13,600 tok/s; `b=256` -> 21,500
tok/s. Throughput rises steeply with batch until the compute bound, then plateaus.

**Requests in flight needed for target throughput `T`**:

```
b_required = T * t_step
```

For `T = 10,000 tok/s` at `t_step = 5 ms`: `b = 50`. Which is the capacity-planning
number that matters.

## 4. Static Versus Dynamic Batching

Static batching with batch size `B` and request lengths `L_1..L_n` pads every batch to
the longest request in it:

```
efficiency_static = sum(L_i) / (n * max(L_i in each batch))
```

With lengths uniform in `[1, 100]` tokens, mean 50, and a batch of 64:

```
E[max of 64 uniform draws] ≈ 100 * 64/65 ≈ 98.5
efficiency ≈ 50 / 98.5 = 51%
```

Half the compute is wasted padding. Dynamic batching with slot-based recycling keeps
the batch full, so efficiency approaches 95%+.

**Latency comparison.** Static batching also imposes waiting: a request arriving one
step before a batch closes waits up to `t_step`. At `t_step = 5 ms` that is small, but
at large batch / memory bound steps (50 ms) it dominates TTFT.

## 5. KV Cache Memory

```
kv_bytes = 2 * L * H_kv * d_head * S * batch * bytes_per_elem
```

Worked example (7B: `L=32`, `H_kv=8` (GQA), `d_head=128`, `S=4096`, fp16):

```
kv_per_seq = 2*32*8*128*4096*2 = 268 MB
batch 16   = 4.3 GB
batch 64   = 17.2 GB
```

At fp32 it is 2x; with MHA (`H_kv = 32`) it is 4x. GQA is the single biggest cache
lever.

**Weights vs cache crossover**: cache exceeds weights when

```
2 * L * H_kv * d_head * S * batch * 2 > P * bytes
```

For 7B GQA, fp16, `S = 4096`: `batch > 14e9 / (2*32*8*128*4096*2) = 5.2`. So beyond 6
concurrent sequences the cache dominates memory. This is why long context hurts serving
more than weight size does.

## 6. Admission Control

Admission must consider peak memory, not average:

```
admit while sum_{i in batch} kv_bytes(S_i + max_new_i) <= capacity * safety_factor
```

Using current length instead of `prompt + max_new` under-reserves by a factor of
`(prompt + max_new) / prompt` (typically 1.3-3x) and causes OOM exactly when many
requests are long. The safety factor (0.8-0.9) covers fragmentation and estimation
error.

## 7. Queueing and Utilization

Little's Law: `L = lambda * W`. With arrival rate `lambda` and service rate `mu`:

```
rho = lambda / mu;   stability requires rho < 1
mean wait W = 1 / (mu - lambda)    (M/M/1)
```

At `rho = 0.9`, `W = 10/mu` — a 10x service time. This is why autoscaling on saturation
fails and scaling on **queue depth** (a leading indicator) is the right signal.

## 8. Replica Sizing

Given target throughput `T` tok/s per cluster, per-replica throughput `T_rep`, and
utilization headroom `h`:

```
replicas = ceil( T / (T_rep * h) )
```

With `T = 50,000`, `T_rep = 13,600`, `h = 0.7`: `ceil(50000/9520) = 6` replicas.
At `h = 0.9`: 5 replicas — but p99 latency is roughly 5x worse. Buy the headroom.

## 9. Cost Per Token

```
cost_per_token = gpu_hourly_cost / tokens_per_second
```

7B on an A100 at $2/hour, `b=64` (13,600 tok/s): `$0.000147/token` -> `$0.147 per 1M
tokens`. At `b=1` (214 tok/s): `$0.0093/token` -> `$9.35 per 1M`. **Batch size alone is
a 64x cost difference.** With int4 weights (`t_step` halves) the batch-64 case improves
further.

## 10. Prefix Cache Hit Rate

For a system prompt of `S` tokens in every request:

```
hit_rate = (requests whose prefix matches a cached prefix) / total requests
savings  = hit_rate * S / total_prompt_tokens
```

With `S = 1000`, `T = 500`: maximum 2% of tokens. Prefix caching matters most for large
system prompts / few-shot blocks, not short prompts. Report the hit rate so the
optimization effort is aimed correctly.

## 11. Streaming Benefit

Streaming does not change throughput or cost; it changes perceived latency:

```
TTFT_streaming = t_first_token (prefill + 1 decode step)
TTFT_buffered  = t_prefill + (n_out - 1) * t_step     (all generation before first byte)
```

For `n_out = 200`, `t_step = 20 ms`: buffered TTFT is 4 seconds; streaming TTFT is
~500 ms. That is the whole argument for streaming — and it means TTFT is the metric to
set the SLO on.

## 12. Retry Amplification

With per-request failure probability `p_f` and bounded retries `r` (no jitter,
synchronous):

```
expected_attempts = 1 + p_f + p_f^2 + ... + p_f^r
```

At `p_f = 0.2, r = 3`: `1.248`. At `p_f = 0.5, r = 3`: `1.875`. Retries also
re-consume capacity, so effective `p_f` rises under load — a positive feedback loop.
Bounded retries plus a circuit breaker (stop retrying a failing replica) is the standard
mitigation.

## Worked Numbers

7B model, A100 ($2/h), 3 TB/s, 300 TFLOP/s, GQA 8 KV heads, `d_head = 128`.

**Case A: batch 1**
```
t_step = max(0.047 ms, 4.7 ms) = 4.7 ms
throughput = 213 tok/s
cost/1M tokens = $9.40
TTFT (1000-token prompt) = prefill ~60 ms + 5 ms = 65 ms
```

**Case B: batch 64**
```
t_step = max(3.0 ms, 4.7 ms) = 4.7 ms
throughput = 13,617 tok/s
cost/1M = $0.147
```

**Case C: batch 64, int4 (3.5 GB weights)**
```
t_step = max(3.0 ms, 1.2 ms + cache) ≈ 1.6 ms   (compute bound)
throughput = 40,000 tok/s
cost/1M = $0.050
```

Combined: **188x cheaper than batch 1**, at unchanged quality (with int4 quantization
validated separately). Cache memory at 4096 context, batch 64: 17.2 GB fp16, 8.6 GB int8.
Fits an 80 GB A100 with weights and headroom.

Capacity for 50,000 tok/s at batch 64, int4: `50000/40000 / 0.7 = 2` replicas (2.4
rounded up). At batch 1, fp16: `50000/213/0.7 = 335` replicas. The architectural
decision, not the model, is what makes this affordable.

## Self-Check Questions

1. Compute the crossover batch size for a 13B model on a GPU with 1.8 TB/s and 300
   TFLOP/s, fp16.
2. Show static batching wastes ~50% compute for uniform lengths in `[1, 100]`, batch 64.
3. Compute KV bytes per sequence for a 70B model (80 layers, 8 KV heads, 128 dim) at
   8k context in fp16.
4. Derive the replicas needed for 30,000 tok/s at batch 32, fp16, `h = 0.6`.
5. Explain why scaling on GPU utilization under-provisions.