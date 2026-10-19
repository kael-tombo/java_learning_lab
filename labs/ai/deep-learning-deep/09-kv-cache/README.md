# 09-kv-cache - KV Cache
## Overview
Decoding caches per-layer K,V: bytes = 2 * layers * kv_heads * dim * bytes_per_elem * seq_len. Each new token then attends in O(T) instead of recomputing O(T^2) keys/values.
## Key formulas
- Per token: 2*L*H*D elements; x seq_len x bytes.
- Work per step drops from quadratic to linear in T (same weights, stated toy op model).
## What the snippets show
- Dl09A: 12288 elems/token, 25.17MB at T=1024 fp16.
- Dl09B: cached vs full op-count contrast at T=512.
## Try it
Halve heads (GQA) in Dl09A and confirm the MB halves.
## Formula reference
- Elements per token = 2 * L * kv_heads * dim; bytes x seq x bytes/elem.
- Prefill O(T^2) once; decode O(T) per token with cache.
- Eviction/quantization (keep recent + landmarks) bounds memory.
## Worked example
- 2*12*8*64 = 12288 elems; fp16 24576 bytes/token.
- x1024 = 25,165,824 bytes = 25.17 MB (1e6 MB convention as printed).
- Toy ops T=512: cached 6.29M vs 25.17M: ratio exactly 4x = T/128? stated toy model.
## Pitfalls
- Cache invalidation on any prefix edit; prefix-caching needs care.
- GQA/MQA change kv_heads: recompute, do not reuse MHA numbers.
- fp8/int KV quantization shifts attention mass; calibrate.
## Connections
- GQA halves/quarters this (attention-variants lab).
- Inference lab: batching amortizes these bytes across requests.
## Exercises
1. Halve heads; confirm MB halves.
2. Compute cache for T = 4096 fp16.
3. Compare fp8 vs fp16 byte totals.
