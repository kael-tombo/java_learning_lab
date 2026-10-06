# Caching - Vision

## Why This Lab Exists
A cache is a bet that a computation done now will be needed again soon. That
bet is almost always correct, and it is almost always managed badly: unbounded
keys, no invalidation story, a hit rate nobody watches, and a cold-start storm
the first time it matters. This lab exists to make the bet and its cost
explicit.

## The Mental Model
Caching moves cost forward in time and sideways in topology:

```
  User request -> L1 (in-process) -> L2 (Redis/cluster) -> L3 (CDN) -> Origin
```

Each layer is *faster and smaller in hit rate*. L1 is sub-microsecond but
per-pod and tiny. The CDN is a world of capacity but only helps for bytes that
vary by URL, not by viewer.

## The Four Questions
Every cache design answers these, and every cache bug lives in one of them:
1. **What is the key?** (granularity, tenancy, version prefix)
2. **What is the TTL?** (explicitness, jitter, negative caching)
3. **How is it invalidated?** (write-through, write-behind, or evict-on-read)
4. **What happens when it is cold?** (stampede protection, prewarming)

## What You Should Be Able To Do
- Pick L1/L2/CDN placement for a read path and justify each hop.
- Compute cache size from working-set size, not from available RAM.
- Explain stampede protection (request coalescing / early expiry) in code.
- State whether a stale read is *acceptable* for that field, and by how much.
- Diagnose a "cache hit rate is 95% and the service is still slow" situation.

## The Anti-Goals
- Caching is not a substitute for an index or a query fix.
- Never cache an object without a documented TTL and invalidation trigger.
- Do not cache what you cannot invalidate; cache the *derivation*, not the
  authority.

## Success Criteria
You can walk any read path and produce a cache spec: layers, keys, TTLs,
invalidation owners, cold-start behaviour, and an expected hit rate with the
arithmetic to back it.

## How To Use This Lab
1. `THEORY.md` for policy, placement, and eviction.
2. `MATH_FOUNDATION.md` for hit rate, hit cost, working sets, bloom filters.
3. `CODE_DEEP_DIVE.md` for LRU/LFU, local cache, request coalescing.
4. `MINI_PROJECT.md` to build a two-tier cache with stampede protection.
5. `REAL_WORLD_PROJECT.md` for a multi-layer read path at scale.
