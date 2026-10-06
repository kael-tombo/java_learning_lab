# Lab 12: Cost Optimization for LLMs — Math Foundation

## 1. Cost Decomposition

```
cost_per_request = c_in * n_in + c_out * n_out + c_emb * n_emb + c_rr * n_rerank
```

With typical prices (`c_in = $3/M`, `c_out = $15/M`, `c_emb = $0.02/M`,
`c_rerank = $1/M`):

For a RAG request with 4,200 prompt tokens, 180 output tokens, 1 query embedding
(1,500 tokens), and 50 rerank inputs (200 tokens each = 10,000 tokens):

```
input    = 3 * 4200/1e6          = $0.0126
output   = 15 * 180/1e6          = $0.0027
embed    = 0.02 * 1500/1e6       = $0.00003
rerank   = 1 * 10000/1e6         = $0.0100
                                          -------
                                            $0.0253

share:  input 50%,  output 11%,  rerank 40%,  embed 0.1%
```

Two non-obvious conclusions: input dominates, but **reranking is a close second** —
and the intuitive "just make outputs shorter" lever moves 11%. This is exactly the
mistake the exercise set is designed to expose.

## 2. Prefix Caching Savings

Let the prompt be a stable prefix of `S` tokens and a volatile suffix of `V` tokens.
With a cache hit rate `h` and cached tokens priced at fraction `alpha` of full price:

```
cost_in = c_in * [ V + S*(alpha + (1-alpha)*h) ]
savings_fraction = c_in * S * (1-alpha) * h / cost_in_before
```

With `S = 3000`, `V = 1200`, `alpha = 0.1`, `h = 0.8`:

```
cost_in = 3/1e6 * [1200 + 3000*(0.1 + 0.9*0.8)] = 3/1e6 * [1200 + 2460] = $0.011
before  = 3/1e6 * 4200 = $0.0126
savings = 12.7%
```

Note: `h` is multiplicative with `S/(S+V)`. If the prefix is only 20% of the prompt
and the hit rate is 50%, savings are `0.2 * 0.5 * 0.9 = 9%`. **Prefix caching has a
ceiling set by the prefix fraction** — if your prompt is mostly per-request retrieved
context, there is not much to cache, which is why context reduction is the bigger
lever there.

## 3. Semantic Cache Expected Savings

With hit probability `h` and quality delta on hits `delta_q`:

```
E[cost] = (1-h)*c_full + h*c_lookup
savings = h * (1 - c_lookup/c_full) ~ h   (c_lookup is ~free)

E[quality] = (1-h)*q_miss + h*(q_miss + delta_q) = q_miss + h*delta_q
```

So the cost saving is roughly `h` and the quality cost is `h * delta_q`. Both scale
with `h`. A semantic cache is therefore a **quality dial**, not a free win: 40% hit
rate on paraphrased questions is 40% of your traffic answered without a fresh
generation. Quantify `delta_q` on the eval set before enabling it broadly.

## 4. Cascade Economics

Two models: cheap `C` at cost `c_c`, expensive `E` at cost `c_e = k * c_c`. Escalation
probability `p`:

```
blended_cost = (1-p)*c_c + p*c_e = c_c * (1 + p*(k-1))
```

For `k = 20` (a 20x price gap):

```
p = 0.1  ->  2.9x cheap cost
p = 0.2  ->  4.8x
p = 0.3  ->  6.7x
p = 0.5  ->  10.5x
```

Quality is the unknown: if quality only matches the expensive model at `p = 0.35`,
blended cost is `7.65x` cheaper for equal quality. If quality falls 2 points at
`p = 0.15`, you pay 3.85x cheaper for a 2-point drop — a trade to make deliberately.

Better than a fixed threshold: escalate on **outcome**, so `p` self-adjusts. With a
verifier in the loop, `p` is determined by how often the cheap model is actually
wrong rather than by how often a classifier is uncertain.

## 5. Batching Throughput

Decode per-token time:

```
t(b) = max( 2*P*b/FLOPS , (2*P + b*C)/BW )      P = params, C = cache bytes/seq
```

Cost per token (in GPU-seconds) is `t(b)/b`:

```
t(b)/b = max( 2*P/FLOPS , (2*P + b*C)/(b*BW) )
       = max( 2*P/FLOPS , (2*P/b + C)/BW )
```

As `b -> inf`, cost/token -> `max(2P/FLOPS, C/BW)`. The memory term falls as `2P/b`;
so:

```
b* for compute bound  ~  P*FLOPS/(C*BW)
b* for memory-bound   ~  P*BW / C          (where 2P/b ~ C)
```

With `P = 7e9`, `C = 1.07e9` (2048-token cache), `FLOPS = 1e15`, `BW = 3.3e12`:

```
2P/BW      = 14e9/3.3e12 = 4.24 ms
C/BW       = 0.324 ms
b* (memory) ~ (2P/BW - C/BW) * BW / C = (4.24-0.324)/0.324 = 12.1
```

So batch ~12 makes the memory term cache-dominated; beyond that the cache term grows
linearly while compute stays small. The real limit is **memory for cache**, not
compute:

```
max_batch_by_memory = (device_mem - weights - overhead) / C
                   = (80e9 - 14e9) / 1.07e9 = 61 sequences at 2048 ctx
```

Practical takeaway: capacity is a cache-memory problem. Reducing `C` (GQA, INT8
cache, shorter contexts) raises batch ceiling multiplicatively.

## 6. Speculative Decoding Expected Length

With acceptance probability `alpha_i` for draft token `i`:

