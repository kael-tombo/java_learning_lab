# VISION — Distributed Cache Capstone

> Build a cache that survives node loss, cluster growth, and a hot key, while
  keeping the semantics honest about staleness.

## Why this capstone

Caching looks trivial and is where correctness quietly dies: stampedes,
inconsistent invalidation, a hash ring reshuffling under load, and a memory
budget nobody computed. This capstone is about the parts of caching that
require thought.

## The Arc

1. **Placement** — consistent hashing, replicas, and what happens on topology change.
2. **Eviction** — LRU/LFU/TinyLFU, admission, and the scan-resistance problem.
3. **Consistency** — TTL, invalidation, versioned keys, read-through vs write-through.
4. **Failure** — stampedes, hot keys, cluster partitions, cold starts.
5. **Operate** — hit rate, memory, eviction rate, and what each number means.

## Milestones (checkable)
- [ ] M1: implement consistent hashing with virtual nodes and show minimal remapping on resize.
- [ ] M2: implement TinyLFU-style admission and demonstrate scan resistance over pure LRU.
- [ ] M3: prevent a cache stampede with single-flight and measure the origin load drop.
- [ ] M4: shard a hot key 1000x and measure the improvement at a stated consistency cost.
- [ ] M5: build an eviction and memory dashboard, and explain every metric.

## Anti-Goals
- A cache with a TTL but no stampede protection.
- Invalidation by broadcast to all nodes (a hidden cluster-wide operation).
- Caching a value with no owner and no invalidation path.

## Interview Lens
- "Your hit rate dropped from 94% to 61%. What happened?"
- "How do you prevent a cache stampede on a popular key?"
- "How do you invalidate across 200 nodes?"

## 30-Day Plan
- Wk1 consistent hashing + ring visualization + resize test.
- Wk2 eviction policies with a scan-resistance benchmark. Wk3 stampede + hot key.
- Wk4 metrics dashboard and a written consistency contract.

## Done = You Can
- State, precisely, what your cache guarantees and what it does not.
