# Lab 12: Cost Optimization for LLMs — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Cost lines | input tokens, output tokens, embedding calls, rerank calls, GPU seconds |
| 2 | RAG's dominant cost | Retrieved input tokens |
| 3 | Chat's dominant cost | Output tokens |
| 4 | Ingestion's dominant cost | Embedding calls |
| 5 | Measure first | No optimization without a per-request breakdown |
| 6 | Attribution | Cost per feature, per tenant, per route |
| 7 | Prefix cache | Caches only a contiguous unchanged prefix |
| 8 | One changed token | Everything after it is a miss |
| 9 | Timestamp early in prompt | Guaranteed cache miss |
| 10 | Layout | stable system + few-shot, then volatile docs, then query |
| 11 | Cache TTL | Minutes to hours; intermittent traffic loses it |
| 12 | Max prefix length | Provider-specific cap |
| 13 | Semantic cache key | hash(normalize(embed(query)), model, prompt, corpus, tenant) |
| 14 | Normalize before embed | Otherwise near-duplicates miss |
| 15 | Similarity threshold | `cos >= tau`, not equality |
| 16 | Semantic cache invalidation | model, prompt, corpus, policy, authz scope |
| 17 | Cache poisoning | Adversarial or stale entries served to others |
| 18 | Tenant scoping | Required in the key, not just in the ACL |
| 19 | When to disable it | Low hit rate on high-entropy workloads |
| 20 | Routing | Send easy work to cheap models |
| 21 | Routing signals | Heuristics, classifier, or cascade |
| 22 | Cascade | Cheap first, escalate on low confidence/validation failure |
| 23 | Cascade > static router | Escalation is outcome-based |
| 24 | Escalation rate | The number that sets blended cost |
| 25 | Context reduction | Return fewer, better chunks — the big RAG lever |
| 26 | Compress context, not instructions | Instructions are small; context is huge |
| 27 | Never compress | Schema, final question, system message |
| 28 | History compaction | Keep last k turns, summarize older |
| 29 | Extractive summarization | Salient sentences; loses connective detail |
| 30 | Learned compression | Token dropping via trained autoencoder |
| 31 | Compression risk | Meaning shifts; measure quality |
| 32 | Static batching | Waits for a full batch; adds TTFT |
| 33 | Continuous batching | Fills slots on arrival |
| 34 | Batching lever | Amortizes weight reads; biggest throughput win |
| 35 | Batching changes numerics | Reduction order differs by batch size |
| 36 | Quality at served batch | Offline batch-1 numbers do not describe production |
| 37 | Speculative decode | Draft proposes k, target verifies all k in one pass |
| 38 | Acceptance rule | accept if `U < p_target/p_draft` |
| 39 | Lossless | Output distribution equals the target's |
| 40 | Speedup typical | 1.5-3x |
| 41 | Best conditions | Large memory-bound target, cheap matching draft |
| 42 | Cost | Draft KV cache + verification overhead |
| 43 | Tree variants | Better acceptance via a draft tree + mask |
| 44 | INT8 cost | ~2x cheaper per token at equal batch |
| 45 | INT4 cost | ~4x cheaper per token |
| 46 | Secondary win | Freed memory allows bigger batches |
| 47 | Output length | Directly billable; control via max_tokens and prompts |
| 48 | Truncation cliff | Below p95 output length, quality falls off |
| 49 | Quality per token | Length is a reward-hacking target (Lab 07) |
| 50 | Embedding dedupe | contentHash before embedding |
| 51 | Embedding cache | `(modelVersion, hash) -> vector` on disk |
| 52 | Idempotent ingest | Second run makes zero embedding calls |
| 53 | Embed only searchable | Do not embed corpora filtered at query time |
| 54 | Rerank cost | k forward passes per query |
| 55 | Rerank k sweep | Quality plateaus early; latency keeps rising |
| 56 | Rerank caching | Per `(queryHash, chunkId)` |
| 57 | Prefill chunking | Long prompts split into chunks interleaved with decode |
| 58 | Sliding window | Bounds cache memory for long outputs |
| 59 | INT8 KV cache | Halves cache bytes |
| 60 | Priority lanes | Interactive first; batch jobs drain when idle |
| 61 | Load shedding | 429 backpressure beats collapse |
| 62 | Utilization target | <= 0.6 for tail latency |
| 63 | Autotuning | Cache results; do not tune in production |
| 64 | Quality-per-cent | `quality / cost_per_request`; plot the frontier |
| 65 | Dominated config | Worse quality at higher cost |
| 66 | Cost per 1k tokens | The unit finance cares about |
| 67 | Token accounting | Provider-reported, not estimated |
| 68 | Streaming | Does not reduce token cost; improves perceived latency |
| 69 | Smaller model routing | 10-30x price gap between tiers |
| 70 | Optimization order | Measure, remove waste, prefix cache, batch/precision, route, cache, reduce context, speculate |

## Self-Check

55+ = solid, 45-54 = redo Exercises 4 and 8, below that reread THEORY 1-8.