```
E[accepted per pass] = 1 + alpha_1 + alpha_1*alpha_2 + ... + prod_{j<=k} alpha_j
```

If `alpha_i = alpha` constant:

```
E[accepted] = (1 - alpha^{k+1}) / (1 - alpha)
```

Speedup (target forward pass costs the same as one token):

```
speedup = E[accepted] / (draft_cost_ratio_adjusted)
```

With `alpha = 0.8`, `k = 5`: `E = (1 - 0.8^6)/0.2 = (1-0.262)/0.2 = 3.69`.
With `alpha = 0.6`, `k = 5`: `E = (1-0.0467)/0.4 = 2.38`.

Observed production speedups (1.5-3x) are lower than the raw `E[accepted]` because the
draft model costs real time and verification is not free:

```
net_speedup = E[accepted] / (1 + draft_k * c_ratio)
```

With `c_ratio = 0.1` (draft is 10% the cost) and `E = 3.69`: `3.69/1.1 = 3.35`.
With hardware overhead reducing effective acceptance: ~2-3x. Report the model, then
the measurement.

## 7. Breakeven Speculative Draft

Let `alpha` be acceptance, `c_d` the draft cost ratio, `c_v` verification overhead:

```
net > 1  <=>  E[accepted] > (1 + c_v) / (1 - c_d * ... )
```

Simplified breakeven: `E[accepted] * (1 - c_d) > 1` -> for `c_d = 0.1`,
`E[accepted] > 1.11`. Almost any reasonable draft clears this. The binding constraint
in practice is verification overhead and cache pressure from the second model, not
acceptance.

## 8. Quantization Cost Model

`cost_per_token ∝ 1/bytes_moved` while memory bound:

```
fp16: bytes = 2P            -> cost ~ 1
int8: bytes = P             -> cost ~ 1/2
int4: bytes = 0.5P          -> cost ~ 1/4
```

Batch ceiling also rises:

```
max_batch ∝ (mem - weights) / C      -> int4 frees 3.5P of memory
```

Combined effect at `b=32` for a 7B model: if fp16 max batch is 61 and int4 raises
available memory by `14e9 - 3.7e9 = 10.3e9 GB-equivalent`, then `max_batch = (80e9 -
3.7e9)/1.07e9 = 71`. Only a ~16% batch gain here — because at 2048 context the cache
dominates and the weights are a minority of memory. At short contexts (512) the
weight saving matters much more. Compute this per workload rather than assuming.

## 9. Rerank Trade-off

Rerank cost `~ k * c_rr * tokens_per_chunk`. Marginal quality gain per `k`:

```
d(quality)/dk -> 0 quickly; d(cost)/dk = constant
```

Knee selection: pick the smallest `k` where the quality curve's slope falls below a
threshold (e.g. 0.2 quality points per doubling of `k`). Empirically `k = 20-50` for
most corpora; the marginal chunk added past 100 contributes almost nothing while
latency is linear.

## 10. Output Length Tiers

Let `L_p` be the p-th percentile of natural output length. Truncation at `L`:

```
P(truncate) = 1 - p
E[quality(L)] decreasing in L below p95
```

Tiered caps (`p50`, `p90`, `p99`) let interactive traffic use short caps and
long-form requests request a long cap explicitly. Reported metric: quality per
output token, not just quality, because quality is not free.

## 11. Total Cost of Ownership

```
monthly = requests * cost_per_request
        + requests * (extra_retries * retry_rate) * cost_per_request
        + ingest_cost * freshness_multiplier
        + eval_cost (continuous evaluation sampling)
        + infra_fixed
```

Two lines people forget: **retries** (a 5% retry rate multiplies spend by 1.05, but a
naive retry-on-timeout policy can multiply by 2x under load) and **continuous
evaluation** (sampling 2% of traffic for scoring is a real line item). Track them.

## 12. Quality-Adjusted Cost

```
qac = quality_metric / cost_per_request
```

Comparing configurations on `qac` finds the efficient frontier. A configuration is
**dominated** if another is at least as good and cheaper. Always plot both axes; the
"best" configuration depends entirely on the exchange rate between quality points and
dollars, which is a product decision.

## Worked Numbers

Baseline (from section 1): `$0.0253/request`. 2M requests/month -> `$50,600/month`.

| Change | Effect | New cost | Monthly |
|--------|--------|----------|---------|
| baseline | — | $0.0253 | $50,600 |
| prefix cache (prefix 71%, hit 80%, alpha 0.1) | input -12.7% | $0.0237 | $47,400 |
| rerank k 50->25 | rerank -50% | $0.0187 | $37,400 |
| context reduction 4200->1200 input | input -70% | $0.0079 | $15,800 |
| cascade p=0.2, k=20 | output+input -~75% on most | $0.0053 | $10,600 |
| semantic cache h=0.35 | -35% of generation cost | $0.0035 | $7,000 |
| int8 weights | GPU cost -50% | $0.0033 | $6,600 |

Cumulative: **7.7x reduction**, and the three largest single contributions were
context reduction, cascade routing, and rerank reduction — not "use a smaller
model". Each step must be validated against the eval suite.

## Self-Check Questions

1. Recompute the cost breakdown if the model returns 600 output tokens.
2. Show that prefix caching savings are capped by the prefix fraction.
3. Derive `E[accepted]` for `alpha = 0.7`, `k = 4`.
4. Compute the max batch by memory for `P=7e9`, `C=0.5e9`, `mem=24e9`.
5. Explain why "shorten the output" moved only 11% in the worked example.