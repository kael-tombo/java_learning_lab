# Lab 12: Cost Optimization for LLMs — Theory

## 1. Where the Money Goes

A serving bill decomposes into four lines, and they respond to completely different
levers:

```
cost = C_in * tokens_in
     + C_out * tokens_out
     + C_embed * embedding_calls
     + C_rerank * rerank_calls
     + C_gpu * gpu_seconds
```

Typical shapes: input tokens dominate **RAG** (retrieved context is the biggest
token block), output tokens dominate **chat**, embedding calls dominate
**ingestion**, and GPU-seconds dominate **everything at scale**. Optimizing the wrong
line is the most common waste: shrinking output tokens when 80% of spend is retrieved
context does nothing.

## 2. Prompt Caching

Most providers discount repeated **prefix** tokens and most engines cache by prefix
hash.

```
layout:  [stable system][stable few-shot][volatile: retrieved docs][user query]
         |<------- cacheable ------->|
```

- Only a **prefix** caches. Change one token at position 200 and everything after is
  a miss.
- Max prefix length per provider; measured hit rate is the metric.
- Cache TTL: minutes to hours. Intermittent traffic loses the cache.
- Levers: move volatile content to the tail, hoist static content, avoid
  per-request timestamps inside the prefix, reuse the same prompt ordering.

Expected win: if 70% of your prompt is a static system prompt reused across calls,
caching removes 70% of input cost on repeat traffic. This is usually the single
largest saving available and it is free.

## 3. Semantic / Response Caching

Beyond prefix caching, cache the **answer**.

```
semantic cache: key = hash(embed(normalize(query)), model, prompt_version, corpus_version)
```

- Normalize aggressively (case, punctuation, whitespace) before embedding — or
  near-duplicates become misses.
- Similarity threshold, not equality. Store `(embedding, response)` and look for
  `cos >= tau`.
- Invalidate on: model change, prompt change, corpus change (for RAG), policy change.
- Risks: personalized answers behind a shared cache key; stale answers after a
  policy update; adversarial cache poisoning. Mitigate with key scoping to
  (tenant, user, authz scope) and short TTLs.
- Measure the hit rate honestly: a low hit rate on high-entropy workloads is normal
  and the cache is pure overhead. Know when to turn it off.

## 4. Model Routing

Different requests need different capability. Route by difficulty:

```
easy   (FAQ, classification, extraction) -> small/cheap model
medium (summarization, standard QA)        -> mid model
hard   (multi-step reasoning, code)       -> frontier model
```

Routing signal options:
1. **Prompt heuristics**: length, presence of code blocks, keywords.
2. **Classifier**: a trained router on (prompt, retrieved difficulty features).
3. **Cascade**: run the cheap model; escalate when confidence is low, output is
   malformed, or verification fails. This is strictly better than a static router
   because escalation is *outcome-based*.

Cascades are the strongest design: you pay the frontier price only on the fraction
that needs it. The escalation rate is the metric that sets your cost.

## 5. Prompt Compression

Reduce tokens before they reach the model.

| Technique | Mechanism | Risk |
|-----------|-----------|------|
| Stop-word / filler removal | Drop low-content tokens | Changes meaning in negation |
| Whitespace/history trimming | Drop old turns, keep summaries | Loses detail older in context |
| Extractive summarization | Keep salient sentences | Loss of connective detail |
| Learned compression (autoencoders, token dropping) | Train a compressor | Needs training; opaque |
| Retrieval-side reduction | Fewer, shorter chunks | The best lever — see below |

Key insight: **compression of the retrieved context beats compression of the
instruction.** If you are paying 4,000 tokens of retrieved text per call, returning
400 well-chosen tokens is a 10x win with no quality loss. Instruction text is usually
100-300 tokens; do not bother compressing it.

Semantic caching of embeddings also matters: identical chunk text re-embedded on every
ingest run is pure waste.

## 6. Dynamic Batching

Batch size is the primary throughput lever (Lab 11 math): at batch 1 you are memory
bound and wasting FLOPS capacity. Dynamic (continuous) batching fills slots as
requests arrive rather than waiting for a batch to fill.

```
static batching:   [wait for batch to fill]  -> added latency, wasted slots
dynamic batching:  [fill as arrivals come]   -> lower TTFT at same throughput
cost model:  cost_per_token falls ~linearly with batch until compute bound
```

Trade-off: batching can change numerics slightly (different reduction orders). If
quality is measured offline at batch 1 and served at batch 32, your offline numbers
do not describe production. Measure quality at the served batch size.

## 7. Speculative Decoding

A small **draft** model proposes `k` tokens; the large **target** model verifies all
`k` in a single forward pass (because verification is parallel across positions).

```
step:
  draft model generates z_1..z_k sequentially (cheap)
  target model scores all k positions in ONE pass (same cost as 1 token)
  accept z_i if  U < p_target(z_i)/p_draft(z_i)
  on first rejection, resample from the adjusted distribution and discard the rest
  expected accepted tokens = 1 + sum_i p_ratio_i
```

Properties:
- **Lossless**: the output distribution is exactly the target's. No quality change.
- Speedup bounded by draft quality and hardware. Typically 1.5-3x.
- Works best when the target is memory bound (large model, small batch) and the
  draft is cheap.
- Good draft/target pairs: same family, adjacent sizes, or a specialized small model.
- Adds a KV cache for the draft model and a tree/mask structure for multi-candidate
  variants.

## 8. Batching for Prefill and Output Length Control

Output length is directly billable. Controls:
- `max_tokens` per request tier, justified by measured output length percentiles.
- Prompt the model to be concise when the task does not need length.
- Structured outputs that are inherently short (JSON schema).
- Stop sequences to cut trailing explanation.

Careful: over-constraining length degrades quality, and length is a known reward-hacking
target in preference tuning (Lab 07). Measure quality per output token.

## 9. Batching Strategy by Traffic Shape

| Traffic | Strategy |
|---------|----------|
| Steady high volume | Large static-ish batches, minimal prefill blocking |
| Spiky | Pre-warmed capacity; scale ahead of the curve |
| Long prompts | Chunked prefill; separate prefill lane |
| Long outputs | Sliding-window attention; INT8 KV cache |
| Many small requests | Semantic cache + routing to small models |
| Batch jobs | Low priority, drained in idle windows |

## 10. Quantization as Cost (Lab 11 Recap)

Cost per token is roughly inversely proportional to bytes moved:

```
int8 weights:  ~2x cheaper per token than fp16 at equal batch
int4 weights:  ~4x
```

Quantization also raises the feasible batch size (less weight memory, more left for
cache), which multiplies the effect. Order of operations: batch first (biggest
lever), then quantize, then route, then cache, then compress.

## 11. Embedding Cost

Ingestion-heavy systems spend heavily here:
- Deduplicate chunk text before embedding (`contentHash`).
- Cache `(modelVersion, hash) -> vector` on disk.
- Embed only what you will search: if a corpus section is filtered out at query time,
  do not embed it.
- Re-embed only on model change; batch API calls with concurrency limits.

## 12. Reranking Cost

Reranking is `k` forward passes per query — often the largest *latency* line. Options:
- Reduce `k` (measure the recall delta).
- Batch the reranker across candidates.
- Use a smaller reranker model.
- Two-stage: rerank top-20 instead of top-100.
- Cache rerank results per (query, chunk) — repeated questions are common in support.

## 13. The Optimization Sequence

An ordering that respects the size of the levers:

```
1. measure the cost breakdown per request (no optimization without this)
2. remove waste: dedupe, cache embeddings, drop unused calls
3. prompt layout for prefix caching          (free, often 30-50% of input cost)
4. batching and precision                    (3-10x on GPU cost)
5. routing / cascade                         (2-5x blended)
6. semantic response cache                   (large on repetitive traffic)
7. retrieval-side context reduction          (10x on input tokens in RAG)
8. speculative decoding                      (1.5-3x, lossless)
9. output length control                     (needs quality measurement)
```

Skip nothing; do them out of order and you will optimize the 3% line.

## 14. Quality Guardrails

Every optimization needs a gate, or you are just making it worse and cheaper:

```
cost_reduction_pct   vs   quality_delta   ->   only ship if delta is inside budget
```

Run the Lab 09 evaluation suite (correctness, faithfulness, abstention, safety) for
each optimization. Cache hit rate must be watched alongside: a cache that improves
cost by 40% and degrades answers by 3 points is a trade, and it is a *decision*,
not an engineering fact.

## Key Equations

```
cost_per_request = C_in*in_tok + C_out*out_tok + C_embed*n_embed + C_rerank*n_rerank
cost_per_token   = gpu_cost * gpu_seconds_per_token
speedup_batch    ~ min(b, FLOPS/(2*BW))          (until compute bound)
accept_rate      = 1 + sum_{i=1..k} p_ratio_i
cache_hit_rate   = cached_prefix_tokens / total_prefix_tokens
quality_per_cent = quality_metric / cost_per_request * 100
```